#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { z } from "zod";
import { refresh, findSymbol } from "./repomap.js";

const ROOT = process.env.KIRO_SAVER_ROOT ?? process.cwd();
const server = new McpServer({ name: "kiro-credit-saver", version: "0.1.0" });
const text = (t: string) => ({ content: [{ type: "text" as const, text: t }] });

server.tool(
  "get_repo_map",
  "Return a compact map of this repository (modules with one-line descriptions). Pass module to get the files and symbols of one module. Auto-refreshes stale cache in .kiro/context/.",
  { module: z.string().optional().describe("Module (top-level directory) name for detail") },
  async ({ module }) => {
    const { mods } = refresh(ROOT);
    if (!module) return text(readFileSync(join(ROOT, ".kiro/context/index.md"), "utf8"));
    const f = join(ROOT, ".kiro/context/modules", module.replace(/[^\w.-]/g, "_") + ".md");
    if (!existsSync(f)) return text(`Unknown module "${module}". Known: ${mods.map((m) => m.name).join(", ")}`);
    return text(readFileSync(f, "utf8"));
  },
);

server.tool(
  "find_symbol",
  "Find functions/classes/types by case-insensitive name substring. Returns file:line entries only.",
  { name: z.string().min(1).describe("Symbol name or substring") },
  async ({ name }) => {
    const hits = findSymbol(refresh(ROOT).mods, name);
    return text(hits.length ? hits.join("\n") : "No matches");
  },
);

await server.connect(new StdioServerTransport());
