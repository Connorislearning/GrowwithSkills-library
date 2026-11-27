# Local data store

Every skill in this library saves what it reads and produces to one private database on the user's own machine. Over time it becomes a full history of the accounts: every change and why it was made, daily numbers, reports and wins. It keeps working if access to an ad account ends.

## What it is

One SQLite file, `paid-social-data/paid-social.db`. SQLite is built into Python, so there is nothing to install, and it is a single file you can back up or copy. The scripts write to it; the AI never has to re-read raw exports. To open the data in Google Sheets or Excel, run `python3 scripts/store.py export` and use the CSV files it writes to `paid-social-data/csv/`. The work log also keeps `paid-social-data/history.csv` up to date after every change.

Why SQLite and not plain CSV files: the database stops duplicate rows when the same day is pulled twice, never overwrites a reason once it is saved, and lets every skill read the same history without parsing files. CSV is kept as the export format because that is what people open.

## Location

Default `paid-social-data/` in the user's working folder. Pass `--store <path>` to any script to use another folder. Use the same folder for every skill.

## Tables

| Table | One row per | Written by |
|---|---|---|
| history | change, with the user's why | paid-social-work-log |
| pending | change found today, waiting for the why | paid-social-work-log |
| snapshots | campaign, ad set or ad, per day (status, budget, bid) | paid-social-work-log |
| daily_metrics | ad per day (spend, impressions, reach, clicks, results, revenue, frequency, video plays) | any skill given an export, or meta_api.py insights |
| moments | story-worthy moment | portfolio-story-worthy-moments |
| accounts | account label (with time zone and notes) | the user |

Columns of `history`: date, time, platform, account_label, level, campaign, ad_set, ad, change_type, old_value, new_value, why, status, source.

## Rules for every skill

1. **Never invent a reason.** `why` holds only the user's own words. With no reason it is "not given" and the row is unconfirmed.
2. **Use account labels, not IDs.** `account_label` is a short alias the user chooses, such as `client-a`. Ad account IDs are never stored.
3. **Keep it private.** The folder gets its own `.gitignore` that ignores everything in it. Never commit it or share it outside the user's workspace.
4. **Secrets stay out of files you share.** API tokens are read from environment variables or a git-ignored `.env` file only.

`store.py` is the same file in every skill's `scripts/` folder, so each skill works when installed on its own.
