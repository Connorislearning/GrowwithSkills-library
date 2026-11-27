---
name: meta-qoq-pacing
description: Pace Meta ad spend against a quarterly budget and compare quarter to date results with the same point last quarter. Use when someone asks if a Meta account is on pace, how much to spend per day to land the quarter, or how this quarter compares to last.
public: true
---
# Meta QoQ pacing

## Inputs

Ask for these if they are missing. Do not guess them.

1. Quarterly budget for the account or campaign group.
2. Target CPA or cost per result.
3. A Meta Ads Manager CSV export with daily rows. Needed columns: Day, Campaign name, Amount spent, Results. Cover this quarter to date and the same days of last quarter.
4. Quarter start and end dates. Default to calendar quarters.

## Math

Use these definitions. Show the numbers you used.

1. Days elapsed (d) and total days in quarter (D). Count today as not yet elapsed.
2. Expected spend to date = budget × d / D.
3. Pacing % = actual spend to date / expected spend to date.
4. Run rate = average daily spend over the last 7 days.
5. Projected quarter spend = spend to date + run rate × (D − d).
6. Required daily spend = (budget − spend to date) / (D − d).
7. CPA to date = spend to date / results to date.
8. Projected results = results to date + (run rate / recent 7 day CPA) × (D − d).

## QoQ comparison

Compare this quarter to last quarter at the same day number (day 40 vs day 40). Report spend, results and CPA for both, and the change in percent. Do not compare a partial quarter to a full one.

## Flags

1. Pacing under 90%: underspending. Check delivery problems before raising budgets.
2. Pacing over 110%: overspending. Say on what date the budget runs out at the current run rate.
3. CPA more than 20% above target: pacing is not the real problem. Say so before recommending more spend.
4. Fewer than 10 days left and pacing off by more than 15%: say the gap may not be closable without a big daily swing, and name the swing.

## Output

Start with one sentence: on pace, ahead or behind, and by how much.

Then a small table: budget, spent, pacing %, projected spend, required daily spend, CPA vs target, projected results.

Then the QoQ table.

Then one recommendation, with the daily budget number to set. Keep it under 150 words outside the tables.

## Rules

Every number must trace to the CSV or the user's inputs. If a column is missing, say which one and stop. Never include client names or account IDs in anything saved or shared.
