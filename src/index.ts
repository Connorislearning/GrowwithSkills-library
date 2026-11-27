import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";
import { SKILLS } from "./skills.generated";

// Skill names are short slugs. Anything else is rejected before it is looked up or logged.
const SKILL_NAME = /^[a-z0-9-]{1,64}$/;

// Records one tool call: tool, skill and time only. Never blocks or fails the response.
function logUsage(env: Env, ctx: ExecutionContext, tool: string, skill: string | null) {
	ctx.waitUntil(
		env.USAGE_DB.prepare("INSERT INTO usage_events (tool, skill) VALUES (?, ?)")
			.bind(tool, skill)
			.run()
			.catch((err) => console.error("usage log failed", err)),
	);
}

function createServer(env: Env, ctx: ExecutionContext) {
	const server = new McpServer({ name: "Skill Library", version: "0.2.0" });

	server.registerTool(
		"list_skills",
		{
			description:
				"List every skill in Connor Hancer's Skill Library, a library of media buying and creative strategy skills. Call this first.",
			inputSchema: z.object({}),
			annotations: { readOnlyHint: true, openWorldHint: false },
		},
		async () => {
			logUsage(env, ctx, "list_skills", null);
			return {
				content: [
					{
						type: "text",
						text: SKILLS.length ? SKILLS.map((s) => `${s.name}: ${s.description}`).join("\n") : "The library is empty.",
					},
				],
			};
		},
	);

	server.registerTool(
		"get_skill",
		{
			description: "Get the full instructions for one skill by name, then follow them.",
			inputSchema: z.object({
				name: z.string().regex(SKILL_NAME, "Use a skill name from list_skills").describe("A skill name from list_skills"),
			}),
			annotations: { readOnlyHint: true, openWorldHint: false },
		},
		async ({ name }) => {
			const skill = SKILLS.find((s) => s.name === name);
			if (skill) logUsage(env, ctx, "get_skill", skill.name);
			return {
				content: [
					{
						type: "text",
						text: skill ? skill.content : `No skill named "${name}". Call list_skills to see the options.`,
					},
				],
			};
		},
	);

	return server;
}

// TODO(Connor): paste your LinkedIn profile URL here. The link is hidden while this is empty.
const LINKEDIN_URL = "";

const esc = (s: string) => s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]!);

function md(text: string) {
	return text
		.split(/\n{2,}/)
		.map((block) => {
			const b = esc(block.trim());
			if (!b) return "";
			if (b.startsWith("## ")) return `<h3>${b.slice(3)}</h3>`;
			if (b.startsWith("# ")) return "";
			return `<p>${b.replace(/\n/g, " ")}</p>`;
		})
		.join("");
}

function homePage(origin: string) {
	const cards = SKILLS.map(
		(s) => `<section><h2>${esc(s.name)}</h2><p class="d">${esc(s.description)}</p>${md(s.readme)}</section>`,
	).join("");
	return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skill Library · Connor Hancer</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap">
<style>
:root{--bg:#1e1e1e;--surface:#262626;--fg:#ffffff;--muted:#b3b8c2;--line:#3a3a3a;--blue:#0066ff;--cyan:#00ffff;color-scheme:dark}
body{font:17px/1.6 Inter,"DejaVu Sans",system-ui,sans-serif;max-width:760px;margin:0 auto;padding:48px 20px;color:var(--fg);background:var(--bg)}
h1,h2{font-family:"Space Grotesk","DejaVu Sans",system-ui,sans-serif}
h1{font-size:40px;margin:0 0 8px}h2{margin:0 0 4px;font-size:22px;color:var(--cyan)}h3{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:20px 0 4px}
.lead{font-size:20px;color:var(--muted)}.d{color:var(--muted);font-style:italic}
section{background:var(--surface);border:1px solid var(--line);border-top:3px solid var(--blue);border-radius:12px;padding:24px;margin:24px 0}
code{background:#000;color:var(--cyan);padding:2px 6px;border-radius:4px;word-break:break-all}
a{color:var(--cyan)}nav{display:flex;flex-wrap:wrap;gap:16px;margin:16px 0}
footer{color:var(--muted);font-size:14px;margin-top:40px;border-top:1px solid var(--line);padding-top:16px}
</style></head><body>
<h1>Skill Library</h1>
<p class="lead">Media buying and creative strategy skills by Connor Hancer, performance marketing and GTM engineer. Each skill is a written system any AI can run.</p>
<nav><a href="https://connorhancer.ai">connorhancer.ai</a>${LINKEDIN_URL ? `<a href="${esc(LINKEDIN_URL)}">LinkedIn</a>` : ""}<a href="https://github.com/Connorislearning">GitHub</a></nav>
<p>Connect any MCP client to <code>${esc(origin)}/mcp</code> to use them. The tools are read-only.</p>
${cards}
<footer>${SKILLS.length} skills · MIT licensed · Served from Cloudflare Workers</footer>
</body></html>`;
}

export default {
	async fetch(request: Request, env: Env, ctx: ExecutionContext) {
		const url = new URL(request.url);
		if (request.method === "GET" && (url.pathname === "/" || url.pathname === "")) {
			return new Response(homePage(url.origin), { headers: { "content-type": "text/html; charset=utf-8" } });
		}
		if (url.pathname.startsWith("/mcp")) {
			// The caller's IP is used only as the rate-limit key. It is never stored or logged.
			const caller = request.headers.get("cf-connecting-ip") ?? "unknown";
			const { success } = await env.RATE_LIMITER.limit({ key: caller });
			if (!success) return new Response("Too many requests. Try again in a minute.", { status: 429 });
		}
		return createMcpHandler(() => createServer(env, ctx))(request, env, ctx);
	},
} satisfies ExportedHandler<Env>;
