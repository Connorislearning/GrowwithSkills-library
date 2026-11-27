"""Quarter (or month) pacing math for qoq-pacing. Python 3.9+, standard library only.

Usage:
  python3 pacing.py --export daily.csv --budget 90000 --volume-goal 1400 [--revenue-goal 95000]
                    [--start 2026-10-01 --end 2026-12-31] [--today 2026-11-27] [--target-cpr 60] [--target-roas 1.1]

Default period is the calendar quarter containing --today (default: today). Pass --start/--end for a month.
"Today" counts as not yet elapsed, so the data should run through yesterday.
The export needs daily rows: Day, Amount spent, Results, and optionally a revenue column.
Prints JSON with the scorecard, quarter-over-quarter comparison at the same day number, and flags.
"""
import argparse, csv, os, datetime as dt, json, sys

REV = ["Purchases conversion value", "Conversion value", "Revenue", "revenue"]


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, select  # noqa: E402


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", "").strip() or 0)
    except ValueError:
        return 0.0


def col(r, names):
    for n in names:
        if n in r and str(r[n]).strip():
            return r[n]
    return ""


def quarter_bounds(d):
    q0 = 3 * ((d.month - 1) // 3) + 1
    s = dt.date(d.year, q0, 1)
    e = (dt.date(d.year + (q0 + 3 > 12), (q0 + 3 - 1) % 12 + 1, 1)) - dt.timedelta(days=1)
    return s, e


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--export"); p.add_argument("--store", default="paid-social-data"); p.add_argument("--platform", default="meta"); p.add_argument("--account")
    p.add_argument("--budget", type=float, required=True)
    p.add_argument("--volume-goal", type=float, required=True); p.add_argument("--revenue-goal", type=float)
    p.add_argument("--start"); p.add_argument("--end"); p.add_argument("--today")
    p.add_argument("--target-cpr", type=float); p.add_argument("--target-roas", type=float)
    a = p.parse_args()
    if not a.export and not a.account:
        sys.exit("Pass --export, or --account to read the local database.")
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    if a.start and a.end:
        start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    else:
        start, end = quarter_bounds(today)
    D = (end - start).days + 1
    d = max(0, min(D, (today - start).days))
    if d == 0:
        sys.exit("No days elapsed yet in this period.")
    left = D - d

    daily = {}
    if a.export:
        src = list(csv.DictReader(open(a.export, newline="", encoding="utf-8-sig")))
    else:
        src = select(connect(a.store), "daily_metrics", "platform=? AND account_label=?", (a.platform, a.account))
    if True:
        for r in src:
            day = dt.date.fromisoformat(col(r, ["Day", "Date", "date"])[:10])
            x = daily.setdefault(day, [0.0, 0.0, 0.0])
            x[0] += num(col(r, ["Amount spent", "Amount spent (USD)", "Spend", "spend"]))
            x[1] += num(col(r, ["Results", "results", "Conversions"]))
            x[2] += num(col(r, REV))

    def total(s, e):
        t = [0.0, 0.0, 0.0]
        for k, v in daily.items():
            if s <= k <= e:
                t = [t[i] + v[i] for i in range(3)]
        return t

    last_day = start + dt.timedelta(days=d - 1)
    spend, results, revenue = total(start, last_day)
    r7s = max(start, last_day - dt.timedelta(days=6))
    s7, res7, rev7 = total(r7s, last_day)
    n7 = (last_day - r7s).days + 1
    run_rate = s7 / n7
    cpr7 = s7 / res7 if res7 else None
    roas7 = rev7 / s7 if s7 else None

    target_cpr = a.target_cpr or a.budget / a.volume_goal
    target_roas = a.target_roas or (a.revenue_goal / a.budget if a.revenue_goal else None)
    exp_spend = a.budget * d / D
    proj_spend = spend + run_rate * left
    out = {
        "period": [str(start), str(end)], "days_elapsed": d, "days_total": D, "days_left": left,
        "targets": {"cost_per_result": round(target_cpr, 2), "cost_per_result_source": "user" if a.target_cpr else "budget / volume goal",
                    "roas": round(target_roas, 2) if target_roas else None},
        "scorecard": {
            "budget": a.budget, "spent": round(spend, 2), "expected_spend_to_date": round(exp_spend, 2),
            "pacing_pct": round(100 * spend / exp_spend, 1), "run_rate_7d": round(run_rate, 2),
            "projected_spend": round(proj_spend, 2),
            "required_daily_spend": round((a.budget - spend) / left, 2) if left else None,
            "results": results, "volume_goal": a.volume_goal,
            "volume_pacing_pct": round(100 * results / (a.volume_goal * d / D), 1),
            "projected_results": round(results + (run_rate / cpr7) * left) if cpr7 else None,
            "cost_per_result": round(spend / results, 2) if results else None,
            "cost_per_result_7d": round(cpr7, 2) if cpr7 else None,
        },
    }
    if a.revenue_goal or revenue:
        out["scorecard"].update(revenue=round(revenue, 2), revenue_goal=a.revenue_goal,
                                roas=round(revenue / spend, 2) if spend else None,
                                projected_revenue=round(revenue + run_rate * (roas7 or 0) * left, 2))
    if proj_spend > a.budget and run_rate:
        out["scorecard"]["budget_runs_out_on"] = str(last_day + dt.timedelta(days=int((a.budget - spend) / run_rate) + 1))

    # Same day number last period
    plen = D
    pstart = (quarter_bounds(start - dt.timedelta(days=1))[0]) if not (a.start and a.end) else start - dt.timedelta(days=plen)
    pend_same = pstart + dt.timedelta(days=d - 1)
    ps, pr, prv = total(pstart, pend_same)
    if ps:
        chg = lambda x, y: round(100 * (x - y) / y, 1) if y else None
        out["prior_same_day"] = {"period_start": str(pstart), "through": str(pend_same), "spent": round(ps, 2), "results": pr,
                                 "cost_per_result": round(ps / pr, 2) if pr else None, "revenue": round(prv, 2),
                                 "change_pct": {"spent": chg(spend, ps), "results": chg(results, pr),
                                                "cost_per_result": chg(spend / results if results else 0, ps / pr if pr else 0)}}
    else:
        out["prior_same_day"] = None

    sc, flags = out["scorecard"], []
    if sc["pacing_pct"] < 90: flags.append("underspending: check delivery before raising budgets")
    if sc["pacing_pct"] > 110: flags.append("overspending" + (f": budget runs out {sc.get('budget_runs_out_on')}" if sc.get("budget_runs_out_on") else ""))
    if sc["cost_per_result"] and sc["cost_per_result"] > 1.2 * target_cpr: flags.append("cost per result more than 20% above target: fix efficiency before adding spend")
    if sc["volume_pacing_pct"] < 90 and 90 <= sc["pacing_pct"] <= 110: flags.append("spend on pace but results behind")
    if left < 10 and abs(sc["pacing_pct"] - 100) > 15: flags.append(f"gap may not close: needs {sc['required_daily_spend']}/day vs run rate {sc['run_rate_7d']}")
    out["flags"] = flags
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
