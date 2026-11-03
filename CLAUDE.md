# Kiro Credit Saver

See `docs/kiro-credit-saver-brief.md` for goals, architecture and unverified assumptions. Experiment results: `docs/experiments/` (01-09). Conclusions so far are in 06 and 09.

- Experiment code, scripts, raw runs and the Django sandbox were deleted (they were never committed); only the write-ups remain. `sandbox-repos/` is gitignored for local clones.
- IDE-index setup (untested, not yet measured): `.kiro/agents/main.json` (native tools + 11 cheap `ide_*` lookups, run with `--agent main`), `ide-reader`, `ide-builder`, `debugger` (Haiku subagents, each declares its own `mcpServers`), steering `.kiro/steering/ide-index.md`. `.kiro/settings/mcp.json` is `disabled` on purpose. Needs a JetBrains IDE with the Index MCP and Debugger MCP plugins; ports in the agent files (29170 / 29190 = IntelliJ).
- `.kiro/agents/sidekick.json`: native-tools helper (Haiku 4.5) for side tasks. Auto-approved tools are read-only; writes/shell need approval (in headless runs they are blocked unless trusted). CLI 2.x agents are JSON; IDE Markdown agents are not loaded by CLI 2.x.
- `.kiro/steering/side-tasks.md` (always on): tells the main agent when and how to delegate to `sidekick`. Measured effect is small (exp. 09); tighten the threshold if it delegates too eagerly.
- Measure cost with `kiro-cli chat --no-interactive "/usage"` deltas (wait ~30 s); run-stream credits undercount subagent usage.
