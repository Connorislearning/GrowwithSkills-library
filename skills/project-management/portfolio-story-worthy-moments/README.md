# Portfolio story-worthy moments

Finds the results worth talking about in my own account history, and writes them up while I still remember why they happened.

## The problem

Media buyers do great work and lose the proof. Results live in Ads Manager, the access ends when the job or contract ends, and much of it is under NDA. A year later, "I cut CPA a lot for a skincare client" is all that is left, with no number and no reason.

## My process

My other skills save everything to one folder on my own machine: the daily work log, daily numbers, and every weekly and quarterly report. That folder is my history, and it survives even if I lose access to an ad account.

Every Friday this skill scans that history for six kinds of moments: an all-time best week, a turnaround, scaling spend without losing efficiency, a breakout creative, a quarter that hit its goal, and a problem caught and fixed fast.

For each one it checks the work log for what I changed in the two weeks before. That turns "CPA dropped" into "CPA dropped 40% after I moved budget to the new hook and cut the broad audience."

Then it writes the story twice. The private version keeps every exact number. The client-safe version uses a generic description, percentages instead of dollars, and nothing that identifies the client. I approve each one before it is marked ready to share. It also drafts a resume bullet and a LinkedIn post.

## What it gives you

A growing, private portfolio of results with causes, and approved client-safe versions ready for a resume, LinkedIn or an interview.

## Works with

Any agent that reads Agent Skills. Works best when the other skills in this library have been saving to the local data store. Without it, upload past exports and reports.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/moments.py --export samples/meta-daily-export.csv --history samples/history.csv --platform meta --account demo --end 2026-11-22
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Assumptions to confirm

The six moment types, the 14-day history minimum, the $500 spend minimum and the thresholds are starting points. Friday is the default run day.
