# Experiment 03 - baseline (Sonnet 4.5) vs reader v2 (Haiku 4.5), 3 questions x 3 reps

Date: 2026-11-01. Kiro CLI 2.35.1, repo `sandbox-repos/django`. Driver: `scripts/run-matrix.ps1` (raw: `docs/experiments/runs/`, `matrix.csv`, `rescored.csv`).
Arms: `baseline` (pinned `claude-sonnet-4.5`, read tools, no MCP) vs `reader` (v2 prompt with accuracy rules, `claude-haiku-4.5`, read tools). Both called directly (no delegation).
Ground truth (def lines in the Django source):
- Q1 middleware: `core/handlers/base.py` load_middleware 27, get_response 138, get_response_async 154
- Q2 filter: `db/models/query.py` filter 1723, _filter_or_exclude 1739, _filter_or_exclude_inplace 1750
- Q3 URL resolve: `urls/resolvers.py` URLResolver 504, URLPattern.resolve 471, URLResolver.resolve 671

## Cost (credits per run)
| Question | baseline (3 runs) | reader (3 runs) |
|----------|-------------------|-----------------|
| Q1 | 0.291 / 0.568 / 0.311 | 0.116 / 0.084 / 0.054 |
| Q2 | 0.683 / 0.657 / 0.823 | 0.045 / 0.045 / 0.051 |
| Q3 | 0.382 / 0.450 / 0.600 | 0.057 / 0.081 / 0.054 |
| **Median** | **0.568** | **0.054** (~10x cheaper) |
| **Total (9 runs)** | 4.765 | 0.587 (~8x cheaper) |

Time: baseline 26-65 s, reader 12-27 s. Tool calls: baseline 3-14, reader 3-7.

## Accuracy (line hits within +-2 of the def line, out of 3; file path correct in 9/9 for both)
| Question | baseline | reader |
|----------|----------|--------|
| Q1 | 2,2,2 | 1,1,1 |
| Q2 | 3,3,3 | 1,1,1 |
| Q3 | 2,2,2 | 2,2,2 |
| **Avg** | **2.33/3 (78%)** | **1.33/3 (44%)** |

Results were highly repeatable within an arm. Reader lost points mainly on Q2: it found `filter` (1723) but stopped after 3 tool calls and missed the `_filter_or_exclude*` helpers it delegates to.

## Scoring caveat
The first scorer rejected wide ranges (e.g. `base.py:27-104`) and Windows `\` paths and gave both arms low scores. I changed the rule after seeing the results (start line of a cited range counts) and rescored from the saved answers. The new rule is more reasonable but was not fixed in advance. Scores measure "cited the right starting line", not answer quality overall. No test of the two-step pipeline yet.

## Findings
1. Reader v2 is ~8-10x cheaper but returns about 44% of the checkable line references vs 78%. Cheap is not enough: it under-explores multi-hop questions (Q2).
2. v2 accuracy rules did not make it fabricate: when wrong it is mostly incomplete rather than wrong (symbols found 2/3 or 3/3).
3. Net value depends on rework. If the main agent must re-search the missing 1-2 items, part of the ~0.5 credit saving is lost. Untested.

## Next
1. Prompt reader to enumerate delegated callees ("also list what each function calls/delegates to") and require >= N search steps for "how does X work" questions; rerun Q2.
2. Test the real pipeline: reader (cheap) then main agent reading only cited ranges, versus baseline; compare total credits and accuracy.
3. Verify delegation from the main agent actually invokes `reader` (the earlier arm C log was ambiguous).
4. Add harder questions (cross-module, ambiguous names) and a second repo; fix the scoring rule in advance.
5. Try `claude-sonnet-4.5` vs `auto` as the "main" arm to see if auto's routing already captures savings.
