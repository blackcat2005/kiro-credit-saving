#!/usr/bin/env python3
"""Collect evidence about a repo's code conventions. Deterministic, stdlib only, no LLM.

Usage:
  python scan.py --root . [--paths src tests] [--since <commit>] [--max-files 4000]

Prints one JSON document: config files found, formatting stats, naming stats, import
style, test layout, docstring/type-hint ratios. Every stat carries counts and a few
`file:line` examples so rules can be backed by evidence. `--since` limits the scan to
files changed since that commit (used for incremental updates).
"""
import argparse, ast, json, os, re, subprocess, sys
from collections import Counter, defaultdict

SKIP_DIRS = {".git", "node_modules", "dist", "build", "out", "target", "__pycache__", ".venv", "venv",
             ".next", "coverage", ".tox", ".mypy_cache", ".kiro", ".claude", "sandbox-repos", "vendor", "migrations"}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".go", ".rs", ".java", ".kt", ".rb", ".php", ".cs"}
CONFIG_NAMES = [".editorconfig", "pyproject.toml", "setup.cfg", "tox.ini", ".flake8", "ruff.toml", ".ruff.toml",
                ".pylintrc", "mypy.ini", ".pre-commit-config.yaml", "package.json", ".eslintrc", ".eslintrc.js",
                ".eslintrc.json", ".eslintrc.cjs", "eslint.config.js", "eslint.config.mjs", ".prettierrc",
                ".prettierrc.json", "prettier.config.js", "tsconfig.json", "biome.json", ".golangci.yml",
                "rustfmt.toml", "clippy.toml", "checkstyle.xml", ".rubocop.yml", "CONTRIBUTING.md", "CLAUDE.md"]


def case_of(name):
    n = name.strip("_")
    if not n:
        return "other"
    if n.isupper():
        return "UPPER_SNAKE" if "_" in n or len(n) > 1 else "other"
    if re.fullmatch(r"[a-z][a-z0-9]*(_[a-z0-9]+)*", n):
        return "snake_case"
    if re.fullmatch(r"[a-z][a-z0-9]*([A-Z][a-z0-9]*)+", n):
        return "camelCase"
    if re.fullmatch(r"[A-Z][a-z0-9]+([A-Z][a-z0-9]*)*", n):
        return "PascalCase"
    if re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)+", n):
        return "kebab-case"
    return "other"


class Stat:
    """Counter with up to 3 examples per bucket."""
    def __init__(self):
        self.c, self.ex = Counter(), defaultdict(list)

    def add(self, key, where=None):
        self.c[key] += 1
        if where and len(self.ex[key]) < 3:
            self.ex[key].append(where)

    def out(self):
        total = sum(self.c.values())
        return {"total": total, "buckets": {k: {"n": v, "pct": round(100 * v / total, 1), "examples": self.ex[k]}
                                            for k, v in self.c.most_common(6)}} if total else {"total": 0}


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout
    except Exception:
        return ""


def list_files(root, paths, since):
    if since:
        names = set(git(root, "diff", "--name-only", since, "HEAD").split()) | \
                set(git(root, "ls-files", "--others", "--exclude-standard").split())
        files = [n for n in names if os.path.isfile(os.path.join(root, n))]
    else:
        files = git(root, "ls-files", "-co", "--exclude-standard").split("\n")
        files = [f for f in files if f]
        if not files:
            files = []
            for d, dirs, fs in os.walk(root):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
                files += [os.path.relpath(os.path.join(d, f), root) for f in fs]
    files = [f.replace("\\", "/") for f in files]
    files = [f for f in files if not any(p in SKIP_DIRS for p in f.split("/")[:-1])]
    if paths:
        files = [f for f in files if any(f == p or f.startswith(p.rstrip("/") + "/") for p in paths)]
    return sorted(files)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--paths", nargs="*", default=[])
    ap.add_argument("--since", default="")
    ap.add_argument("--max-files", type=int, default=4000)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    all_files = list_files(root, a.paths, a.since)
    code = [f for f in all_files if os.path.splitext(f)[1] in CODE_EXT][: a.max_files]

    langs = Counter(os.path.splitext(f)[1] for f in code)
    configs = [f for f in git(root, "ls-files").split() if os.path.basename(f) in CONFIG_NAMES and f.count("/") <= 2] \
        or [n for n in CONFIG_NAMES if os.path.exists(os.path.join(root, n))]

    indent, quotes, eol, final_nl, tabs = Stat(), Stat(), Stat(), Stat(), Stat()
    lens, long_counts = [], Counter()
    file_names, test_layout = Stat(), Stat()
    py_func, py_class, py_const, py_private = Stat(), Stat(), Stat(), Stat()
    py_doc, py_hints, py_imports, py_rel, py_future, py_all = Stat(), Stat(), Stat(), Stat(), Stat(), Stat()
    js_func, js_class, js_import, js_export, js_semi = Stat(), Stat(), Stat(), Stat(), Stat()
    exceptions = Stat()

    for f in code:
        path = os.path.join(root, f)
        try:
            raw = open(path, "rb").read()
            text = raw.decode("utf-8")
        except Exception:
            continue
        ext = os.path.splitext(f)[1]
        stem = os.path.splitext(os.path.basename(f))[0]
        file_names.add(case_of(stem.replace(".test", "").replace(".spec", "")), f)
        base = os.path.basename(f)
        if re.match(r"test_.*\.py$", base) or re.search(r"_test\.(py|go)$", base) or re.search(r"\.(test|spec)\.[jt]sx?$", base):
            kind = "test_prefix" if base.startswith("test_") else "test_suffix"
            loc = "tests_dir" if re.search(r"(^|/)(tests?|__tests__)/", f) else "colocated"
            test_layout.add(f"{kind}+{loc}", f)
        eol.add("crlf" if b"\r\n" in raw else "lf", f)
        final_nl.add("final_newline" if raw.endswith(b"\n") else "no_final_newline", f)
        lines = text.split("\n")
        for i, line in enumerate(lines, 1):
            if not line.strip():
                continue
            lens.append(len(line))
            for lim in (79, 88, 100, 120):
                if len(line) > lim:
                    long_counts[lim] += 1
            m = re.match(r"^(\s+)\S", line)
            if m:
                ws = m.group(1)
                if "\t" in ws:
                    tabs.add("tabs", f"{f}:{i}")
                else:
                    tabs.add("spaces", f"{f}:{i}")
                    if len(ws) % 2 == 0 or len(ws) % 4 == 0:
                        pass
        # indentation width: first indented line after a block opener
        for i, line in enumerate(lines[:-1]):
            if re.search(r"[:{(\[]\s*$", line) and lines[i + 1].startswith(" ") and lines[i + 1].strip():
                w = len(lines[i + 1]) - len(lines[i + 1].lstrip(" ")) - (len(line) - len(line.lstrip(" ")))
                if w in (2, 4, 8):
                    indent.add(f"{w}_spaces", f"{f}:{i + 2}")
                break
        if ext in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
            s, d = len(re.findall(r"(?<![\w\"`\\])'[^'\n]*'", text)), len(re.findall(r"(?<![\w'`\\])\"[^\"\n]*\"", text))
            if s or d:
                quotes.add("single" if s >= d else "double", f)
            js_semi.add("semicolons" if len(re.findall(r";\s*$", text, re.M)) > len(lines) * 0.2 else "no_semicolons", f)
            for i, line in enumerate(lines, 1):
                m = re.match(r"\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)", line)
                if m:
                    js_func.add(case_of(m.group(1)), f"{f}:{i}")
                m = re.match(r"\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_$][\w$]*)", line)
                if m:
                    js_class.add(case_of(m.group(1)), f"{f}:{i}")
                if re.match(r"\s*import\s", line):
                    js_import.add("esm_import", f"{f}:{i}")
                elif re.search(r"\brequire\(", line):
                    js_import.add("require", f"{f}:{i}")
                if re.match(r"\s*export\s+default\b", line):
                    js_export.add("default_export", f"{f}:{i}")
                elif re.match(r"\s*export\s+(const|function|class|type|interface|enum)\b", line):
                    js_export.add("named_export", f"{f}:{i}")
        elif ext == ".py":
            s, d = len(re.findall(r"(?<![\w\"\\])'[^'\n]*'", text)), len(re.findall(r"(?<![\w'\\])\"[^\"\n]*\"", text))
            if s or d:
                quotes.add("single" if s >= d else "double", f)
            try:
                tree = ast.parse(text)
            except Exception:
                continue
            for node in ast.walk(tree):
                where = f"{f}:{getattr(node, 'lineno', 0)}"
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    py_func.add(case_of(node.name), where)
                    if node.name.startswith("_") and not node.name.startswith("__"):
                        py_private.add("single_underscore_private", where)
                    if not node.name.startswith("_"):
                        py_doc.add("has_docstring" if ast.get_docstring(node) else "no_docstring", where)
                    ann = bool(node.returns) or any(x.annotation for x in node.args.args)
                    py_hints.add("annotated" if ann else "unannotated", where)
                elif isinstance(node, ast.ClassDef):
                    py_class.add(case_of(node.name), where)
                elif isinstance(node, ast.ExceptHandler):
                    exceptions.add("bare_except" if node.type is None else "typed_except", where)
            for node in tree.body:
                where = f"{f}:{getattr(node, 'lineno', 0)}"
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            py_const.add(case_of(t.id), where)
                elif isinstance(node, ast.Import):
                    py_imports.add("import x", where)
                elif isinstance(node, ast.ImportFrom):
                    py_imports.add("from x import y", where)
                    if node.module == "__future__":
                        py_future.add("uses __future__", where)
                    py_rel.add("relative" if node.level else "absolute", where)
            py_all.add("defines __all__" if "__all__" in text else "no __all__", f)

    lens.sort()
    pct = lambda p: lens[min(len(lens) - 1, int(len(lens) * p))] if lens else 0
    out = {
        "head": git(root, "rev-parse", "HEAD").strip(),
        "root": root, "since": a.since or None, "files_scanned": len(code), "languages": dict(langs.most_common(8)),
        "config_files": configs[:40],
        "formatting": {"line_length": {"p50": pct(.5), "p95": pct(.95), "p99": pct(.99), "max": lens[-1] if lens else 0,
                                       "lines_over": dict(long_counts), "total_lines": len(lens)},
                       "indent_width": indent.out(), "indent_chars": tabs.out(), "quotes_approx": quotes.out(),
                       "line_endings": eol.out(), "final_newline": final_nl.out(), "js_semicolons": js_semi.out()},
        "naming": {"file_names": file_names.out(), "python_functions": py_func.out(), "python_classes": py_class.out(),
                   "python_module_constants_and_vars": py_const.out(), "python_private": py_private.out(),
                   "js_functions": js_func.out(), "js_classes": js_class.out()},
        "imports": {"python_top_level": py_imports.out(), "python_relative_vs_absolute": py_rel.out(),
                    "python_future": py_future.out(), "python_all": py_all.out(), "js_style": js_import.out(),
                    "js_exports": js_export.out()},
        "structure": {"tests": test_layout.out()},
        "quality": {"python_public_function_docstrings": py_doc.out(), "python_type_hints": py_hints.out(),
                    "python_except_style": exceptions.out()},
        "notes": ["quotes_approx is regex-based and approximate", "migrations/ and vendored dirs are skipped",
                  "official config files (listed in config_files) override these statistics"],
    }
    json.dump(out, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
