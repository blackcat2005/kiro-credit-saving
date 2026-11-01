# Experiment 09 - `sidekick` (full-toolset side-task agent) vs main agent alone

Date: 2026-11-01. Kiro CLI 2.35.1. Agent: `.kiro/agents/sidekick.json` (Haiku 4.5, tools `*`, auto-approved tools read-only). Steering: `.kiro/steering/side-tasks.md` (always on; tells the main agent what to delegate). Cost = account `/usage` delta (30 s settle) because run-stream credits undercount subagent usage. Raw run logs were kept outside the repo and are not included.

## Light task (this repo, 1 run per arm)
Task: list the experiment write-ups with titles, and find markdown files that mention "sidekick".
| Arm | Credits (account) | Stream credits | Notes |
|-----|-------------------|----------------|-------|
| Delegated to `sidekick` (agent spawned itself) | 0.36 | 0.199 | spawn confirmed (`role: sidekick`) |
| Main agent alone (`subagent` not trusted) | 0.31 | 0.304 | tried to spawn, was blocked, did it directly |
Result: delegating a light task cost ~16% more. Both answers correct.

## Heavier task (Django clone, 2 runs per arm, alternating)
Task: explain how the migration autodetector decides rename vs remove+add, citing file:line for key functions and a 5-line control-flow summary. Reference lines: `generate_renamed_fields` 1089, `only_relation_agnostic_fields` 111, `deep_deconstruct` 72 (autodetector.py), `ask_rename` 67 (questioner.py).
| Run | Arm | Credits (account) | Tool calls | Function names right (of 4) | Lines right (of 4) |
|-----|-----|-------------------|------------|-----------------------------|--------------------|
| 1 | main alone | 0.97 | 13 | 3 | 2 |
| 2 | delegated | 0.61 | 15 | 3 | 1 |
| 3 | main alone | 0.57 | 5 | 3 | 0 |
| 4 | delegated | 0.69 | 8 | 3 | 0 |
Means: main alone 0.77, delegated 0.65 (about 15% lower), but main alone ranged 0.57-0.97, so the ranges overlap. Stream credits for delegated runs were 0.26 (about 40% of real cost). In all four runs the spawn status was confirmed for the delegated arm and blocked for the main arm.

## Findings
1. Delegation did not show a reliable saving: ~16% more on a light task, ~15% less (within noise) on a heavier one. n = 1 and 2 per arm.
2. Accuracy was the same in both arms (3/4 function names, line citations poor everywhere); the line-based scorer cannot separate them.
3. The steering's "do not delegate tasks smaller than the cost of explaining them" did not stop the main agent from delegating a light task. The threshold is too soft or ignored.
4. The biggest measured saving in these experiments is still the small agent answering lookups directly (0.08/run, exp. 06) rather than a larger agent coordinating subagents.
5. Run streams undercount delegated usage again (consistent with exp. 05-06): use `/usage` deltas.

## Practical guidance (from the data so far)
- Use `sidekick` for work that produces large output or can run in parallel (long test runs, big logs, many-file sweeps) and for isolating context; do not expect big savings on simple lookups.
- For plain "where is X / how does Y work" questions, a read-only small-model agent called directly is the cheaper choice.
- If the main agent delegates too eagerly, tighten the steering with a concrete threshold (e.g. only when more than ~5 search/read steps are expected) and re-measure.

## Caveats
Very small samples; one repo; the heavier task had no ground-truth summary check, only function names and lines; credits for Free-plan `/usage` have 0.01 resolution and a delay, so deltas were read after 30 s.

## Untested next steps
- Cheaper models for the read-only agent (`qwen3-coder-next` 0.05x, `minimax-m2.1` 0.15x in the CLI list) and their accuracy.
- Tasks with truly large output (test suites, long logs).
- A concrete delegation threshold in the steering.
