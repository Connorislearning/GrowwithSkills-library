---
name: paid-social-work-log
description: Growth marketing paid social work log. Records each day's ad account changes with reasons, confirmed by the user and saved to a local file.
license: MIT
metadata:
  category: project-management
  public: true
  version: 0.1.0
---
# Paid social work log

Run this at the end of each workday. It records what changed in the user's paid social ad accounts today (Meta first; TikTok, Snapchat, Pinterest or LinkedIn work the same way if the user has their change history), asks the user to confirm it and add why, and saves the result to a running log file. Later skills (weekly reports, the EOS weekly report, the quarterly briefing) read this log so they can tie results to the changes that caused them.

## How the work is split

Python scripts in `scripts/` do the mechanical work, so it costs no AI tokens and gives the same answer every time. The agent only asks the user why and writes the message. Scripts need Python 3.9 or later and nothing else. Everything is saved in a local SQLite database, `paid-social-data/paid-social.db`, and `history.csv` beside it is rebuilt after every change so it opens in Google Sheets.

- `scripts/changes.py`: **what happened.** Brings in today's changes from an MCP activity log, or compares today's export snapshot with yesterday's. Shows two tables: what happened, and why.
- `scripts/meta_api.py`: the Meta Marketing API fallback when there is no MCP tool.
- `scripts/history.py`: **why it happened.** Saves the user's reasons into the `history` table, adds changes the user tells you about, and rebuilds `history.csv`.
- `scripts/store.py`: the local database.

Try it first with the made-up files in `samples/`. If the agent cannot run Python, do the same steps by hand and write rows in the history format below.

## Where today's changes come from

Use the first one that works, for each connected account:

1. **Meta Ads MCP** (or another platform's MCP tool). Call its activity log tool for today, save the result as JSON, then run `python3 scripts/changes.py import-activity --file <activity.json> --platform meta --account <label>`.
2. **Meta Marketing API.** If there is no MCP tool but the user has set `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID` (environment variables or a git-ignored `.env` file), run `python3 scripts/meta_api.py activities --account <label>`. Never ask the user to paste a token into the chat, and never write one to a file that could be committed.
3. **Manual export** (any platform). Save an ad-level export with status and budget columns, then run `python3 scripts/changes.py snapshot --export <file> --platform <platform> --account <label>` and `python3 scripts/changes.py diff --platform <platform> --account <label>`. The first day only saves a baseline.
4. **The user's own list**, typed or dictated, added with `history.py add`.

Use a short account label the user picks, such as `client-a`. Never store an ad account ID.

## Steps

1. Collect today's changes for every account as above. `python3 scripts/changes.py show` prints both tables.
2. Send the confirmation message below. Default: in this chat. Slack or email if the user named one and a connector is available.
3. Pass each reason exactly as the user wrote it: `python3 scripts/history.py confirm --why "1=scaling winner" --why "2=CPA 2x target"`. If the user says everything is fine as listed, use `--all-ok`.
4. For each change the user says is missing: `python3 scripts/history.py add --platform <p> --account <label> --campaign "<name>" --change "<what>" --why "<their words>"`.
5. If the user does not reply, run `confirm` with no reasons. Rows are saved as why "not given", unconfirmed. At the next run, show them (`history.py show`) and add reasons the user gives with `history.py set-why --id <n> --why "<their words>"`.

## Never invent a reason

The why column holds only the user's own words. If the user gives no reason, it stays "not given". Do not infer one from the data, even when it looks obvious. The scripts enforce this: they never fill in a why.

## Confirmation message

Two tables: what happened, then why.

```
Paid social work log for <date>: <N> changes in <M> campaigns.

What happened
1. <Campaign>  <Ad set>          budget: $200 -> $300
2. <Campaign>  <Ad set> / <Ad>   status: active -> paused

Why
1. <Campaign>  budget: $200 -> $300        not given
2. <Campaign>  status: active -> paused    not given

Reply with a reason by number (for example "1 scaling winner, 2 CPA 2x target"), "ok" to save as is, or tell me anything I missed.
```

If there were no changes, send "No changes logged today."

## History format

```
date,time,platform,account_label,level,campaign,ad_set,ad,change_type,old_value,new_value,why,status,source
2026-11-27,,meta,client-a,ad_set,Prospecting,Broad 25-44,,budget,200,300,scaling winner,confirmed,snapshot 2026-11-26 -> 2026-11-27
```

(Example row is made up.) It opens directly in Google Sheets.

## Running it every day

If the agent supports scheduled tasks, offer to schedule this run every weekday at a time the user picks. Otherwise the user runs it by asking for "today's work log."

## Save to the local data store

The scripts save everything: snapshots, pending changes and the confirmed history in `paid-social-data/paid-social.db`, plus `history.csv` for Google Sheets. The folder ignores itself in git.

## Rules

- Log only. Never change anything in the ad account.
- Every line traces to the change history or the user's own words. Do not invent reasons.
- The log lives on the user's own machine or workspace. Never include client names or ad account IDs in anything shared outside it.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=paid-social-work-log
<!-- cta:end -->
