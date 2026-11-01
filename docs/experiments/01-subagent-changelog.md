# Experiment 01 - invoke a Kiro subagent and have it log its changes

Smallest possible test. No MCP, no Haiku, no repo map. Answers: does a custom
subagent run, does it write the changelog, what does it cost.

## Setup
1. Open this folder in Kiro (IDE or CLI). Confirm `.kiro/agents/scribe.md` is detected.
2. Note the model picker value (record it below).

## Run (3 prompts, fresh chat each time; write down credits shown in the chat panel)
| # | Prompt | Purpose |
|---|--------|---------|
| A | "Add a line `hello A` to docs/experiments/sandbox.txt" | baseline: main agent does it itself |
| B | "Use the scribe subagent to add a line `hello B` to docs/experiments/sandbox.txt" | subagent invoke + changelog |
| C | "Use the built-in general-task-execution subagent to add `hello C` to docs/experiments/sandbox.txt, then append a line to .kiro/context/changelog.md" | built-in subagent, no custom agent |

## Record
| # | Credits | Context % | Subagent actually spawned? | Model shown | Changelog line written? | Notes |
|---|---------|-----------|----------------------------|-------------|--------------------------|-------|
| A |  |  | n/a |  | n/a |  |
| B |  |  |  |  |  |  |
| C |  |  |  |  |  |  |

## Questions this answers (brief section 4)
- Does Kiro auto-pick `scribe` from its `description`, or must the prompt name it?
- Does a subagent show its own model / credits, or only the main chat's?
- Does the subagent need a trust prompt to write files?
- Is subagent overhead on a trivial task higher than doing it directly (A vs B)?

## Next, only if B works
Add `model:` to `scribe.md` (try Haiku), rerun B, compare credits.
