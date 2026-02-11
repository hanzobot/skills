#!/usr/bin/env node
/**
 * grok_search.mjs
 *
 * Minimal xAI (Grok) search wrapper.
 * - Uses xAI Responses API (OpenAI-compatible)
 * - Lets Grok run server-side tools:
 *   - web_search (web)
 *   - x_search (X/Twitter)
 *
 * Usage:
 *   node scripts/grok_search.mjs "query" --web
 *   node scripts/grok_search.mjs "query" --x
 *   node scripts/grok_search.mjs "query" --web --json
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";

function usage(msg) {
  if (msg) console.error(msg);
  console.error(
    "Usage: grok_search.mjs <query> (--web|--x) [--json] [--model <id>] [--max <n>]"
  );
  process.exit(2);
}

function readKeyFromHanzo BotConfig() {
  try {
    const p = path.join(os.homedir(), ".hanzo-bot", "bot.json");
    const raw = fs.readFileSync(p, "utf8");
    const j = JSON.parse(raw);
    // common places
    return (
      process.env.XAI_API_KEY ||
      j?.env?.XAI_API_KEY ||
      j?.env?.vars?.XAI_API_KEY ||
      null
    );
  } catch {
    return process.env.XAI_API_KEY || null;
  }
}

const args = process.argv.slice(2);
if (args.length === 0) usage();

let queryParts = [];
let mode = null; // 'web' | 'x'
let jsonOut = false;
let model = "grok-4-1-fast";
let maxResults = 8;

for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === "--web") mode = "web";
  else if (a === "--x") mode = "x";
  else if (a === "--json") jsonOut = true;
  else if (a === "--model") {
    const v = args[++i];
    if (!v) usage("Missing value for --model");
    model = v;
  } else if (a === "--max") {
    const v = Number(args[++i]);
    if (!Number.isFinite(v) || v <= 0) usage("Bad value for --max");
    maxResults = Math.floor(v);
  } else if (a.startsWith("-")) {
    usage(`Unknown flag: ${a}`);
  } else {
    queryParts.push(a);
  }
}

const query = queryParts.join(" ").trim();
if (!query) usage("Missing <query>");
if (!mode) usage("Must specify --web or --x");

const apiKey = readKeyFromHanzo BotConfig();
if (!apiKey) {
  console.error(
    "Missing XAI_API_KEY. Set env var or add env.XAI_API_KEY in ~/.bot/bot.json"
  );
  process.exit(1);
}

const toolType = mode === "x" ? "x_search" : "web_search";

// We ask Grok to *use the tool*, and return structured JSON.
// Note: xAI docs mention inline citations and citations lists.
const prompt = `Use the provided ${toolType} tool to research: ${JSON.stringify(
  query
)}\n\nReturn ONLY valid JSON (no markdown) in this schema:\n{\n  "query": string,\n  "mode": "${mode}",\n  "results": [\n    {"title": string|null, "url": string|null, "snippet": string|null}\n  ],\n  "citations": [string]\n}\n\nConstraints:\n- results length <= ${maxResults}\n- citations should be unique URLs\n- If you cannot find anything, return empty arrays (still valid JSON).`;

const body = {
  model,
  // OpenAI Responses API style:
  input: [
    {
      role: "user",
      content: [{ type: "input_text", text: prompt }],
    },
  ],
  tools: [{ type: toolType }],
  // don't store this on xAI side
  store: false,
  temperature: 0,
};

const res = await fetch("https://api.x.ai/v1/responses", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Authorization: `Bearer ${apiKey}`,
  },
  body: JSON.stringify(body),
});

if (!res.ok) {
  const t = await res.text().catch(() => "");
  console.error(`xAI API error: ${res.status} ${res.statusText}`);
  console.error(t.slice(0, 4000));
  process.exit(1);
}

const data = await res.json();

// Try to extract the model's text.
const text =
  data.output_text ||
  // xAI responses: output is an array of events; the assistant message is usually later.
  data?.output
    ?.flatMap((o) => (Array.isArray(o?.content) ? o.content : []))
    ?.find((c) => c?.type === "output_text" && typeof c?.text === "string")
    ?.text ||
  null;

if (!text) {
  // fallback: emit whole response
  if (jsonOut) {
    console.log(JSON.stringify({ query, mode, raw: data }, null, 2));
  } else {
    console.log(JSON.stringify(data, null, 2));
  }
  process.exit(0);
}

// If the model complied, `text` should be JSON.
if (jsonOut) {
  console.log(text.trim());
  process.exit(0);
}

// Pretty, human output for terminal usage.
let parsed;
try {
  parsed = JSON.parse(text);
} catch {
  console.log(text.trim());
  process.exit(0);
}

const lines = [];
lines.push(`Query: ${parsed.query ?? query}`);
lines.push(`Mode: ${parsed.mode ?? mode}`);
lines.push("");

const results = Array.isArray(parsed.results) ? parsed.results : [];
if (results.length) {
  lines.push("Results:");
  for (const r of results) {
    const title = r?.title || "(no title)";
    const url = r?.url || "";
    const snip = r?.snippet || "";
    lines.push(`- ${title}${url ? `\n  ${url}` : ""}${snip ? `\n  ${snip}` : ""}`);
  }
} else {
  lines.push("Results: (none)");
}

const citations = Array.isArray(parsed.citations) ? parsed.citations : [];
if (citations.length) {
  lines.push("");
  lines.push("Citations:");
  for (const c of citations) lines.push(`- ${c}`);
}

console.log(lines.join("\n"));
