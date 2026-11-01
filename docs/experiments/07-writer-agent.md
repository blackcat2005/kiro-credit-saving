# Experiment 07 - `writer` agent: explore, then persist findings to files

Date: 2026-11-01. Agent: `.kiro/agents/writer.json` (Kiro CLI 2.x JSON; copy also in `sandbox-repos/django/.kiro/agents/`). Merges the explorer (`reader`) with the change log idea (`scribe`).

## Design
- Model `claude-haiku-4.5`; tools `fs_read, fs_write, grep, glob, code`.
- Prompt: explore, then (1) write a note to `.kiro/context/notes/<slug>.md` (Question / Files with def lines / Summary / Unsure), (2) append one line to `.kiro/context/changelog.md`, (3) reply with the note path and a 3-line summary. If a note on the topic already exists, read it first instead of re-exploring.
- Write restriction: `toolsSettings.fs_write.allowedPaths = [".kiro/context/**"]`, and `fs_write` is deliberately NOT in `allowedTools`.

## What I learned about restricting writes (Kiro CLI 2.35.1, non-interactive)
| Config | Result |
|--------|--------|
| `fs_write` in `allowedTools` (+ `allowedPaths`) | **No restriction**: the agent edited `README.rst` (I reverted it). |
| `--trust-tools` including `fs_write` | Same, everything auto-approved. |
| `fs_write` NOT in `allowedTools`, `allowedPaths=[".kiro/context/**"]`, not trusted | **Works**: write to `README.rst` blocked ("requires explicit approval"), writes under `.kiro/context/` went through without a prompt. Source tree unchanged (`git status` clean apart from `.kiro/`). |

So `allowedPaths` means "auto-approved paths", not "only these paths"; the restriction comes from leaving `fs_write` un-approved elsewhere. In interactive use the out-of-path write would prompt instead of being blocked; in headless runs it fails.

## Probes (1 run each, not an experiment on cost/accuracy)
- Q2 (`filter()` delegation): 0.201 credits, 10 tool calls; created `notes/queryset-filter-delegation.md` and `changelog.md`. Note contained a delegation chain, but two cited lines were off by 1-2 (1738/1748 vs real 1739/1750).
- Middleware question: 0.131 credits, 5 tool calls; note + changelog line written (note may be lighter on line numbers).
- Negative test: out-of-scope write blocked (see table).

## Caveats
Writing costs extra (0.13-0.20 vs ~0.08 for read-only `reader`). Note accuracy is Haiku-grade. Whether re-use of notes lowers the cost of a repeat question is still untested.

## Next
1. Ask the same question twice with `writer` and compare cost of the second run (does the saved note get used?).
2. Check stale-note handling after editing a file in the sandbox repo.
3. Use `writer` as a subagent of `delegator` (add to `availableAgents`) and measure real cost with `/usage` deltas.
4. IDE: `.kiro/agents/scribe.md` remains for the IDE's Markdown agent format (not loaded by CLI 2.x).
