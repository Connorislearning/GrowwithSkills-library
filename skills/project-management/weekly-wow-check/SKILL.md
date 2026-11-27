---
name: weekly-wow-check
description: Monday week-over-week Meta ads report for Slack. Flags changes in cost per result, spend, CPC, CTR and frequency, plus creative fatigue.
license: MIT
metadata:
  category: project-management
  public: true
  version: 0.1.0
---
# Meta weekly week-over-week report

Run this on Monday to compare last week (Monday to Sunday) with the week before. Run it again on Friday to compare this week so far (Monday to Thursday, or to yesterday) with the same days last week, before the weekly report meeting. It writes a short report the user can paste into Slack.

## Inputs

Ask for anything missing. Do not guess.

1. Data for the last 14 days at the ad level, with daily rows. Any of these works:
   - A Meta Ads Manager export (CSV or XLSX) the user uploads or pastes.
   - A Meta Ads connector or MCP tool, if the agent has one.
   Needed columns: Day, Campaign name, Ad set name, Ad name, Amount spent, Impressions, Link clicks, Results, Frequency. CPC and CTR can be computed if they are missing.
2. Target cost per result. Optional. Ask once, and continue without it if the user has none.
3. Week start day. Default Monday.

If a needed column is missing, name it and stop.

## Math

Run `python3 scripts/wow.py --export <file> --platform <platform> --account <label>` (add `--end <yesterday> --days 4` on Friday, and `--target-cpr` if there is a target). It saves the rows to the local data store, does all the math and flags below, and prints JSON. Write the Slack message from that JSON; do not recompute the numbers. If the agent cannot run Python, compute them by hand as follows.


Compute each metric for last week (LW) and the week before (PW), for the whole account and for each ad.

1. Amount spent = sum of spend.
2. Cost per result = spend / results.
3. CPC = spend / link clicks.
4. CTR = link clicks / impressions.
5. Frequency = impressions / reach if Reach is present. If not, use the spend-weighted average of the Frequency column, and say so.
6. Week-over-week change = (LW − PW) / PW, shown as a percent.

Skip ads with under $50 spend in both weeks. Say how many you skipped. This threshold is a default the user can change.

## Flags

1. **Cost per result up** more than 20% WoW, or above target. Red if the ad or account spent meaningfully, yellow otherwise.
2. **Creative fatigue.** Frequency up WoW and above 3, and CTR down more than 15% WoW. Yellow. Recommend a creative refresh.
3. **CPC spike.** CPC up more than 25% WoW while CTR held steady. Usually rising auction cost, not the creative. Yellow.
4. **Spend shift.** An ad's share of account spend moved more than 10 percentage points. Note it, because it explains most account-level changes.
5. **Outlier.** Any ad whose WoW change in cost per result is more than 2 standard deviations from the account's average change. Call out both good and bad outliers.

All thresholds are starting points. Use the user's numbers if they give them.

## Output

Plain text that pastes cleanly into Slack. Use *bold* with single asterisks, and no tables, because Slack does not render Markdown tables.

```
*Meta weekly report: <LW dates> vs <PW dates>*
Overall: <green / yellow / red>. Spend $X (+Y%), cost per result $X (+Y%), CPC $X (+Y%), CTR X% (+Y pts), frequency X (+Y).

*Needs attention*
• <Ad or ad set>: <what changed, with the number>. <Action.>
(up to 5)

*Working*
• <Ad>: <what improved, with the number>.
(up to 3)

*This week*
• <1 to 3 actions>
```

If nothing is flagged, write the overall line and "No action needed this week."

## Save to the local data store

If the agent can write files, save to the user's local data store (default `paid-social-data/`, one SQLite file; see `references/local-data-store.md`). save its rows to the `daily_metrics` table (the script does this), and save the report to `reports/`. If the export is missing, read the last 14 days from the `daily_metrics` table instead. Use the user's account label, never an ad account ID. If the store does not exist, offer to create it.

## Rules

- Every number traces to the input data. Show the date ranges used.
- Recommend, do not act. Never change anything in an ad account without the user's go ahead.
- Never include client names or ad account IDs in anything saved or shared outside the user's own workspace.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=weekly-wow-check
<!-- cta:end -->
