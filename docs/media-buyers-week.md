# The Media Buyer's Week

How the skills fit into a paid social media buyer's normal week. Described by Connor Hancer on 2026-11-27. Works with any AI tool that reads skills, any ad platform, and any CRM, or by hand with exports.

## Every day

- **During the day**, the buyer changes budgets and builds ads, through an AI tool (an MCP connector) or by hand in each ads manager.
- **After budget changes:** `daily-spend-check`. Spend only. Is money going out at the normal speed for this hour? Most useful for brands, often e-commerce, that must spend their full budget.
- **End of day:** `paid-social-work-log`. It shows the changes it can see in the connected accounts. The buyer adds what it missed and why. It saves everything to the local database. It never invents a reason.

## Monday

- `weekly-wow-check`: last week vs the week before. Cost per result, spend, CPC, CTR and frequency, with creative fatigue and outliers flagged. Written for Slack.

## Friday

- `weekly-wow-check` again: this week so far vs the same days last week.
- `eos-weekly-report`: the Google Doc for the reporting meeting. It reads the week's work log, so nobody has to remember fifty changes from Monday, and shows what moved afterward in the ad account and the CRM.
- `weekly-insights-deck`: the same report as slides, if the audience wants slides. (Draft; needs more work.)
- `portfolio-story-worthy-moments`: finds record results and turns them into private and client-safe portfolio stories.

## Every two weeks, monthly, and at quarter end

- `qoq-pacing`: zoom out. Are we on track for the quarter? Should part of next month's budget move into this month, or the reverse? At quarter end it is the executive briefing.

## When planning creative

- `video-creative-analysis`: which stage of each video breaks (hook, hold, click or convert), and the next test.

## How data moves

Every skill reads from and writes to one local SQLite database, `paid-social-data/paid-social.db`, on the buyer's own machine. See [local-data-store.md](local-data-store.md). Python scripts in each skill do the math and the file work, so no AI tokens are spent on it. The AI only asks why and writes.
