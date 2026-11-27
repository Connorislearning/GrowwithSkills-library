"""Hook, hold, click and convert math for video-creative-analysis. Python 3.9+, standard library only.

Usage:
  python3 funnel.py --export ad-level.csv [--min-impressions 1000] [--hold thruplays|p50|p75] [--target-cpa 30]
  python3 funnel.py --store paid-social-data --platform meta --account client-a [--since 2026-10-28]

Each ad is judged against the account median, not a benchmark. The problem stage is the first stage
clearly below median (default: more than 15% below). Prints JSON; the agent writes the diagnosis and tests.
Frames for the first 3 seconds of a video can be pulled with ffmpeg, for example:
  ffmpeg -i ad.mp4 -vf "select='eq(n,0)+gte(t,1)*lt(t,1.04)+gte(t,2)*lt(t,2.04)+gte(t,3)*lt(t,3.04)'" -vsync vfr frame_%d.png
"""
import argparse, csv, json, os, statistics, sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, select  # noqa: E402

COLS = {"ad": ["Ad name", "ad"], "spend": ["Amount spent", "spend"], "impressions": ["Impressions", "impressions"],
        "plays3": ["3-second video plays", "video_3s_plays"], "thruplays": ["ThruPlays", "thruplays"],
        "p50": ["Video plays at 50%"], "p75": ["Video plays at 75%"],
        "clicks": ["Link clicks", "link_clicks"], "results": ["Results", "results"]}


def num(x):
    try:
        return float(str(x).replace(",", "").replace("$", "").strip() or 0)
    except ValueError:
        return 0.0


def get(r, k):
    for n in COLS[k]:
        if n in r and str(r[n]).strip():
            return r[n]
    return ""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--export"); p.add_argument("--store", default="paid-social-data")
    p.add_argument("--platform", default="meta"); p.add_argument("--account"); p.add_argument("--since", default="")
    p.add_argument("--min-impressions", type=float, default=1000); p.add_argument("--hold", default="thruplays", choices=["thruplays", "p50", "p75"])
    p.add_argument("--gap", type=float, default=15); p.add_argument("--target-cpa", type=float)
    a = p.parse_args()
    if a.export:
        src = list(csv.DictReader(open(a.export, newline="", encoding="utf-8-sig")))
    elif a.account:
        src = select(connect(a.store), "daily_metrics", "platform=? AND account_label=? AND date>=?", (a.platform, a.account, a.since))
    else:
        sys.exit("Pass --export, or --account to read the local database.")
    tot = defaultdict(lambda: defaultdict(float))
    for r in src:
        t = tot[get(r, "ad")]
        for k in COLS:
            if k != "ad":
                t[k] += num(get(r, k))
    ads, skipped = [], 0
    for name, t in tot.items():
        if t["impressions"] < a.min_impressions:
            skipped += 1; continue
        hold_n = t[a.hold]
        ads.append({"ad": name, "spend": round(t["spend"], 2), "impressions": int(t["impressions"]),
                    "hook_rate": t["plays3"] / t["impressions"] if t["impressions"] else None,
                    "hold_rate": hold_n / t["plays3"] if t["plays3"] else None,
                    "ctr": t["clicks"] / t["impressions"] if t["impressions"] else None,
                    "cvr": t["results"] / t["clicks"] if t["clicks"] else None,
                    "cpa": round(t["spend"] / t["results"], 2) if t["results"] else None, "results": t["results"]})
    if not ads:
        sys.exit("No ads above the impression minimum.")
    med = {k: statistics.median([x[k] for x in ads if x[k] is not None]) for k in ["hook_rate", "hold_rate", "ctr", "cvr"]
           if any(x[k] is not None for x in ads)}
    stage_names = {"hook_rate": "hook", "hold_rate": "body (hold)", "ctr": "offer (click)", "cvr": "landing (convert)"}
    for x in ads:
        x["problem_stage"] = "none"
        for k in ["hook_rate", "hold_rate", "ctr", "cvr"]:
            if k in med and x[k] is not None and x[k] < med[k] * (1 - a.gap / 100):
                x["problem_stage"] = stage_names[k]; break
        for k in ["hook_rate", "hold_rate", "ctr", "cvr"]:
            if x[k] is not None:
                x[k] = round(100 * x[k], 2)
        x["small_sample"] = x["results"] < 20
    ads.sort(key=lambda x: x["spend"], reverse=True)
    cpas = [x["cpa"] for x in ads if x["cpa"]]
    med_cpa = statistics.median(cpas) if cpas else None
    bar = a.target_cpa or med_cpa
    print(json.dumps({"hold_metric": a.hold, "medians_pct": {stage_names[k]: round(100 * v, 2) for k, v in med.items()},
                      "median_cpa": med_cpa, "skipped_low_impressions": skipped, "ads": ads,
                      "winners": [x["ad"] for x in sorted([x for x in ads if x["cpa"] and x["cpa"] <= bar], key=lambda x: x["cpa"])[:3]],
                      "losing_spenders": [x["ad"] for x in ads if x["cpa"] is None or x["cpa"] > bar][:3]}, indent=1))


if __name__ == "__main__":
    main()
