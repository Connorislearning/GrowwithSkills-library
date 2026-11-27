# Daily spend check

Answers one question during the day: is money going out at the right speed?

## The problem

Many brands, e-commerce especially, need to spend their full budget every day. A budget change, a rejected ad or a payment problem can quietly stop delivery, and nobody notices until the next morning, when the day is already lost.

## My process

I look only at spend. I compare spend so far today with what is normal by this hour, using the same weekday over the last four weeks. A straight line through the day is the fallback when there is no history.

That gives a pace for each campaign and a projected end-of-day number. Under 80% pace, I check the work log first, because a budget change I made this morning is often the reason. Over 125%, I remember that platforms can overspend a daily budget on single days and balance it across the week, so I only worry when the weekly total is at risk.

I run it after any budget change and a few times a day for brands that must spend fully. It recommends. It never touches a budget on its own.

## What it gives you

A one-line pace summary and up to five campaigns that need attention, biggest dollar gap first.

## Works with

Any agent that reads Agent Skills, and any ad platform. Best with a connector. Without one, paste or upload a spend export with the time it was pulled.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/pace.py --today samples/today-so-far.csv --history samples/hourly-spend-history.csv --hour 14 --must-spend
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Assumptions to confirm

The 80% and 125% pace thresholds, the 2-hour stall rule and the 30% off-trend rule are starting points.
