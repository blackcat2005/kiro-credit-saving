# Experiment 02 - read-only Haiku subagent vs main agent (Django)

Date: 2026-11-01. Kiro CLI 2.35.1, Windows. Repo: `django/django` shallow clone in `sandbox-repos/django` (7,085 files, ~45 MB, gitignored).
Question (same for all arms): "Where does Django build and run the middleware chain for a request/response? Give file:line and a short summary."
Reference answer (from the source): `BaseHandler.load_middleware` base.py:27, `get_response` :138, `get_response_async` :154.

## Setup
- `reader` agent: `.kiro/agents/reader.json` (CLI 2.x needs JSON; `.md` agents are not loaded by 2.x). Model `claude-haiku-4.5` (0.4x), tools `fs_read, grep, glob, code`, no write/shell.
- Credits come from `--output-format stream-json` (`meteringUsage`, summed). Script: `scripts/run-arm.ps1`.

## Results (n = 1 per arm)
| Arm | Credits | Max context | Tool calls | Secs | Accuracy vs reference |
|-----|---------|-------------|------------|------|-----------------------|
| A: default agent (auto) explores itself | 0.377 | 7.2% | 5 | 27 | Good (27->26, 138, 154->152) |
| B: `reader` called directly (Haiku 4.5) | 0.067 | 8.1% | 4 | 12 | Weak: ranges `39-88`, `130-142`, earlier run `32/162/175` |
| C: default agent told to use `reader` | 0.167 | 11.2% | 11 | 30 | Right idea, line ranges loose |

## Findings
1. B is ~5.6x cheaper than A, but it is a direct call to the small agent, not delegation from a large one.
2. Haiku's line numbers are unreliable (different between two runs, off by up to 24 lines). Files and symbol names were right.
3. C is inconclusive: the log shows "Spawning agent crew" and no `reader` name, so it is unproven that `reader` ran. Highest context use (11.2%).
4. Kiro CLI exposes per-step credits in stream-json (answers brief section 4, "does it report credits", for the CLI; ACP not tested).
5. CLI 2.x model list has Haiku 4.5 only (no Haiku 5.5). The user's default agent also loads an MCP (`codegraph`) that failed in the run; it did not affect results but adds noise.

## Limits
n=1, one question, `auto` may pick different models per run, credit total may include setup overhead.

## Improvements (priority order)
1. **Make measurements trustworthy**: 3-5 runs x 3 questions (easy / cross-file / "how does X work"); pin A with `--model claude-sonnet-4.5`; report median. Run in a clean agent without user-global MCPs.
2. **Fix accuracy, not just cost**: change `reader` output to symbol + file only (no line numbers) or require it to confirm each cited line with `read_file`/`code` before answering; the main agent then reads exact ranges. Score each answer against a fixed reference.
3. **Two-step pipeline**: reader returns candidates, main agent reads only those ranges. Compare total credits against A; a cheap but wrong reader that forces rework is a net loss.
4. **Verify delegation (arm C)**: read `C_delegate.jsonl` around "Spawning agent crew"; confirm which agent ran and on which model. Try naming `reader` in the agent's prompt/description so auto-delegation selects it; check whether subagent credits are billed at the subagent's model rate.
5. **Cache findings**: have the reader write a short note to `.kiro/context/notes/<topic>.md`, then ask a related question and measure whether the second ask gets cheaper. This tests the original "read files instead of re-exploring" idea without an MCP server.
6. **Cap output and effort**: limit reader reply to ~15 lines to keep returned context small (C's context was highest).
7. **Revisit later**: Haiku 5.5 (0.06x) once available in the CLI/IDE; the IDE path; the MCP repo-map idea only if steps 2-5 show exploration is still the main cost.
