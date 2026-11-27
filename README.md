# Skill Library

Media buying and creative strategy skills by Connor Hancer. Each skill is a written system any AI can run. They are served as a read-only remote MCP server on Cloudflare Workers.

## The skills

| Skill | What it does |
| --- | --- |
| [meta-qoq-pacing](skills/meta-qoq-pacing) | Paces spend against a quarterly budget and gives the daily budget to set tomorrow |
| [meta-daily-spend-check](skills/meta-daily-spend-check) | Morning account check that ranks problems by dollars at risk |
| [video-creative-analysis](skills/video-creative-analysis) | Finds which stage of a video ad breaks: hook, hold, click or convert |
| [weekly-insights-deck](skills/weekly-insights-deck) | Turns the other three into an eight slide Google Slides report |

They work as a system. Pacing, the spend check and the creative analysis feed the weekly deck. The report is a byproduct of work already done.

## Use them

Add the Worker's address plus `/mcp` (shown on the landing page) as a remote MCP server (custom connector) in Claude, ChatGPT or any MCP client. Call `list_skills`, then `get_skill`.

## How it works

Every skill is a folder in `skills/` with a `SKILL.md` for the AI and a `README.md` for people. Each push to `main` redeploys the Cloudflare Worker through Workers Builds. Only skills marked `public: true` are served.

## Run locally

```
npm install
npm run dev
```

Built on Cloudflare's [authless remote MCP template](https://developers.cloudflare.com/agents/guides/remote-mcp-server/).

## License

MIT. See [LICENSE](LICENSE).
