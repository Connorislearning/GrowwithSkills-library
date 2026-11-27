# EOS weekly report

Paid media results in the format leadership teams that run on EOS already use every week.

## The problem

Many small companies run their week on EOS. Their weekly Level 10 meeting has a scorecard, rocks and an issues list. Paid media usually shows up as a screenshot or a separate deck, so it does not fit the meeting and the problems never reach the issues list.

## My process

I build the paid media section to match the meeting. The scorecard has 5 to 10 numbers, each with an owner and a weekly goal, and each is simply on track or off track. No commentary in the scorecard.

Anything off track goes straight onto the issues list, worded as a problem, not a fix. The meeting solves it. That keeps the report short and makes sure a bad number turns into a decision.

The part people value most is the changes and impact section. Because I log every change daily, the report lists what I actually did that week, grouped into a few actions, and shows what moved afterward in the ad account and in the CRM. Nobody has to remember fifty changes from Monday.

Rocks get one line of evidence each, pulled from the data or my daily work log. Headlines cover the few things people should know. Last week's to-dos get marked done or not done, so follow-through is visible.

The doc is built straight in Google Docs when a connector is available.

## What it gives you

A one to two page Google Doc: scorecard, rock review, headlines, to-dos and a ranked issues list.

## Works with

Any agent that reads Agent Skills. Best with a Google Drive or Docs connector. Without one, you get a .docx or text to paste.

## Try it

The files in `samples/` are made-up sample data, not from any real account. Run this from the skill's folder (Python 3.9 or later, nothing to install):

```
python3 scripts/scorecard.py --export samples/meta-daily-export.csv --goals samples/goals.json --history samples/history.csv --crm samples/crm-daily.csv --end 2026-11-22
```

With your own data, use your own export, or let your AI agent run the script for you. Your data is saved in `paid-social-data/` on your machine and never leaves it.

## Assumptions to confirm

The default layout uses the standard EOS Level 10 sections. Share your own EOS template and the skill will follow it.

Source for the meeting format: EOS Worldwide, [What Is a Level 10 Meeting?](https://www.eosworldwide.com/level-10-meeting), and Gino Wickman, *Traction*.
