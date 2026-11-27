"""Week-over-week math for weekly-wow-check. Python 3.9+, standard library only.

Usage:
  python3 wow.py --export EXPORT.csv --platform meta --account client-a [--store paid-social-data] [--end YYYY-MM-DD] [--days 7] [--min-spend 50]
  python3 wow.py --platform meta --account client-a [--store paid-social-data]   # read daily-metrics.csv only

Monday: leave --end empty (defaults to last Sunday) for last week vs the week before.
Friday: pass --end as yesterday and --days 4 for this week so far vs the same days last week.

With --export, rows are also saved to the daily_metrics table in the local database (re-pulled days replace old rows).
Prints JSON with account totals, per-ad metrics and flags. The agent writes the Slack message from it.
"""
import argparse
import csv
import os
import datetime as dt
import json
import pathlib
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, select, upsert  # noqa: E402

ALIASES = {
    "date": ["Day", "Date", "Reporting starts", "date"],
    "campaign": ["Campaign name", "Campaign"], "ad_set": ["Ad set name", "Ad group name"], "ad": ["Ad name", "Ad"],
    "spend": ["Amount spent (USD)", "Amount spent", "Spend", "Cost"], "impressions": ["Impressions"],
    "reach": ["Reach"], "link_clicks": ["Link clicks", "Clicks", "Clicks (all)"], "results": ["Results", "Conversions"],
    "frequency": ["Frequency"], "video_3s_plays": ["3-second video plays", "3-second video plays (all)"], "thruplays": ["ThruPlays"],
    "revenue": ["Purchases conversion value", "Conversion value", "Revenue"],
}
FIELDS = ["date", "platform", "account_label", "campaign", "ad_set", "ad", "spend", "impressions", "reach",
          "link_clicks", "results", "result_type", "revenue", "frequency", "video_3s_plays", "thruplays"]


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", "").strip() or 0)
    except ValueError:
        return 0.0


def pick(r, f):
    for n in ALIASES.get(f, [f]):
        if n in r and str(r[n]).strip():
            return str(r[n]).strip()
    return ""


def load_export(path, platform, account):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        out = []
        for r in csv.DictReader(fh):
            row = {f: pick(r, f) for f in ALIASES}
            if not row["date"]:
                sys.exit("Export needs a daily Day/Date column (break the export down by day).")
            row.update(platform=platform, account_label=account)
            out.append(row)
    return out


def merge_store(store, rows):
    db = connect(store)
    upsert(db, "daily_metrics", rows)
    return select(db, "daily_metrics")


def metrics(rows):
    s = {f: sum(num(r.get(f)) for r in rows) for f in ["spend", "impressions", "reach", "link_clicks", "results", "revenue"]}
    freq_w = sum(num(r.get("frequency")) * num(r.get("spend")) for r in rows)
    m = {"spend": round(s["spend"], 2), "results": s["results"]}
    m["cost_per_result"] = round(s["spend"] / s["results"], 2) if s["results"] else None
    m["cpc"] = round(s["spend"] / s["link_clicks"], 2) if s["link_clicks"] else None
    m["ctr_pct"] = round(100 * s["link_clicks"] / s["impressions"], 3) if s["impressions"] else None
    if s["reach"]:
        m["frequency"], m["frequency_method"] = round(s["impressions"] / s["reach"], 2), "impressions/reach"
    else:
        m["frequency"], m["frequency_method"] = (round(freq_w / s["spend"], 2) if s["spend"] else None), "spend-weighted average"
    m["roas"] = round(s["revenue"] / s["spend"], 2) if s["revenue"] and s["spend"] else None
    return m


def pct(a, b):
    return None if a is None or b in (None, 0) else round(100 * (a - b) / b, 1)


def compare(lw, pw):
    out = {"this": lw, "prior": pw, "change_pct": {}}
    for k in ["spend", "results", "cost_per_result", "cpc", "frequency", "roas"]:
        out["change_pct"][k] = pct(lw.get(k), pw.get(k))
    out["change_pct"]["ctr_pts"] = None if lw["ctr_pct"] is None or pw["ctr_pct"] is None else round(lw["ctr_pct"] - pw["ctr_pct"], 3)
    out["change_pct"]["ctr_rel"] = pct(lw["ctr_pct"], pw["ctr_pct"])
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--export"); p.add_argument("--platform", required=True)
    p.add_argument("--account", required=True, help="your own label, never an ad account ID")
    p.add_argument("--store", default="paid-social-data"); p.add_argument("--end")
    p.add_argument("--days", type=int, default=7); p.add_argument("--min-spend", type=float, default=50)
    p.add_argument("--target-cpr", type=float)
    a = p.parse_args()

    if a.export:
        rows = merge_store(a.store, load_export(a.export, a.platform, a.account))
    else:
        rows = select(connect(a.store), "daily_metrics")
        if not rows:
            sys.exit("No export given and the local database has no daily_metrics rows yet.")
    rows = [r for r in rows if r["platform"] == a.platform and r["account_label"] == a.account]

    if a.end:
        end = dt.date.fromisoformat(a.end)
    else:
        t = dt.date.today()
        end = t - dt.timedelta(days=t.weekday() + 1)  # last Sunday
    lw_start = end - dt.timedelta(days=a.days - 1)
    pw_end, pw_start = end - dt.timedelta(days=7), lw_start - dt.timedelta(days=7)
    in_range = lambda r, s, e: s <= dt.date.fromisoformat(r["date"][:10]) <= e
    lw = [r for r in rows if in_range(r, lw_start, end)]
    pw = [r for r in rows if in_range(r, pw_start, pw_end)]
    if not lw or not pw:
        sys.exit(f"Missing data: {len(lw)} rows for {lw_start}..{end}, {len(pw)} rows for {pw_start}..{pw_end}.")

    result = {"periods": {"this": [str(lw_start), str(end)], "prior": [str(pw_start), str(pw_end)]},
              "account": compare(metrics(lw), metrics(pw)), "ads": [], "skipped_low_spend": 0, "flags": []}
    acct_spend = result["account"]["this"]["spend"] or 1
    acct_spend_pw = result["account"]["prior"]["spend"] or 1
    ads = sorted({(r["campaign"], r["ad_set"], r["ad"]) for r in lw + pw})
    for k in ads:
        l = [r for r in lw if (r["campaign"], r["ad_set"], r["ad"]) == k]
        q = [r for r in pw if (r["campaign"], r["ad_set"], r["ad"]) == k]
        ml, mp = metrics(l), metrics(q)
        if ml["spend"] < a.min_spend and mp["spend"] < a.min_spend:
            result["skipped_low_spend"] += 1
            continue
        c = compare(ml, mp)
        c.update(campaign=k[0], ad_set=k[1], ad=k[2],
                 spend_share_change_pts=round(100 * (ml["spend"] / acct_spend - mp["spend"] / acct_spend_pw), 1))
        result["ads"].append(c)

    def flag(obj, kind, detail):
        result["flags"].append({"object": obj, "type": kind, "detail": detail})

    cpr_changes = [x["change_pct"]["cost_per_result"] for x in result["ads"] if x["change_pct"]["cost_per_result"] is not None]
    mean = statistics.mean(cpr_changes) if len(cpr_changes) > 2 else None
    sd = statistics.pstdev(cpr_changes) if len(cpr_changes) > 2 else None
    for x in [result["account"] | {"campaign": "ACCOUNT", "ad_set": "", "ad": ""}] + result["ads"]:
        name = " / ".join(v for v in [x["campaign"], x["ad_set"], x["ad"]] if v)
        ch, th = x["change_pct"], x["this"]
        if ch["cost_per_result"] is not None and ch["cost_per_result"] > 20:
            flag(name, "cost_per_result_up", ch["cost_per_result"])
        if a.target_cpr and th["cost_per_result"] and th["cost_per_result"] > a.target_cpr:
            flag(name, "above_target", th["cost_per_result"])
        if th["frequency"] and th["frequency"] > 3 and (ch["frequency"] or 0) > 0 and (ch["ctr_rel"] or 0) < -15:
            flag(name, "creative_fatigue", {"frequency": th["frequency"], "ctr_change_pct": ch["ctr_rel"]})
        if (ch["cpc"] or 0) > 25 and abs(ch["ctr_rel"] or 0) <= 10:
            flag(name, "cpc_spike_auction", ch["cpc"])
        if abs(x.get("spend_share_change_pts", 0)) > 10:
            flag(name, "spend_shift", x["spend_share_change_pts"])
        if sd and name != "ACCOUNT" and ch["cost_per_result"] is not None and abs(ch["cost_per_result"] - mean) > 2 * sd:
            flag(name, "outlier_good" if ch["cost_per_result"] < mean else "outlier_bad", ch["cost_per_result"])
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
