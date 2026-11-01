# Experiment 06 - real cost per arm from account usage deltas

Date: 2026-11-01. Script: `scripts/run-usage-delta.ps1` (data: `docs/experiments/runs/usage-delta.csv`, `U_*`). For each arm: read `kiro-cli chat "/usage"` (credits used on the Free plan, 2-decimal resolution), run 3 questions (1 run each, same questions/ground truth/scoring as exp. 04-05), read `/usage` again after 8 s. Sanity check: two consecutive `/usage` reads were identical (12.29), so the command itself costs nothing.

## Results (3 runs per arm)
| Arm | Account delta (3 runs) | Real credits/run | Stream-reported (3 runs) | Avg line hits (of 3) |
|-----|------------------------|------------------|--------------------------|----------------------|
| Sonnet alone (`baseline`) | 1.68 | 0.560 | 1.673 | 2.33 |
| `reader` v3 alone (Haiku) | 0.25 | 0.083 | 0.256 | 2.00 |
| Delegation (Sonnet main -> `reader`) | 1.01 | 0.337 | **0.342** | 2.00 |
| Pipeline (reader, then Sonnet verifies) | 0.96 | 0.320 | 0.960 | 2.33 |

## Findings
1. **Confirmed: the run stream undercounts subagent usage.** For the three top-level arms the stream matches the account within 0.01. For delegation the stream says 0.342 but the account moved 1.01 (~3x). Do not use `meteringUsage` for delegated runs; use account deltas.
2. Real costs per run: reader alone 0.08 < pipeline 0.32 ~ delegation 0.34 < Sonnet alone 0.56.
3. Versus Sonnet alone: reader alone is 6.7x cheaper, pipeline 1.75x, delegation 1.66x. Experiment 05's "4.7x cheaper" for delegation was wrong; the real saving is ~40%.
4. Delegation (0.34) is not cheaper than the explicit pipeline (0.32) and not more accurate here; its main benefit is that the main agent decides to delegate by itself.
5. Accuracy this batch: baseline and pipeline 2.33, reader and delegation 2.00. With 3 runs per arm and 3 questions these differences are within noise (experiment 04 had pipeline 1.89, reader v3 1.78).

## Caveats
n=3 per arm, one repo (Python), 3 questions; `/usage` has 0.01 resolution (relative error ~1-4% on these deltas); no other Kiro activity was assumed in between (the machine may have other sessions). Delegator has only the `subagent` tool, a restricted setup.

## Implications
- The cheapest option measured is the small agent alone (0.08/run), at about 85% of the accuracy of Sonnet alone (earlier batches 1.78 vs 2.33, this one 2.0 vs 2.33). Putting a large model in front of it (delegation, pipeline) costs 4x more for no clear accuracy gain in these data.
- A large main agent adds value only when its reasoning is needed after exploration; for pure "where is X" questions, routing straight to the small reader is the better trade.

## Next
1. Task where the large model's reasoning matters (e.g. plan a change using the reader's findings) and compare end-to-end cost/quality.
2. More repetitions on the two cheap arms (reader alone vs pipeline) to tell the accuracy gap from noise: ~0.25 and ~1 credit per 3 runs.
3. A second repo and other language; harder multi-hop questions.
4. Check delegator with read tools, and Haiku 5.5 when available.
