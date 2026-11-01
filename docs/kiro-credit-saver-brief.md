# Kiro Credit Saver — brief (condensed)

Goal: cut Kiro credit use per session. Kiro reads a cached, deterministic repo map instead of re-exploring the project every turn.

## Flow
1. Deterministic discovery first (git ls-files, regex/ctags symbols, config) — no LLM.
2. Haiku summarises only unclear parts, written once and cached by hash.
3. Large model plans from steering + repo map; small model executes tasks; large model reviews diff only.

## Layers
1. `.kiro/context/index.md` (small) + `modules/<name>.md` (detail). One writer per module file.
2. Steering `.kiro/steering/repo-map.md` always includes `index.md`.
3. MCP server `mcp-server/` (TypeScript): `get_repo_map`, `find_symbol`; later `summarize_file`, `get_task_context`. Staleness checked at read time (content hash) because hooks do not run in subagents.
4. Custom subagent `.kiro/agents/explorer.md` (Haiku, read-only + writes to `.kiro/context/`).
5. Later: package as a Power; optional ACP wrapper. A2A is overkill.

## Unverified (test in Kiro before investing in Haiku/cache)
- Is Haiku in this account's model list?
- Which model do built-in subagents use; is it configurable?
- Do small-model subagents really cost fewer credits?
- Credit cost of one MCP tool call?
- Does ACP report credit usage?

## Order
0 baseline (3–5 real tasks: credits per prompt, % context) → 1 MCP `get_repo_map` → 2 steering + index → 3 re-measure → 4 `explorer` → 5 Haiku + cache → 6 Power.

## Open decisions
Language (chosen: TypeScript), Kiro IDE vs CLI, personal vs team.

Note: Haiku via direct API costs API money, not Kiro credits; savings come from Kiro reading less.
