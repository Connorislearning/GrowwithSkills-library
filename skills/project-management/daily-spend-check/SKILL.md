---
name: daily-spend-check
description: Intraday spend pacing check. Compares spend so far today with budgets and the normal hourly curve, and flags campaigns that will under- or overspend.
license: MIT
metadata:
  category: project-management
  public: true
  version: 0.3.0
---
# Daily spend check

Checks one thing: is money going out at the right speed today? It looks only at spend, not results. Use it after budget changes, and for brands (often e-commerce) that must spend their full budget every day. Run it a few times a day, or every hour on a schedule.

## Scripts

Code does the math so no AI tokens are spent on it. Scripts need Python 3.9 or later and nothing else. `python3 scripts/pace.py --today <today-so-far.csv> --hour <hours finished> [--history <hourly history.csv>] [--must-spend]` does all the math and flags below and prints JSON. Write the message from that JSON; do not recompute. If the agent cannot run Python, follow the steps below by hand. Try it first with the made-up files in `samples/`.

## Inputs

1. Today's spend so far, by campaign (or ad set if budgets are set there), from one of:
   - An ad platform connector or MCP tool (Meta, TikTok, Google, or any other).
   - An export or screenshot from the ads manager, uploaded or pasted, with the time it was pulled.
2. The daily budget for each campaign or ad set. Read it from the same source, or ask.
3. The normal hourly spend curve. Best: hourly spend for the same weekday over the last 4 weeks, from the local data store or a "by hour" breakdown export. If none is available, use a straight line through the day and say so.
4. The account's time zone. Ask once and save it in the local data store.
5. Today's budget changes, from the paid-social-work-log entries for today, if any.

## Math

For each campaign:

1. Share of day expected = the normal curve's cumulative share of daily spend at the current hour (for a straight line, hours elapsed / 24).
2. Expected spend now = daily budget × share of day expected.
3. Pace % = spend so far / expected spend now.
4. Projected end-of-day spend = spend so far / share of day expected.

Do not flag before 10% of the day's spend is expected, because early-hour numbers are too small to judge.

## Flags

1. **Underpacing.** Pace under 80%. Red if the brand must spend fully, yellow otherwise. Check whether it started after a budget change today (from the work log), a paused ad, a rejected ad, or a payment problem.
2. **Overpacing.** Pace over 125%. Yellow. Note that platforms can spend above the daily budget on single days and balance it over the week; Meta, for example, can spend up to 75% above a daily budget on a given day but no more than 7 times the daily budget across a week. Flag it red only if the weekly total is on track to exceed that.
3. **Stalled.** No spend in the last 2 hours on a campaign that normally spends then. Red.
4. **Off trend.** Account-level spend more than 30% away from the normal curve for this hour. Yellow.

All thresholds are defaults the user can change.

## Output

Short enough for a Slack message.

First line: account spend so far, expected by now, pace %, projected end of day vs total daily budget, and the time checked.

Then up to 5 flagged campaigns, biggest dollar gap first: campaign, pace %, projected end of day vs budget, likely reason, and the action (check delivery, raise budget, lower budget, watch).

If nothing is flagged, write "Spend is on pace" and stop.

## Save to the local data store

If the agent can write files, save to the user's local data store (default `paid-social-data/`, one SQLite file; see `references/local-data-store.md`). Save each check to `reports/`, and add hourly spend rows to the `daily_metrics` table when the source gives them, so the normal curve gets better over time. Use the user's account label, never an ad account ID.

## Rules

- Recommend, do not act. Never change a budget without the user's go ahead.
- Every number traces to the input data. Say when the normal curve was assumed.
- Never include client names or ad account IDs in anything shared outside the user's workspace.

Source for the Meta overspend rule: Jon Loomer, [Updates to Meta Ads Budgeting](https://www.jonloomer.com/updates-to-meta-ads-budgeting/); Meta Marketing API, [Budgets](https://developers.facebook.com/documentation/ads-commerce/marketing-api/bidding/overview/budgets.md).

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=daily-spend-check
<!-- cta:end -->
