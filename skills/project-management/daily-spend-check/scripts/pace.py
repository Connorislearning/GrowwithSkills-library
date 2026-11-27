"""Intraday spend pacing for daily-spend-check. Python 3.9+, standard library only.

Usage:
  python3 pace.py --today today-so-far.csv --hour 14 [--history hourly-spend-history.csv] [--must-spend]

--today    one row per campaign (or ad set): Campaign name, Daily budget, Amount spent (so far today)
--hour     hours of the account's day already finished (14 means 00:00-14:00 is in the numbers)
--history  hourly spend rows (Day, Hour, Campaign name, Amount spent) for the same weekday in past weeks.
           Without it, a straight line through the day is used.
Prints JSON: per-campaign pace, projection and flags. Thresholds are defaults you can change.
"""
import argparse, csv, json, sys
from collections import defaultdict


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


def curve_from_history(path):
    by = defaultdict(lambda: defaultdict(float))  # campaign -> hour -> spend
    acct = defaultdict(float)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            h, c, s = int(num(col(r, "Hour", "Hour of day"))), col(r, "Campaign name", "Campaign"), num(col(r, "Amount spent", "Spend"))
            by[c][h] += s
            acct[h] += s
    def cum(d):
        tot = sum(d.values()) or 1
        out, run = [], 0.0
        for h in range(24):
            run += d.get(h, 0)
            out.append(run / tot)
        return out
    return {c: cum(d) for c, d in by.items()}, cum(acct), {c: dict(d) for c, d in by.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--today", required=True); p.add_argument("--hour", type=int, required=True)
    p.add_argument("--history"); p.add_argument("--must-spend", action="store_true")
    p.add_argument("--under", type=float, default=80); p.add_argument("--over", type=float, default=125)
    p.add_argument("--off-trend", type=float, default=30)
    a = p.parse_args()
    if not 0 < a.hour <= 24:
        sys.exit("--hour must be 1 to 24")
    curves, acct_curve, hourly = ({}, None, {}) if not a.history else curve_from_history(a.history)
    straight = lambda h: h / 24
    out = {"hour": a.hour, "curve": "historical" if a.history else "straight line (assumed)", "campaigns": [], "flags": []}
    tot_b = tot_s = tot_e = 0.0
    with open(a.today, newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            c = col(r, "Campaign name", "Campaign", "Ad set name")
            b, s = num(col(r, "Daily budget", "Budget", "Ad set budget")), num(col(r, "Amount spent", "Spend"))
            share = curves[c][a.hour - 1] if c in curves else straight(a.hour)
            exp = b * share
            row = {"campaign": c, "daily_budget": b, "spent": round(s, 2), "expected_now": round(exp, 2),
                   "share_of_day_expected": round(share, 3),
                   "pace_pct": round(100 * s / exp, 1) if exp else None,
                   "projected_end_of_day": round(s / share, 2) if share else None}
            row["gap_dollars"] = round((row["projected_end_of_day"] or 0) - b, 2)
            out["campaigns"].append(row)
            tot_b += b; tot_s += s; tot_e += exp
            if share < 0.10:
                continue
            if row["pace_pct"] is not None and row["pace_pct"] < a.under:
                out["flags"].append({"campaign": c, "type": "underpacing", "severity": "red" if a.must_spend else "yellow", "pace_pct": row["pace_pct"]})
            if row["pace_pct"] is not None and row["pace_pct"] > a.over:
                out["flags"].append({"campaign": c, "type": "overpacing", "severity": "yellow", "pace_pct": row["pace_pct"]})
            if c in hourly and s == 0 and sum(hourly[c].get(h, 0) for h in (a.hour - 2, a.hour - 1)) > 0:
                out["flags"].append({"campaign": c, "type": "stalled", "severity": "red"})
    out["account"] = {"daily_budget": tot_b, "spent": round(tot_s, 2), "expected_now": round(tot_e, 2),
                      "pace_pct": round(100 * tot_s / tot_e, 1) if tot_e else None}
    if out["account"]["pace_pct"] is not None and abs(out["account"]["pace_pct"] - 100) > a.off_trend:
        out["flags"].append({"campaign": "ACCOUNT", "type": "off_trend", "severity": "yellow", "pace_pct": out["account"]["pace_pct"]})
    out["campaigns"].sort(key=lambda r: abs(r["gap_dollars"]), reverse=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
