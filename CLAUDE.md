# Kiro Credit Saver

See `docs/kiro-credit-saver-brief.md` for goals, architecture and unverified assumptions.

- MCP server: `mcp-server/` (TypeScript). `cd mcp-server && npm install && npm run build && npm test`.
- `.kiro/` holds steering, the `explorer` agent, and `settings/mcp.json`; `.kiro/context/` is generated cache (do not hand-edit).
- Keep tool output compact; tool names ≤64 chars, `[A-Za-z0-9_]`, non-empty descriptions.
