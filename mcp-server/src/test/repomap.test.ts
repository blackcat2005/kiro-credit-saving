import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { refresh, findSymbol, extractSymbols } from "../repomap.js";

test("extractSymbols ts/py", () => {
  assert.deepEqual(extractSymbols("a.ts", "export async function foo() {}\nclass Bar {}").map((s) => s.name), ["foo", "Bar"]);
  assert.deepEqual(extractSymbols("a.py", "def f():\n  pass\nclass C: pass").map((s) => s.name), ["f", "C"]);
});

test("refresh writes only changed modules", () => {
  const d = mkdtempSync(join(tmpdir(), "ksr-"));
  mkdirSync(join(d, "src")); mkdirSync(join(d, "lib"));
  writeFileSync(join(d, "src/a.ts"), "export function hello() {}");
  writeFileSync(join(d, "lib/b.py"), "def world(): pass");
  assert.deepEqual(refresh(d).written.sort(), ["lib", "src"]);
  assert.deepEqual(refresh(d).written, []);
  writeFileSync(join(d, "src/a.ts"), "export function hello2() {}");
  const r = refresh(d);
  assert.deepEqual(r.written, ["src"]);
  assert.match(readFileSync(join(d, ".kiro/context/index.md"), "utf8"), /\*\*src\*\*/);
  assert.equal(findSymbol(r.mods, "hello2").length, 1);
});
