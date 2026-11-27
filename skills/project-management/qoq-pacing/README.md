# Meta QoQ pacing

Most pacing reports tell you what you spent. This one tells you what to set the budget to tomorrow.

## The problem

A quarterly budget is a promise. Buyers miss it in two ways. They underspend early and panic spend in the last two weeks at a worse CPA. Or they overspend and go dark before the quarter ends. Both are pacing failures you can see coming weeks ahead.

## My process

It starts with three quick questions: the quarterly budget, the volume goal (leads, purchases or sign-ups) and the revenue goal. From those it works out the cost per result and ROAS the quarter needs, so the briefing is judged against the business goal, not a number someone guessed.


I check pacing against a straight line from the first day of the quarter to the last. Then I project where the quarter lands at the current 7 day run rate. The gap between the two is the real number. It turns into one figure: the daily budget needed from today to land on budget.

I always check efficiency before spend. If CPA is well above target, more budget makes the quarter worse. The skill says that out loud before it recommends a bigger number.

Then I compare against the same day last quarter. Day 40 against day 40. That shows whether the account is actually improving or just spending more.

## What it gives you

A one-page executive briefing: the bottom line, a scorecard against budget, volume and revenue goals, a quarter-over-quarter table, what drove the results, and the decision to make. Written for founders who track the business in Google Sheets.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/pacing.py --export samples/meta-daily-export.csv --budget 50000 --volume-goal 1600 --revenue-goal 100000 --today 2026-11-27
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Assumptions to confirm

Pacing is linear across days. Some accounts should weight toward weekdays or the end of quarter. The 90% and 110% thresholds and the 20% CPA guardrail are starting points.
