---
name: meta-daily-spend-check
description: Daily Meta ads health check. Reads yesterday's ad set export, flags wasted spend, delivery problems and cost spikes, and ranks them by dollars at risk. Use for a morning account check or when someone asks what needs attention in a Meta account today.
public: true
---
# Meta daily spend check

## Inputs

1. A Meta Ads Manager CSV export at the ad set level with daily rows for the last 8 days. Needed columns: Day, Ad set name, Ad set budget, Amount spent, Results, Impressions, CPM, Frequency, Delivery.
2. Target CPA. Ask if missing.

## Checks

Run each check on yesterday, using the prior 7 days as the baseline.

1. **Zero results burn.** Spend over 2× target CPA with zero results in the last 3 days. Red.
2. **CPA drift.** 3 day CPA more than 50% above target. Red if spend is meaningful, yellow otherwise.
3. **Underdelivery.** Spend under 70% of daily budget for 2 days in a row. Yellow. Check the Delivery column for learning limited or rejected ads.
4. **CPM spike.** Yesterday's CPM more than 30% above the 7 day average. Yellow. Note if frequency also rose.
5. **Fatigue.** Frequency above 3 on a prospecting ad set with CTR down versus the 7 day average. Yellow.
6. **Overspend.** Meta can spend above the daily budget on single days and balances it across the week. Only flag overspend when the 7 day total is more than 10% over 7× the daily budget.

## Ranking

Rank every flag by dollars at risk: yesterday's spend on that ad set for red flags, half of it for yellow. Show the biggest first.

## Output

Write it like a Slack message.

First line: green, yellow or red for the whole account, plus total spend yesterday and CPA vs target.

Then up to 5 flags. Each one is one line: ad set, what is wrong, the number, and the action (pause, cut budget, refresh creative, check delivery, watch).

If nothing is flagged, say "No action needed today" and stop. Do not pad it.

## Rules

Recommend, do not act. Never pause or change anything in an account without the user's go ahead. Every number traces to the export. Never include client names or account IDs in anything saved or shared.
