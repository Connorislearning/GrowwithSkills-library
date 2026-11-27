---
name: eos-weekly-report
description: Weekly paid media report as a Google Doc in EOS format. Ties the week's logged changes to results in the ad account and CRM.
license: MIT
metadata:
  category: project-management
  public: true
  version: 0.1.0
---
# EOS weekly report

Builds the paid media section of a weekly leadership meeting in the EOS (Entrepreneurial Operating System) format. The default layout follows the sections of the EOS Level 10 Meeting that need data: Scorecard, Rock review, Headlines, To-Do list and Issues. If the user shares their own EOS template, use it instead and keep its section order.

## Scripts

Code does the math so no AI tokens are spent on it. Scripts need Python 3.9 or later and nothing else. `python3 scripts/scorecard.py --account <label> --goals goals.json` (or `--export <file> --history history.csv`, plus `--crm <crm.csv>`) computes every scorecard number, its on or off track status, and the before and after numbers for each logged change. Write the doc from its JSON; do not recompute. Goals live in a small JSON file (see `samples/goals.json`). If the agent cannot run Python, follow the steps below by hand. Try it first with the made-up files in `samples/`.

## Inputs

Ask for anything missing, a few at a time.

1. The week's ad results, from one of: the output of weekly-wow-check, an ads manager export (uploaded or pasted), or an ad platform connector. Any platform works.
2. Scorecard measurables and weekly goals. If the user has none, propose these and ask them to set the goal for each: spend, results, cost per result, revenue or ROAS (if tracked), CTR, frequency. Keep it to 5 to 10 measurables. Each needs an owner.
3. Rocks: the quarter's 3 to 7 priorities for paid media, each with an owner. Ask once per quarter and reuse them.
4. Last week's to-do list, if there was one, so each item can be marked done or not done.
5. The week's work log from paid-social-work-log (the `history` table in the local database). This is the main source for what was done, so nobody has to remember every change.
6. Optional: results from the CRM or analytics tool the team uses (HubSpot, Salesforce, Shopify, GA4 or any other), through a connector or an export: leads, qualified leads, pipeline, sales or revenue for the same week.
7. Optional: pacing from qoq-pacing.

## Sections

1. **Header.** Report week, prepared date, prepared by.
2. **Scorecard.** A table: measurable, owner, goal, this week, last week, status. Status is "On track" when the result meets the goal and "Off track" when it does not. Mark off-track rows clearly (red text or a red cell in Google Docs). Do not explain off-track rows here; each one becomes an issue.
3. **Rock review.** Each rock, its owner, and "On track" or "Off track". One line of evidence per rock, from the data or the work log.
4. **Changes and impact.** Group the week's work log rows into 3 to 7 actions (for example "moved 30% of budget to the new hook ads"). For each: what was done, when, and what moved in the ad account or CRM in the days after, with numbers. Say "Too early to tell" when there are fewer than 3 days of data after the change. Say "No clear effect" rather than claiming one. Results can lag, so check CRM results up to 14 days after a change.
5. **Headlines.** Up to 5 one-sentence items that people should know: a big win, a platform change, a creative that broke out, a delivery problem. No discussion.
6. **To-do list.** Last week's to-dos marked done or not done. New to-dos from this week, each with an owner and a due date within 7 days.
7. **Issues list.** One line per issue, worded as the problem to solve, not the fix. Start with every off-track scorecard row and rock. Add anything from the data that needs a decision. Rank the top 3. The meeting solves them with IDS (Identify, Discuss, Solve), so do not solve them in the doc.

## Building the doc

1. If a Google Docs or Google Drive connector is available, create a Google Doc named "Paid media weekly: <week dates>" (or copy the user's template), fill it, and share the link.
2. If not, produce a .docx file, or Markdown that pastes into Google Docs, and say which connector would let you create it directly.

## Writing rules

Plain words. Numbers in every scorecard cell. Every status is "On track" or "Off track", never "mostly" or "close". Keep the whole doc to one or two pages.

## Save to the local data store

If the agent can write files, save to the user's local data store (default `paid-social-data/`, one SQLite file; see `references/local-data-store.md`). Read the week's numbers from the `daily_metrics` table, the work log from `history.csv`, and last week's EOS report from `reports/` (for the to-do list). Save the doc text and link to `reports/`. Use the user's account label, never an ad account ID. If the store does not exist, offer to create it.

## Rules

- Every number traces to an input. If a number is missing, write "Not available" in the cell.
- The doc may go to a client or leadership. Include only that account's data.
- Never include client names or ad account IDs in anything saved to the skill library.
- EOS, Level 10 Meeting and Rocks are terms from EOS Worldwide. This skill is not affiliated with EOS Worldwide.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=eos-weekly-report
<!-- cta:end -->
