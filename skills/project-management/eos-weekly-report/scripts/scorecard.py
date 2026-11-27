"""Scorecard numbers and change impact for eos-weekly-report. Python 3.9+, standard library only.

Usage:
  python3 scorecard.py --export daily.csv --goals goals.json [--history history.csv] [--crm crm.csv] [--end 2026-11-22]

--goals    JSON list: [{"measurable": "Cost per result", "metric": "cost_per_result", "goal": 25, "better": "lower", "owner": "Connor"}]
           metric is one of: spend, results, cost_per_result, revenue, roas, ctr_pct, cpc, frequency, crm:<column>
--history  history.csv from paid-social-work-log; used for the changes and impact section
--crm      optional daily CRM or analytics export with a Date/Day column and numeric columns (for crm:<column>)
Week is Monday to Sunday ending on --end (default: last Sunday). Prints JSON.
"""
import argparse, csv, os, datetime as dt, json, pathlib, sys
from collections import defaultdict


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, select  # noqa: E402


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", "").strip() or 0)
    except ValueError:
        return 0.0


def col(r, *names):
    for n in names:
        if n in r and str(r[n]).strip():
            return r[n]
    return ""


def read(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8-sig"))) if path and pathlib.Path(path).exists() else []


def metrics(rows):
    t = defaultdict(float)
    for r in rows:
        t["spend"] += num(col(r, "Amount spent", "spend")); t["results"] += num(col(r, "Results", "results"))
        t["revenue"] += num(col(r, "Purchases conversion value", "revenue")); t["impressions"] += num(col(r, "Impressions", "impressions"))
        t["clicks"] += num(col(r, "Link clicks", "link_clicks")); t["reach"] += num(col(r, "Reach", "reach"))
    m = {"spend": round(t["spend"], 2), "results": t["results"], "revenue": round(t["revenue"], 2)}
    m["cost_per_result"] = round(t["spend"] / t["results"], 2) if t["results"] else None
    m["roas"] = round(t["revenue"] / t["spend"], 2) if t["spend"] and t["revenue"] else None
    m["ctr_pct"] = round(100 * t["clicks"] / t["impressions"], 3) if t["impressions"] else None
    m["cpc"] = round(t["spend"] / t["clicks"], 2) if t["clicks"] else None
    m["frequency"] = round(t["impressions"] / t["reach"], 2) if t["reach"] else None
    return m


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--export"); p.add_argument("--store", default="paid-social-data"); p.add_argument("--platform", default="meta"); p.add_argument("--account"); p.add_argument("--goals", required=True)
    p.add_argument("--history"); p.add_argument("--crm"); p.add_argument("--end")
    a = p.parse_args()
    if a.export:
        rows = read(a.export)
    else:
        db = connect(a.store)
        rows = select(db, "daily_metrics", "platform=? AND account_label=?", (a.platform, a.account))
        if not a.history:
            a.history_rows = select(db, "history", "account_label=?", (a.account,))
    if not rows:
        sys.exit("No rows in export.")
    day = lambda r: dt.date.fromisoformat(col(r, "Day", "Date", "date")[:10])
    t = dt.date.today()
    end = dt.date.fromisoformat(a.end) if a.end else t - dt.timedelta(days=t.weekday() + 1)
    start, pend, pstart = end - dt.timedelta(6), end - dt.timedelta(7), end - dt.timedelta(13)
    within = lambda rs, s, e: [r for r in rs if s <= day(r) <= e]
    this, prior = metrics(within(rows, start, end)), metrics(within(rows, pstart, pend))
    crm = read(a.crm)
    for m, s, e in [(this, start, end), (prior, pstart, pend)]:
        for r in within(crm, s, e):
            for k, v in r.items():
                if k not in ("Day", "Date", "date"):
                    m[f"crm:{k}"] = round(m.get(f"crm:{k}", 0) + num(v), 2)

    score = []
    for g in json.load(open(a.goals)):
        v, lv = this.get(g["metric"]), prior.get(g["metric"])
        ok = None if v is None else (v <= g["goal"] if g.get("better", "higher") == "lower" else v >= g["goal"])
        score.append({"measurable": g["measurable"], "owner": g.get("owner", ""), "goal": g["goal"], "this_week": v,
                      "last_week": lv, "status": "Not available" if ok is None else ("On track" if ok else "Off track")})

    impact = []
    groups = defaultdict(list)
    for h in (getattr(a, "history_rows", None) or read(a.history)):
        d = dt.date.fromisoformat(h["date"][:10])
        if start <= d <= end:
            groups[(h["date"][:10], h["campaign"])].append(h)
    data_end = max(day(r) for r in rows)
    for (d, camp), hs in sorted(groups.items()):
        d0 = dt.date.fromisoformat(d)
        camp_rows = [r for r in rows if col(r, "Campaign name", "campaign") == camp]
        before = metrics(within(camp_rows, d0 - dt.timedelta(7), d0 - dt.timedelta(1)))
        after_end = min(data_end, d0 + dt.timedelta(7))
        after = metrics(within(camp_rows, d0 + dt.timedelta(1), after_end))
        days_after = (after_end - d0).days
        impact.append({"date": d, "campaign": camp,
                       "changes": [f'{h["change_type"]} {h.get("ad_set","")} {h.get("ad","")}: {h["old_value"] or "-"} -> {h["new_value"] or "-"} (why: {h["why"]})'.replace("  ", " ") for h in hs],
                       "days_after": days_after, "too_early": days_after < 3,
                       "before_7d": {k: before[k] for k in ("spend", "results", "cost_per_result")},
                       "after": {k: after[k] for k in ("spend", "results", "cost_per_result")}})
    print(json.dumps({"week": [str(start), str(end)], "this_week": this, "last_week": prior,
                      "scorecard": score, "changes_and_impact": impact,
                      "note": "Effects listed are what moved after a change, not proof the change caused it."}, indent=1))


if __name__ == "__main__":
    main()
