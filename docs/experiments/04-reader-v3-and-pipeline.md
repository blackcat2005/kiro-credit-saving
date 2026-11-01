# Experiment 04 - reader v3 and the two-step pipeline

Date: 2026-11-01. Same repo, questions, ground truth and +-2-line scoring as experiment 03. Driver: `scripts/run-pipeline.ps1` (data: `docs/experiments/runs/pipeline.csv`, `P_*.final.txt`). n = 9 runs (3 questions x 3 reps). Scoring rule was fixed before running.

## What changed
- **Step 1, reader v3** (`.kiro/agents/reader.json`): prompt requires locating the main def, then listing and locating everything it calls/delegates to, citing the def/class line, max 20 lines.
- **Step 2, pipeline**: `reader` (Haiku 4.5) proposes candidates; `baseline` (Sonnet 4.5) reads only the cited ranges and answers. Credits = both steps.

## Results
| Arm | Total credits (9 runs) | Median/run | Avg line hits (of 3) |
|-----|------------------------|------------|----------------------|
| baseline, Sonnet alone (exp. 03) | 4.765 | 0.568 | 2.33 |
| reader v2 (exp. 03) | 0.587 | 0.054 | 1.33 |
| **reader v3** | 0.752 | ~0.08 | 1.78 |
| **pipeline (v3 + Sonnet verify)** | **2.689** | ~0.27 | **1.89** |

Per question line hits (reps 1,2,3): Q1 reader 0,1,1 / pipeline 1,0,2; Q2 reader 2,3,3 / pipeline 3,3,2; Q3 reader 2,2,2 / pipeline 2,2,2. File path correct in 18/18.

## Findings
1. Step 1 worked: v3 raised reader accuracy from 1.33 to 1.78 (Q2 from 1/3 to 2-3/3) for about 28% more credit (0.587 -> 0.752).
2. Pipeline cost 44% less than Sonnet alone (2.689 vs 4.765) and reached 81% of its line accuracy (1.89 vs 2.33). Not equal accuracy, so this is a trade-off, not a free win.
3. Verification added little: pipeline accuracy was only +0.11 over reader v3 alone, for +1.94 credits. Reader v3 alone is the best value per credit in this data.
4. Q1 (middleware) is the weak spot for every arm (baseline also 2/3); the Sonnet verify step did not fix it and even lost a hit in rep 2.

## Caveats
n=9, one repo, Python only, three questions, scoring counts only cited start lines. Differences of ~0.1 hit are within noise. The first rep of earlier experiments had no baseline re-run with the new scorer beyond the rescoring in exp. 03.

## Next
1. Rerun baseline with the same pre-set scorer to remove the rescoring caveat (cost ~4.8 credits; or use 1 rep x 3 questions, ~1.6).
2. Look at Q1 misses (`P_Q1_*` final texts) for a prompt or tool fix.
3. Try `reader` as an actual delegated subagent from the default agent, and measure whether delegation overhead eats the saving.
4. Add harder/other-language questions before drawing conclusions.
