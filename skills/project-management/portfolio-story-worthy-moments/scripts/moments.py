"""Find story-worthy moments in saved paid social history. Python 3.9+, standard library only.

Usage:
  python3 moments.py --export daily.csv --platform meta --account client-a [--history history.csv] [--moments moments.csv] [--end 2026-11-22]
  python3 moments.py --store paid-social-data --platform meta --account client-a [--save]   # reads the local database

Works in full weeks (Monday to Sunday) ending on --end (default: last Sunday).
Detects: record week, turnaround, efficient scale, breakout creative. Each moment lists the logged changes
from the 14 days before it. It never invents a cause: no logged change means "cause not logged".
Prints JSON. The agent writes the stories from it.
"""
import argparse, csv, os, datetime as dt, json, pathlib, statistics, sys
from collections import defaultdict


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, select, upsert  # noqa: E402


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
    p = pathlib.Path(path)
    return list(csv.DictReader(p.open(newline="", encoding="utf-8-sig"))) if p.exists() else []


def week_start(d):
    return d - dt.timedelta(days=d.weekday())


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--export"); p.add_argument("--store"); p.add_argument("--history"); p.add_argument("--moments")
    p.add_argument("--platform", required=True); p.add_argument("--account", required=True)
    p.add_argument("--end"); p.add_argument("--min-spend", type=float, default=500)
    p.add_argument("--min-history-days", type=int, default=14)
    p.add_argument("--save", action="store_true", help="record new moments in the database (public_ready = no)")
    a = p.parse_args()
    if a.store:
        db = connect(a.store)
        rows = select(db, "daily_metrics", "platform=? AND account_label=?", (a.platform, a.account))
        hist = select(db, "history", "account_label=?", (a.account,))
        seen = select(db, "moments", "account_label=?", (a.account,))
    elif a.export:
        rows, hist, seen = read(a.export), read(a.history) if a.history else [], read(a.moments) if a.moments else []
    else:
        sys.exit("Pass --export or --store.")
    if not rows:
        sys.exit("No data.")

    end = dt.date.fromisoformat(a.end) if a.end else week_start(dt.date.today()) - dt.timedelta(days=1)
    acct = defaultdict(lambda: [0.0, 0.0, 0.0])   # week -> spend, results, revenue
    ad = defaultdict(lambda: [0.0, 0.0])          # (week, ad) -> spend, results
    days = set()
    for r in rows:
        d = dt.date.fromisoformat(col(r, "Day", "date", "Date")[:10])
        if d > end:
            continue
        days.add(d)
        w = week_start(d)
        sp, res, rev = num(col(r, "Amount spent", "spend")), num(col(r, "Results", "results")), num(col(r, "Purchases conversion value", "revenue"))
        acct[w][0] += sp; acct[w][1] += res; acct[w][2] += rev
        name = " / ".join(x for x in [col(r, "Campaign name", "campaign"), col(r, "Ad set name", "ad_set"), col(r, "Ad name", "ad")] if x)
        ad[(w, name)][0] += sp; ad[(w, name)][1] += res
    if len(days) < a.min_history_days:
        sys.exit(f"Only {len(days)} days of history; need {a.min_history_days}.")
    weeks = sorted(w for w in acct if w + dt.timedelta(days=6) <= end)
    if len(weeks) < 3:
        sys.exit("Need at least 3 full weeks.")
    cur, prev, prev2 = weeks[-1], weeks[-2], weeks[-3]
    cpr = lambda w: acct[w][0] / acct[w][1] if acct[w][1] else None
    roas = lambda w: acct[w][2] / acct[w][0] if acct[w][0] and acct[w][2] else None
    found = []

    def add(kind, metric, before, after, period, detail=None):
        found.append({"moment_type": kind, "metric": metric, "before": before, "after": after,
                      "change_pct": round(100 * (after - before) / before, 1) if before else None,
                      "period": period, "detail": detail or {}})

    if acct[cur][0] >= a.min_spend:
        past = [w for w in weeks[:-1] if acct[w][0] >= a.min_spend]
        if past and cpr(cur) and all(cpr(w) is None or cpr(cur) < cpr(w) for w in past):
            best = min(cpr(w) for w in past if cpr(w))
            add("record", "cost_per_result", round(best, 2), round(cpr(cur), 2), [str(cur), str(cur + dt.timedelta(6))], {"weeks_compared": len(past)})
        if past and roas(cur) and all(roas(w) is None or roas(cur) > roas(w) for w in past):
            add("record", "roas", round(max(roas(w) or 0 for w in past), 2), round(roas(cur), 2), [str(cur), str(cur + dt.timedelta(6))])
        if past and all(acct[cur][1] > acct[w][1] for w in past):
            add("record", "results", max(acct[w][1] for w in past), acct[cur][1], [str(cur), str(cur + dt.timedelta(6))])
        base = weeks[-5] if len(weeks) >= 5 else prev2
        if cpr(base) and cpr(prev) and cpr(cur) and acct[cur][0] >= 0.9 * acct[base][0]:
            if cpr(prev) <= 0.75 * cpr(base) and cpr(cur) <= 0.75 * cpr(base):
                add("turnaround", "cost_per_result", round(cpr(base), 2), round(cpr(cur), 2), [str(base), str(cur + dt.timedelta(6))])
        if acct[base][0] and acct[cur][0] >= 1.5 * acct[base][0] and cpr(base) and cpr(cur) and cpr(cur) <= 1.1 * cpr(base):
            add("efficient_scale", "spend", round(acct[base][0], 2), round(acct[cur][0], 2), [str(base), str(cur + dt.timedelta(6))],
                {"cost_per_result_before": round(cpr(base), 2), "cost_per_result_after": round(cpr(cur), 2)})
        ad_cprs = {n: v[0] / v[1] for (w, n), v in ad.items() if w == cur and v[1]}
        if len(ad_cprs) >= 3:
            med = statistics.median(ad_cprs.values())
            for n, c in ad_cprs.items():
                if c <= 0.5 * med and ad[(cur, n)][0] >= 0.10 * acct[cur][0]:
                    add("breakout_creative", "cost_per_result", round(med, 2), round(c, 2), [str(cur), str(cur + dt.timedelta(6))],
                        {"ad": n, "spend_share_pct": round(100 * ad[(cur, n)][0] / acct[cur][0], 1)})

    old = {(m.get("account_label"), m.get("moment_type"), m.get("metric"), m.get("period")) for m in seen}
    out = []
    for m in found:
        key = (a.account, m["moment_type"], m["metric"], " to ".join(m["period"]))
        if key in old:
            continue
        s = dt.date.fromisoformat(m["period"][0])
        m["linked_changes"] = [
            {k: h.get(k, "") for k in ["date", "campaign", "ad_set", "ad", "change_type", "old_value", "new_value", "why"]}
            for h in hist
            if h.get("account_label", a.account) == a.account and h.get("date")
            and s - dt.timedelta(days=14) <= dt.date.fromisoformat(h["date"][:10]) <= dt.date.fromisoformat(m["period"][1])
        ] or "cause not logged"
        m.update(account_label=a.account, platform=a.platform, period=" to ".join(m["period"]))
        out.append(m)
    if a.save and a.store:
        upsert(connect(a.store), "moments", [dict(m, date_found=str(dt.date.today()), linked_changes=json.dumps(m["linked_changes"]),
                                                  public_ready="no") for m in out])
    print(json.dumps({"scanned_through": str(end), "weeks_of_history": len(weeks), "new_moments": out}, indent=1))


if __name__ == "__main__":
    main()
