# Experiment 08 - do saved notes make a repeat question cheaper?

Date: 2026-11-01. Agent `writer` (Haiku 4.5, writes `.kiro/context/notes/`). Script: `scripts/run-notes-reuse.ps1` (data: `docs/experiments/runs/notes-reuse.csv`, `N_*`). 3 Django questions per phase: (1) fresh, notes dir cleared; (2) identical question again; (3) paraphrased question. Cost from top-level run streams (reliable for non-delegated runs) and account `/usage` deltas (they agree: 0.54 / 0.89 / 0.54).

A first attempt was invalid (phases 2-3 ran only Q3 because of a `$q`/`$Q` variable clash in my script) and was discarded; this is the rerun.

## Results
| Phase | Credits (3 runs) | Tool calls | Avg line hits (of 3) |
|-------|------------------|------------|----------------------|
| 1. fresh | 0.544 | 25 | 1.33 |
| 2. same question again | **0.891** | 32 | 1.00 |
| 3. paraphrase | 0.543 | 27 | 1.33 |

Per run (credits): Q1 0.137 / 0.164 / 0.148; Q2 0.225 / 0.299 / 0.208; Q3 0.182 / 0.428 / 0.187.

## Findings
1. **Notes did not reduce cost. The repeat question was 64% more expensive** (0.891 vs 0.544), with more tool calls and no gain in accuracy. In `same_again` the agent mostly re-explored with grep/read; in Q3 it listed the notes dir and read one note but then re-read the source anyway.
2. The prompt told `writer` to read an existing note first, but a Haiku-class agent did not do it reliably, and it picked a new slug every time: **8 notes were created for 3 topics** (duplicates like `queryset-filter-delegation.md` and `queryset-filter-internals.md`). Lookup by a model-chosen slug does not work.
3. The `writer` costs about twice the read-only `reader` (0.18 vs 0.08 per run) and was less accurate here (1.33 vs 2.0 for `reader` v3), so the note-taking itself is an extra cost that the experiment did not pay back.
4. Changelog: lines are now appended, not overwritten (earlier probe lost lines), but a blank line appears between some entries and two entries are not unique per topic.

## Interpretation
Letting the cheap model decide whether to reuse a note is the weak link. Cache lookup has to be deterministic (outside the model), as in the original brief (index/hash checked by code), not an instruction in the prompt.

## Next
1. Deterministic lookup: a small script or the main agent computes a stable key (e.g. normalised topic or file paths), checks the notes/ index, and passes the note path to the agent, so the agent never chooses between "read note" and "explore".
2. Make notes useful to read: one index file (`notes/index.md`: slug, topic, files, mtime/hash of the files it cites) the main agent loads, plus staleness check by file hash.
3. Re-measure repeat cost with that lookup; target: repeat question < 30% of fresh cost.
4. Consider dropping `writer` for question answering and keeping it only for recording changes (changelog) where its output is not re-used by itself.
