---
inclusion: always
---

# Use the IDE-index subagents for code intelligence

The JetBrains IDE index (MCP server `ide-index`) is semantic: it beats grep-and-read for navigation, refactors and diagnostics. Its full schema set is large, so the main agent carries only a small set of cheap lookups and three subagents carry the rest.

Call these directly (single answer, short output): `ide_find_definition`, `ide_find_references`, `ide_find_implementations`, `ide_find_class`, `ide_find_file`, `ide_symbol_info`, `ide_file_structure`, `ide_diagnostics`, `ide_index_status`, `ide_project_status`, `ide_sync_files`. If a reference/implementation list looks long (more than ~15 hits) or needs follow-up hops, delegate it to `ide-reader` next time instead.

Everything else (call/type hierarchy, project diagnostics, refactors, build, tests) goes through a subagent. Project and IDE management (open/close project, modules, plugin install, IDE restart) is not exposed to agents: ask the user to do it in the IDE.

| Need | Subagent |
|---|---|
| Where is X defined/used, who calls Y, what implements Z, type hierarchy, file structure, "does this file have errors", list tests | `ide-reader` (read-only) |
| Rename/move/safe-delete, change signature, member edits, structural replace, Java-to-Kotlin, reformat/imports, build, run tests | `ide-builder` |
| Anything the IDE cannot answer (non-code files, unsupported language), shell work, docs | `sidekick` |

Rules:
1. Self-contained task: goal, file paths or symbol names, expected result, constraints. Subagents cannot see this chat.
2. Ask for a short report with file:line, not file contents.
3. Ask `ide-reader` first for any "find/trace" question; only fall back to `sidekick` (grep) if it reports unsupported language or dumb mode.
4. Refactors go through `ide-builder` with `dryRun` first. Review its diff yourself before accepting.
5. After you or a tool changed files outside the IDE, tell the subagent to call `ide_sync_files`.
6. Independent queries run in parallel; one-symbol lookups you already know the answer to are not worth delegating.
7. Treat reports as claims: spot-check cited lines for anything that matters.

Prerequisites (user side): JetBrains IDE open with the project indexed (smart mode); plugin tools you need are enabled in Settings > Tools > Index MCP Server (many are off by default); the port in the `mcpServers` entry of `main.json`, `ide-reader.json` and `ide-builder.json` matches your IDE (29170 IntelliJ, 29172 PyCharm, 29173 WebStorm). `.kiro/settings/mcp.json` is disabled on purpose so other agents do not load the schemas.

## Debugger (`debugger` subagent)

Use `debugger` only for a concrete, reproducible bug that reading code and running tests cannot explain. It is expensive (many tool round-trips), so first try reading the code and a failing test.
- Brief it with: run configuration or test, failing condition, suspect `file:line`, values to observe.
- Prefer logpoints over stepping; it has a ~15 tool-call budget and reports hypothesis plus evidence. It never edits code; you fix the bug.
- Set the debugger plugin's safety mode to Read-only in Settings > Tools > Debugger MCP Server. Default port 29190 is IntelliJ IDEA (PyCharm 29192, WebStorm 29193); edit `.kiro/agents/debugger.json` if yours differs.
