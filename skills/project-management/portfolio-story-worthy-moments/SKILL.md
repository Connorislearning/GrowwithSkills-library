---
name: portfolio-story-worthy-moments
description: Scans your saved paid social history for extraordinary results and turns each into a portfolio story, with a client-safe version to share.
license: MIT
metadata:
  category: project-management
  public: true
  version: 0.1.0
---
# Portfolio story-worthy moments

Media buyers get great results and forget them, or lose the proof when they leave a job. This skill reads the history the other skills save in the local data store, finds results worth telling, ties each one to the changes that caused it, and saves it as a story the user can use on a resume, on LinkedIn or in an interview.

## Scripts

Code does the math so no AI tokens are spent on it. Scripts need Python 3.9 or later and nothing else. `python3 scripts/moments.py --store paid-social-data --platform <p> --account <label> --save` finds the moments, attaches the logged changes from the work log, skips ones already saved, and prints JSON. The agent's job is the writing: the private story, the client-safe version, the resume bullet and the LinkedIn draft. If the agent cannot run Python, follow the steps below by hand. Try it first with the made-up files in `samples/`.

## Inputs

1. The local data store folder (default `paid-social-data/`). See `references/local-data-store.md` for the layout. The script reads the `daily_metrics`, `history` and `moments` tables.
2. If the store does not exist yet, the user can upload past exports and reports instead. Save them into the store first, then scan.
3. Scan window. Default: the last 7 days when run weekly, the last 1 day when run daily. Always compare against the full history in the store.

## What counts as story-worthy

Check each account and each ad against its own history. A moment needs at least 14 days of history for the account, and meaningful spend (default: at least $500 in the period). All thresholds are defaults the user can change.

1. **Record.** Best week ever for the account on cost per result, ROAS or result volume.
2. **Turnaround.** Cost per result down 25% or more, holding for at least 2 weeks, with spend flat or up.
3. **Efficient scale.** Spend up 50% or more while cost per result stayed within 10%.
4. **Breakout creative.** An ad at half the account's median cost per result or better, on at least 10% of account spend.
5. **Goal hit.** A quarter that landed within 5% of budget and met its volume or revenue goal (from qoq-pacing reports).
6. **Rescue.** A problem flagged red by a daily or weekly check that was fixed within 7 days, with the dollars saved estimated from the spend at risk.

Skip anything already in the `moments` table for the same account, type and period.

## Find the cause

For each moment, look in the `history` table for changes on that account in the 14 days before the result started. List the ones that plausibly caused it, with their logged reasons. If there are none, say "Cause not logged" rather than guessing.

## Write the story

For each new moment, write `moments/<YYYY-MM-DD>_<slug>.md` with two versions.

**Private version** (stays in the store): account label, exact numbers, dates, the linked changes.

Structure it as Situation, Task, Action, Result:
- Situation: where the account was, with the starting number.
- Task: the goal.
- Action: what was changed, from the work log.
- Result: the ending number and the change in percent, over what period.

**Client-safe version** (for sharing), built from the private one:
- Replace the account with a generic description the user approves, such as "a DTC skincare brand". Never use the account label, client name, or ad account ID.
- Show percent changes and multiples, not dollar amounts, unless the user says a dollar figure is cleared to share.
- Round numbers (for example "about 40%" instead of "38.7%").
- Remove anything that identifies the client: product names, audience names, campaign names, screenshots.

Also give, from the client-safe version:
- One resume bullet, starting with a verb, with the number.
- A LinkedIn post draft, under 120 words.

## Confirm with the user

Show the user each new moment: one line on what happened, then the client-safe version. Ask them to confirm it is accurate and choose the generic description. Set `public_ready` to yes only after they approve it. Add a row to `moments/moments.csv` either way.

If nothing qualifies, say "No new story-worthy moments this period" and stop.

## Running it on a schedule

Default is every Friday, after the week's reporting. If the agent supports scheduled tasks, offer to set that up; the user can choose daily instead. Otherwise the user runs it by asking for "this week's story-worthy moments."

## Rules

- Every number traces to the data store or a file the user provided. Never round in the private version.
- Never claim a cause the work log does not support.
- Never publish or post anything. Drafts only, and only client-safe versions leave the store.
- Never include client names or ad account IDs in anything shared outside the user's workspace.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=portfolio-story-worthy-moments
<!-- cta:end -->
