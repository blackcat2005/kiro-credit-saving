---
name: conventions-builder
description: Builds or updates a repo's code conventions as a Kiro skill folder with a name the user chooses. Use when the user asks to create, generate, refresh or update code conventions / coding style / style guide for this repository. Derives rules from the existing code with evidence, not guesses.
---

# conventions-builder

Generates (and later updates) a **skill folder** that records how code is written in this repo. The generated skill is loaded on demand by Kiro (progressive disclosure), so it costs no context until a coding task matches its description.

## Inputs (ask the user if missing)
1. **Name** of the output folder: lowercase letters, digits, hyphens, max 64 chars, e.g. `acme-conventions`. Output goes to `.kiro/skills/<name>/`. The `name` in its SKILL.md frontmatter must equal the folder name.
2. **Mode**: `init` if `.kiro/skills/<name>/` does not exist, `update` if it does (decide automatically, tell the user which).
3. Optional **scope**: sub-paths to analyse (default: whole repo, except vendored/generated dirs).

## Workflow: init
1. Run the scanner (deterministic, no LLM tokens): `python <this skill>/scripts/scan.py --root . [--paths ...]`. Use `python -I`. Read only its JSON output; do not open source files unless a rule needs a quick check.
2. Read the files listed in `config_files` (editorconfig, linters, formatters, tsconfig, CONTRIBUTING.md). **Official config beats statistics.** Cite the config as the source.
3. Turn statistics into rules using the thresholds in `references/output-format.md` (rule >= 90%, prevailing 70-90%, mixed < 70% = do not enforce). Never state a rule without counts and 1-3 `file:line` examples.
4. Write the output skill following `references/output-format.md`: a short `SKILL.md` (summary table, under ~80 lines) plus `references/<area>.md` for detail (naming, formatting, imports, testing, errors, project structure) only for areas with real evidence.
5. Stamp the generated SKILL.md frontmatter with `metadata: generated-commit: <head>` and `generated-by: conventions-builder`.
6. Report to the user: folder created, rules found per area, areas skipped for lack of evidence, anything contradictory.

## Workflow: update
1. Read `.kiro/skills/<name>/SKILL.md`; take `generated-commit` from its metadata. If missing or not in git history, treat as init but keep manual blocks.
2. Run `scan.py --since <generated-commit>` to get stats for changed files only, and a full `scan.py` run if the user asked for a full refresh. Compare new numbers with the recorded ones (`references/*.md` hold counts).
3. **Propose, do not overwrite.** Show the user a list of rule changes (new rule, strengthened, weakened, now mixed, removed because the code no longer exists) with evidence. Apply only what the user accepts.
4. Preserve everything between `<!-- manual:start -->` and `<!-- manual:end -->` verbatim; those are the user's own rules.
5. Update the counts, examples and `generated-commit`. Keep a one-line entry per change in `references/CHANGELOG.md` (append only).

## Rules for this skill
- Evidence first: a convention is what the code does, backed by numbers; opinions go only in manual blocks.
- Keep output small: the generated SKILL.md is read on every matching task. Put detail in `references/` and link it.
- Do not edit source code. Write only under `.kiro/skills/<name>/`.
- Prefer delegating bulk reading to a cheap read-only subagent if one exists; do the rule-writing yourself.
- If the scanner does not cover a language in the repo (it has statistics for Python and JS/TS, generic formatting for others), say so and rely on config files and a small sample of files for that language.
