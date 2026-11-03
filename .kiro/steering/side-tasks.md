---
inclusion: always
---

# Delegate side tasks to the sidekick subagent

Keep your own context for reasoning, design and the final answer. Hand these to the `sidekick` subagent instead of doing them yourself:

- mapping code the IDE index cannot answer (non-code files, unsupported language), listing files, reading many files. For "where is X / what calls Y" use `ide-reader` first (see ide-index.md)
- running tests, builds or linters and summarising the output; reading long logs or docs
- mechanical or repetitive edits, renames, boilerplate, small fixes with a clear spec
- drafting docs, comments or commit messages

Keep these yourself: architecture and design decisions, ambiguous requirements, security-sensitive changes, reviewing the sidekick's diff, and anything that needs the whole conversation.

How to delegate:
1. Give a self-contained task: goal, file paths if known, the expected result, constraints. The sidekick cannot see this chat.
2. Ask for a short report (files changed, check result, open questions), not file contents.
3. Delegate independent side tasks together so they run in parallel.
4. Treat the report as a claim: check the cited lines or the diff before relying on it, and rerun the check if the result matters.
5. Do not delegate a task smaller than the cost of explaining it (one-line edit, one known file).