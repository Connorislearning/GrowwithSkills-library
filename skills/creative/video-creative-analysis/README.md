# Video creative analysis

Tells you which part of a video ad is broken, so the next version fixes the right thing.

## The problem

Most teams judge a video by CPA and stop there. A losing ad gets killed and a new one gets made from scratch. That throws away the parts that worked.

## My process

I treat every video as a four step funnel. Hook. Hold. Click. Convert. Each step has one metric. Hook rate is 3 second plays over impressions. Hold rate is ThruPlays over 3 second plays. Then CTR. Then conversion rate.

The first step that breaks is the problem. A low hook rate means a new opening, same body. A good hook with bad hold means the middle does not pay off the promise. Good hold with low CTR is an offer problem. Good CTR with weak conversion is the landing page, and the creative is fine.

I judge every ad against the account's own median, not an industry benchmark. Benchmarks vary too much by vertical to be useful.

When I have the video, I pull frames from the first 3 seconds and name the hook type. Over time that builds a record of which openings work for which audience.

## What it gives you

A ranked table with the problem stage for every ad. Why the winners win. One test for each big loser. Three next creative tests.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/funnel.py --export samples/meta-ad-level-export.csv
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Assumptions to confirm

ThruPlays as the hold metric. Some buyers prefer 50% or 75% watch rate. The 1,000 impression minimum is a starting point.
