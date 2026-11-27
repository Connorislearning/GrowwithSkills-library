# Meta weekly week-over-week report

Every Monday, a Slack-ready summary of what changed in a Meta account last week, and why.

## The problem

Monday mornings start with someone asking "how did last week go?" Answering it means pulling an export, building a pivot in Google Sheets, and eyeballing percent changes across dozens of ads. Small teams often skip it, so problems like creative fatigue run for weeks before anyone notices.

## My process

I compare last week with the week before on five numbers: cost per result, amount spent, CPC, CTR and frequency. I look at the account first, then at each ad.

Then I look for patterns, not single numbers. Rising frequency with falling CTR is creative fatigue, so the fix is new creative. Rising CPC with steady CTR is usually the auction getting more expensive, so the creative is fine. A big swing in which ads got the spend explains most account-level changes, so I call that out before anything else.

I also flag outliers in both directions. The ad that suddenly got cheaper is worth as much attention as the one that got worse.

The output is written to paste straight into Slack. No tables, because Slack does not show them.

## What it gives you

One overall line, up to five things that need attention, up to three things that are working, and the actions for this week.

## Works with

Any AI agent that reads Agent Skills (Claude, Codex, Cursor, Copilot). With no connector, upload or paste your Ads Manager export.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/wow.py --export samples/meta-daily-export.csv --platform meta --account demo --end 2026-11-22
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Assumptions to confirm

The thresholds (20% cost per result, frequency 3 with a 15% CTR drop, 25% CPC, $50 minimum spend) are starting points.
