---
name: qoq-pacing
description: Quarter-end executive briefing for Meta ads: pacing vs quarterly budget, same-day QoQ comparison, and the daily budget to set.
license: MIT
metadata:
  category: project-management
  public: true
  version: 0.2.0
---
# Meta QoQ pacing

An executive briefing on the quarter. Run it every two weeks or monthly to steer spend, and at quarter end as the review a founder or leadership team reads. It can also pace a single month inside the quarter. Write for a reader who tracks the business in Google Sheets and is not a media buyer: plain words, every metric defined the first time it appears.

## Scripts

Code does the math so no AI tokens are spent on it. Scripts need Python 3.9 or later and nothing else. After the intake questions, run `python3 scripts/pacing.py --account <label> --budget <n> --volume-goal <n> [--revenue-goal <n>]` (or `--export <file>`; add `--start/--end` for a month). It does all the math, the quarter-over-quarter comparison and the flags below, and prints JSON. Write the briefing from it; do not recompute. If the agent cannot run Python, follow the steps below by hand. Try it first with the made-up files in `samples/`.

## Intake questions

Ask these first, in one short message, before reading any data. Do not guess the answers.

1. What is the quarterly ad budget?
2. What is the volume goal for the quarter? (Results such as leads, purchases or sign-ups, and which one counts.)
3. What is the revenue goal for the quarter, if you track revenue from ads? (Skip if not.)
4. Quarter start and end dates. Default to calendar quarters.

From the answers, derive the targets and show them back to the user:
- Target cost per result = budget / volume goal.
- Target ROAS = revenue goal / budget (only if a revenue goal was given).

If the user already has a target CPA or ROAS that differs from the derived one, use theirs and say so.

## Data

1. Daily data from Meta Ads Manager: an uploaded or pasted export (CSV, XLSX, or a Google Sheet copied in), or a Meta Ads connector if the agent has one. Needed columns: Day, Campaign name, Amount spent, Results. Add Purchase conversion value (or the revenue column the account uses) if a revenue goal was given. Cover this quarter to date and the same days of last quarter.
2. Pacing curve. Default is a straight line (the same expected spend every day). If the user says the account spends more on weekdays or ramps at quarter end, weight expected spend by those days and say which curve you used.
3. Mode: mid-quarter or quarter-end review. Infer it from the dates.
4. Optional: the work log from paid-social-work-log, to explain what drove the results.

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
9. Volume pacing = results to date / (volume goal × d / D).
10. If a revenue goal was given: revenue to date, ROAS to date = revenue / spend, and projected revenue = revenue to date + run rate × recent 7 day ROAS × (D − d).

## QoQ comparison

Compare this quarter to last quarter at the same day number (day 40 vs day 40). Report spend, results and CPA for both, and the change in percent. Do not compare a partial quarter to a full one.

## Flags

1. Pacing under 90%: underspending. Check delivery problems before raising budgets.
2. Pacing over 110%: overspending. Say on what date the budget runs out at the current run rate.
3. CPA more than 20% above target: pacing is not the real problem. Say so before recommending more spend.
4. Volume pacing under 90% while spend pacing is on track: the money is going out but the results are not. Lead with this.
5. Fewer than 10 days left and pacing off by more than 15%: say the gap may not be closable without a big daily swing, and name the swing.

## Output

Write it as a one-page briefing. Keep it under 300 words outside the tables.

1. **Bottom line.** One or two sentences: on pace, ahead or behind, by how much, and whether efficiency (CPA) is on target.
2. **Scorecard table.** Budget, spent, pacing %, projected spend, cost per result vs target, results vs volume goal and projected results, and (if given) revenue vs revenue goal, ROAS and projected revenue.
3. **Quarter over quarter table.** This quarter vs last quarter at the same day number: spend, results, CPA, and the change in percent.
4. **What drove it.** Up to three reasons, each tied to a number from the data (for example, one campaign took most of the spend increase).
5. **Decision.** Mid-quarter: whether spend needs to be reallocated, including moving part of next month's budget into this month (or the reverse) when results are strong (or weak), with the dollar amount. Also the daily budget to set from today, and the date the budget runs out at the current run rate if overspending. Quarter-end: what to keep, what to stop, and the budget recommendation for next quarter.
6. **Definitions.** One line each for pacing %, run rate and CPA, for readers who are new to them.

## Save to the local data store

If the agent can write files, save to the user's local data store (default `paid-social-data/`, one SQLite file; see `references/local-data-store.md`). Save the intake answers and the briefing to `reports/`, and reuse saved intake answers for the same quarter. Add export rows to the `daily_metrics` table, and read last quarter from it when the user has no export for it. Use the user's account label, never an ad account ID. If the store does not exist, offer to create it.

## Rules

Every number must trace to the CSV or the user's inputs. If a column is missing, say which one and stop. Never include client names or account IDs in anything saved or shared.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=qoq-pacing
<!-- cta:end -->
