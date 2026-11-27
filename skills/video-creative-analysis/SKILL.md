---
name: video-creative-analysis
description: Diagnose why Meta video ads win or lose. Splits each video's funnel into hook, hold, click and convert, names the stage that breaks, and recommends the next test. Use when someone shares video ad performance data or a video file and asks what is working or what to make next.
public: true
---
# Video creative analysis

## Inputs

1. A Meta Ads Manager CSV export at the ad level. Needed columns: Ad name, Amount spent, Impressions, 3 second video plays, ThruPlays, Link clicks, Results.
2. Target CPA. Ask if missing.
3. Optional: the video files or links, for the first 3 seconds breakdown.

Skip any ad with under 1,000 impressions. Say how many you skipped.

## Metrics

1. Hook rate = 3 second video plays / impressions.
2. Hold rate = ThruPlays / 3 second video plays.
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

## Rules

Every number traces to the export. Say when sample sizes are small. Never include client names or account IDs in anything saved or shared.
