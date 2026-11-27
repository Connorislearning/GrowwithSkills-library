---
name: video-creative-analysis
description: Diagnoses why Meta video ads win or lose by splitting each into hook, hold, click and convert, then recommends the next creative test.
license: MIT
metadata:
  category: creative
  public: true
  version: 0.2.0
---
# Video creative analysis

## Scripts

Code does the math so no AI tokens are spent on it. Scripts need Python 3.9 or later and nothing else. `python3 scripts/funnel.py --export <ad-level.csv>` (or `--account <label>` to read the local database) computes hook, hold, CTR, conversion rate and CPA per ad, the account medians and each ad's problem stage, and prints JSON. The agent does the judgment: why winners win, the frame-by-frame hook review, and the next tests. If the agent cannot run Python, follow the steps below by hand. Try it first with the made-up files in `samples/`.

## Inputs

1. Ad-level data from Meta Ads Manager: an uploaded or pasted export, or a Meta Ads connector if the agent has one. Needed columns: Ad name, Amount spent, Impressions, 3 second video plays, ThruPlays, Link clicks, Results.
2. Target CPA. Ask if missing.
3. Optional: the video files or links, for the first 3 seconds breakdown.

Skip any ad with under 1,000 impressions. Say how many you skipped.

## Metrics

1. Hook rate = 3 second video plays / impressions.
2. Hold rate = ThruPlays / 3 second video plays. If the user prefers watch-percent, use 50% (or 75%) video plays / 3 second video plays instead, and say which one you used.
3. CTR = link clicks / impressions.
4. Conversion rate = results / link clicks.
5. CPA = spend / results.

Compute the account median for each metric. Judge each ad against the median, not a fixed benchmark.

## Diagnosis

Find the first stage where the ad falls clearly below the median. That is the problem stage.

1. **Hook problem.** Low hook rate. People scroll past. Test a new first 3 seconds, keep the body.
2. **Body problem.** Good hook, low hold. The promise in the hook is not paid off. Tighten the middle or move the payoff earlier.
3. **Offer problem.** Good hold, low CTR. People watch but do not care enough to click. Test the offer, the CTA or the angle.
4. **Landing problem.** Good CTR, low conversion rate. The ad works. Fix the page or the form, not the creative.

## First 3 seconds breakdown

If a video is provided, extract frames at 0, 1, 2 and 3 seconds (for example with ffmpeg) and look at them. Describe what is on screen, any text overlay, and the first spoken line. Name the hook type: question, callout, pattern interrupt, demo, testimonial, stat, or other.

## Output

1. One sentence on the top pattern across the account.
2. A table ranked by spend: ad, spend, hook rate, hold rate, CTR, CPA, problem stage.
3. For the top 3 winners: why they work, in two sentences each.
4. For the top 3 spenders that lose: the problem stage and one test.
5. Three next creative tests, each as one line: what to change, what to keep, what metric should move.

## Save to the local data store

If the agent can write files, save to the user's local data store (default `paid-social-data/`, one SQLite file; see `references/local-data-store.md`). save its rows to the `daily_metrics` table (the script does this), and save the analysis to `reports/`, including the hook type named for each video. Use the user's account label, never an ad account ID. If the store does not exist, offer to create it.

## Rules

Every number traces to the export. Say when sample sizes are small. Never include client names or account IDs in anything saved or shared.

<!-- cta:start -->
## Want this run for you?

Connor Hancer builds and runs these reporting systems for paid social teams. Contact: [CONTACT_URL_TBD]?utm_source=skill&utm_medium=github&utm_campaign=video-creative-analysis
<!-- cta:end -->
