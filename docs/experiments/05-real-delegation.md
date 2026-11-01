# Experiment 05 - real delegation (Sonnet main agent -> Haiku `reader` subagent)

Date: 2026-11-01. Kiro CLI 2.35.1. Same questions, ground truth and pre-set +-2-line scoring as experiment 04. Driver: `scripts/run-delegate.ps1` (data: `docs/experiments/runs/delegate.csv`, `D_*`).

## Setup
`delegator` (`.kiro/agents/delegator.json`): `claude-sonnet-4.5`, only the `subagent` tool, `toolsSettings.subagent.availableAgents/trustedAgents = ["reader"]`, so it cannot explore itself and must delegate. `reader` is v3 (Haiku 4.5, read tools). Logs confirm the spawn: tool "Spawning agent crew" (this is the `subagent` tool's display name) with `role: "reader"` in 9/9 runs. This resolves the ambiguity of arm C in experiment 02.

## Results (9 runs)
| Arm | Credits as reported by the run stream | Avg line hits (of 3) |
|-----|---------------------------------------|----------------------|
| Sonnet alone (exp. 03, rescored) | 4.765 | 2.33 |
| Pipeline: reader then Sonnet verifies (exp. 04) | 2.689 | 1.89 |
| reader v3 alone (exp. 04) | 0.752 | 1.78 |
| **Delegation (this experiment)** | **1.011** (median 0.106) | **2.33** (Q1 1,2,3; Q2 3,3,3; Q3 2,2,2) |

File path correct 9/9. Time 28-49 s per run.

## IMPORTANT caveat: reported credits probably undercount the subagent
Account usage (`kiro-cli chat "/usage"`, Free plan, 50 credits) before/after:
- After exp. 04: 9.32 used. Exp. 04 stream total was 2.689 and the account moved by exactly that (6.63 -> 9.32), so for top-level runs the stream matches the account.
- After exp. 05 (plus one probe run): 12.29 used, a rise of **2.97**, versus 1.011 + 0.108 = 1.12 reported by the streams.
So roughly 1.85 credits (about 60%) of the delegated work did not show up in the stream, most plausibly the subagent's own usage. Real cost per delegated run is then about 0.30, not 0.11. That is about the same as the pipeline (0.30) and ~44% below Sonnet alone (0.53). This is inferred from two account readings, not measured per run; other account usage in between cannot be fully excluded.

> Update: confirmed in experiment 06 (`06-usage-delta.md`). Stream credits undercount delegated runs ~3x; real cost is ~0.34 credits/run, not 0.11. The "4.7x cheaper" below is wrong; the real saving vs Sonnet alone is ~1.7x.

## Findings
1. Delegation works as designed: the main agent hands the question to `reader`, which does the searching, and the main agent relays its findings.
2. Accuracy matched Sonnet alone (2.33 vs 2.33) and was above reader v3 run directly (1.78); with n=9 and one repo the second difference may be noise, since the delegator mostly relays reader's text.
3. Cost advantage depends on the undercount: reported 4.7x cheaper than Sonnet alone; account-based estimate only ~1.8x cheaper. Per-run metering from `meteringUsage` cannot be trusted for delegated runs.

## Next
1. Measure delegation cost properly: read `/usage` before and after a fixed batch (and the same for the other arms), use account deltas as the credit measure.
2. Try a delegator that also has read tools, to see whether it delegates only when worthwhile and what that does to cost.
3. Harder/other-language questions and a second repo before drawing conclusions.
