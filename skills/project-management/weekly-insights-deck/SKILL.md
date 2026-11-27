---
name: weekly-insights-deck
description: Turns the weekly report into an eight-slide client or leadership deck, built in Google Slides or as a .pptx.
license: MIT
metadata:
  category: project-management
  version: 0.2.0
---
# Weekly insights deck

## Inputs

1. The week's eos-weekly-report output (from `reports/` in the local data store, or pasted). This is the main input: the deck presents that report as slides and adds no new analysis.
2. If there is no weekly report, fall back to weekly-wow-check output, or an ads manager export.
3. Audience: client or internal. Ask if unclear.
4. Optional: a Google Slides template to copy.

## Deck structure

Eight slides. One idea per slide. No slide gets more than 40 words of text plus a chart or table.

1. **Title.** Account, week dates.
2. **The headline.** One sentence on what happened this week and why.
3. **KPIs.** Spend, results, CPA. This week, last week, change, and target.
4. **Pacing.** Quarter to date spend vs budget and projected landing.
5. **What worked.** Top 1 to 3 creatives or audiences, with the number that proves it.
6. **What did not.** Top 1 to 3 problems and what was done about them.
7. **Next week.** Up to 3 tests, each with the metric it should move.
8. **Decisions needed.** Anything the reader must approve. Say "None this week" if empty.

## Building the deck

If a Google Slides or Google Drive connector is available, copy the template if one was given, otherwise create a new presentation. Fill the slides in order. Share the link at the end.

If no connector is available, produce the same eight slides as a .pptx file or a slide by slide outline, and say which connector would let you build it in Google Slides.

## Writing rules

Lead every slide with the takeaway as the title, not a label. "CPA fell 18% after the hook refresh" beats "Performance". Plain words. No jargon the client would not use.

## Save to the local data store

If the agent can write files, save to the user's local data store (default `paid-social-data/`, one SQLite file; see `references/local-data-store.md`). Read the week's numbers from the `daily_metrics` table and findings from `reports/` when no export is given. Save the slide outline and the deck link to `reports/`. Use the user's account label, never an ad account ID. If the store does not exist, offer to create it.

## Rules

Every number traces to an input. Never invent a number to fill a slide. If data for a slide is missing, put "Not available this week" on it. For a client deck, include only that client's data. Never put client names or numbers in anything saved to Skill Library.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=weekly-insights-deck
<!-- cta:end -->
