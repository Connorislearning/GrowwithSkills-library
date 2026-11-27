# Skill Library

Skills that run a paid social media buyer's week, by Connor Hancer. Log the work every day, check spend during the day, report on Monday and Friday, zoom out every two weeks, and keep the best results as portfolio stories.

- **Any AI tool.** Each skill is a folder in the open [Agent Skills](https://agentskills.io/specification) format: a `SKILL.md` the AI follows. Claude, Codex, Cursor and Copilot read it directly. In ChatGPT, paste the `SKILL.md` in as instructions.
- **Any ad platform or CRM.** Examples use Meta because it is the most common. The work log connects to the Meta Ads MCP first, falls back to the Meta Marketing API, then to a manual export. Every skill works from an export.
- **Code where code can do it.** Python scripts in each skill do the math, so no AI tokens are spent on it. The AI only does the judgment and the writing.
- **Your history stays yours.** Everything is saved to one local database on your machine.

## The week

| When | Skill | What it does |
| --- | --- | --- |
| End of every day | [paid-social-work-log](skills/project-management/paid-social-work-log) | Logs every change in your ad accounts, with the reason you give. Never invents one |
| After budget changes | [daily-spend-check](skills/project-management/daily-spend-check) | Spend-only pacing: is money going out at the normal speed for this hour? |
| Monday and Friday | [weekly-wow-check](skills/project-management/weekly-wow-check) | Week over week: cost per result, spend, CPC, CTR, frequency, fatigue, outliers. For Slack |
| Friday | [eos-weekly-report](skills/project-management/eos-weekly-report) | Google Doc in EOS format. Ties the week's logged changes to results in the ad account and CRM |
| Friday | [weekly-insights-deck](skills/project-management/weekly-insights-deck) | The weekly report as eight slides (draft) |
| Friday | [portfolio-story-worthy-moments](skills/project-management/portfolio-story-worthy-moments) | Finds record results and writes private and client-safe portfolio stories |
| Every two weeks, monthly, quarter end | [qoq-pacing](skills/project-management/qoq-pacing) | Executive briefing against budget, volume and revenue goals, and the budget move to make |
| When planning creative | [video-creative-analysis](skills/creative/video-creative-analysis) | Which stage of each video breaks: hook, hold, click or convert |

More in [docs/media-buyers-week.md](docs/media-buyers-week.md).

## Quick start

1. **Install the skills** into your AI tool:

   ```
   npx skills add Connorislearning/GrowwithSkills-library
   ```

   Or copy the folders in `skills/` by hand:

   | Tool | Copy skill folders into |
   | --- | --- |
   | Claude Code | `.claude/skills/` |
   | Codex, Cursor, Copilot | `.agents/skills/` |

2. **Try a skill on its sample data.** Every skill's README has a "Try it" command. The files in each `samples/` folder are made-up sample data, not from any real account. You need Python 3.9 or later and nothing else.

   ```
   cd skills/project-management/weekly-wow-check
   python3 scripts/wow.py --export samples/meta-daily-export.csv --platform meta --account demo --end 2026-11-22
   ```

3. **Run the work log tonight.** Ask your AI for "today's paid social work log". It creates `paid-social-data/` in your working folder.

## Your data and your keys

- Your data is saved in `paid-social-data/paid-social.db`, a SQLite file on your machine. The folder ignores itself in git, so it is never committed. `python3 scripts/store.py export` writes every table to CSV for Google Sheets. See [docs/local-data-store.md](docs/local-data-store.md).
- Accounts are stored under a label you choose, such as `client-a`. Ad account IDs are never stored.
- For the Meta Marketing API fallback, set `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID` as environment variables, or in a `.env` file. `.env` is in `.gitignore`. Never commit a token or paste one into a chat.

## Connect through MCP

This repository also deploys a read-only MCP server on Cloudflare Workers that serves the skills' instructions. Add the Worker's address plus `/mcp` (shown on the landing page) as a remote MCP server (custom connector) in your AI tool, then call `list_skills` and `get_skill`. Only skills marked `public: true` are served.

## Develop

```
python3 tests/check_skills.py   # skill format and safety checks
python3 tests/run_samples.py    # run every skill on its sample data
npm install && npm run dev      # run the Worker locally
```

Built on Cloudflare's [authless remote MCP template](https://developers.cloudflare.com/agents/guides/remote-mcp-server/).

## Want this run for you?

Connor Hancer builds and runs paid social reporting systems for teams. Contact: [CONTACT_URL_TBD]

## License

MIT. See [LICENSE](LICENSE).
