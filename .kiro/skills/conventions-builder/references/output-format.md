# Output format of the generated conventions skill

## Evidence thresholds
| Share of the code following it | Label | How to write it |
|--------------------------------|-------|-----------------|
| >= 90% | **Rule** | imperative sentence: "Use snake_case for functions" |
| 70-90% | **Prevailing** | "Mostly X (78%); follow X in new code" |
| < 70% | **Mixed** | list the alternatives and counts, say "no single convention, match the surrounding file" |
| from a config file | **Configured** | name the file and key, e.g. "ruff `line-length = 88` (pyproject.toml)" |

Always add the count (`n/total`) and 1-3 examples as `path:line`. Skip an area entirely when there is no evidence for it.

## Folder layout
```
.kiro/skills/<name>/
  SKILL.md                # summary only, under ~80 lines
  references/
    naming.md             # per area, only where there is evidence
    formatting.md
    imports.md
    testing.md
    errors-and-docs.md
    structure.md
    CHANGELOG.md          # append-only, one line per update
```

## Generated SKILL.md template
```markdown
---
name: <name>
description: Code conventions for this repository (naming, formatting, imports, tests, docs). Use when writing, editing or reviewing code in this repo, or when asked about its style.
metadata:
  generated-by: conventions-builder
  generated-commit: <full sha>
---

# <Project> code conventions

Derived from the code on <date> at commit <short sha>. Evidence in `references/`.

## Summary
| Area | Convention | Level | Detail |
|------|------------|-------|--------|
| Functions | snake_case | Rule (98.7%, 4210/4265) | references/naming.md |
| Quotes | double | Rule (99.6%) | references/formatting.md |
| Line length | 88 | Configured (.flake8) | references/formatting.md |
| ... | ... | ... | ... |

## When writing code
- 3-8 bullets: the rules that matter most, imperative, each with its level.

<!-- manual:start -->
Your own rules go here. They are never overwritten.
<!-- manual:end -->
```

## references/<area>.md template
```markdown
# <Area>
Source: scan at <short sha> (<n> files).

## <Rule title> - <level>
<one sentence>. <n>/<total> (<pct>%).
Examples: `path:line`, `path:line`
Exceptions: <where it differs, with counts>
```
