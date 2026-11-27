# Paid social work log

A two-minute end-of-day record of every change I made across my paid social accounts, and why. Meta first, other platforms the same way.

## The problem

Three weeks after a CPA jump, nobody remembers what changed. Ads Manager's activity history shows what changed, but not why, and it is hard to search. Without a log, weekly and quarterly reports describe results without explaining them.

## My process

At the end of each day the log pulls the day's changes: budgets, bids, pauses, new ads, targeting. It drops the automatic system noise and sends me a short numbered list.

I reply with "ok" or a few words of reason per change. That takes under two minutes. The confirmed list is added to history.csv, one row per change, which opens in Google Sheets.

Most of it runs as small Python scripts on my own machine. One saves a daily snapshot of every campaign, ad set and ad and compares it with yesterday's. The other keeps the history file. That means no AI tokens spent on comparing rows, and the same answer every time. The AI only asks me why and writes the message.

The log never guesses a reason. If I don't give one, it says "not given".

The reason is the valuable part. When the Monday report shows CPA up 30%, the log tells me it was the day I moved budget into a new audience. My weekly and quarterly reports read the log so they can explain results, not just list them.

## What it gives you

A confirmed, dated change log with reasons, saved on your own machine.

## Works with

Any agent that reads Agent Skills. Best with a Meta Ads connector (Meta's Ads MCP server has activity log tools). Without one, paste an Activity History export or just tell it what you changed.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/changes.py snapshot --export samples/meta-export-2026-11-19.csv --platform meta --account demo
python3 scripts/changes.py snapshot --export samples/meta-export-2026-11-20.csv --platform meta --account demo
python3 scripts/changes.py diff --platform meta --account demo
python3 scripts/history.py confirm --why "1=CTR down 30% after 3 weeks"
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Connecting to Meta

The skill uses the Meta Ads MCP first. If you don't have it, it falls back to the Meta Marketing API, then to a manual export. For the API, set `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID` as environment variables, or put them in a `.env` file that git ignores. Never commit a token or paste it into a chat. The database stores your own account label, never the account ID.

## Assumptions to confirm

The confirmation goes to the chat by default. Slack or email works if a connector is available.

Sources: Meta Marketing API, [Ad Account Activities](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-account/activities); Meta Ads MCP server, [Activity logs tools](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-tools-activity-logs).
