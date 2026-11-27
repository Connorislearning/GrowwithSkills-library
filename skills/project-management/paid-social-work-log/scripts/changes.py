"""What happened: collect today's ad account changes into the local database. Python 3.9+, standard library only.

Three ways in, in this order of preference:
  1. Meta Ads MCP (or any platform's MCP): the agent saves the activity log it returns as JSON, then
       python3 changes.py import-activity --file activity.json --platform meta --account client-a
  2. Meta Marketing API: python3 meta_api.py activities --account client-a   (calls import-activity for you)
  3. Manual export, any platform: save a daily ad-level export with status and budget columns, then
       python3 changes.py snapshot --export export.csv --platform meta --account client-a
       python3 changes.py diff --platform meta --account client-a
Then show the two tables (what happened, why) with:  python3 changes.py show
The script never fills in a reason. Reasons come only from the user, through history.py.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, select, upsert  # noqa: E402

NOT_GIVEN = "not given"
ALIASES = {
    "campaign": ["Campaign name", "Campaign", "campaign_name"],
    "ad_set": ["Ad set name", "Ad group name", "Ad group", "adset_name"],
    "ad": ["Ad name", "Ad", "ad_name"],
    "status": ["Delivery", "Status", "Ad delivery", "effective_status"],
    "budget": ["Ad set budget", "Campaign budget", "Budget", "Daily budget", "daily_budget"],
    "bid": ["Bid", "Bid amount", "Bid strategy", "bid_amount"],
    "date": ["Day", "Date", "Reporting starts"],
}


def pick(row, field):
    for n in ALIASES[field]:
        if n in row and str(row[n]).strip():
            return str(row[n]).strip()
    return ""


def cmd_snapshot(a, db):
    with open(a.export, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"No rows in {a.export}")
    date = a.date or pick(rows[-1], "date")[:10] or dt.date.today().isoformat()
    out, seen = [], set()
    for r in rows:
        s = {k: pick(r, k) for k in ["campaign", "ad_set", "ad", "status", "budget", "bid"]}
        if not s["campaign"] or (s["campaign"], s["ad_set"], s["ad"]) in seen:
            continue
        seen.add((s["campaign"], s["ad_set"], s["ad"]))
        s.update(date=date, platform=a.platform, account_label=a.account,
                 level="ad" if s["ad"] else ("ad_set" if s["ad_set"] else "campaign"))
        out.append(s)
    upsert(db, "snapshots", out)
    print(f"Saved snapshot for {date}: {len(out)} objects.")


def cmd_diff(a, db):
    dates = [r["date"] for r in db.execute("SELECT DISTINCT date FROM snapshots WHERE platform=? AND account_label=? ORDER BY date",
                                           (a.platform, a.account))]
    if len(dates) < 2:
        sys.exit(f"Need two snapshot days to compare; found {len(dates)}. The first day is the baseline.")
    d_old, d_new = dates[-2], dates[-1]
    get = lambda d: {(r["campaign"], r["ad_set"], r["ad"]): r for r in select(db, "snapshots", "platform=? AND account_label=? AND date=?", (a.platform, a.account, d))}
    old, new = get(d_old), get(d_new)
    rows, groups = [], set()

    def add(obj, ctype, ov, nv, level=None, ad=None):
        rows.append({"date": d_new, "time": "", "platform": a.platform, "account_label": a.account,
                     "level": level or obj["level"], "campaign": obj["campaign"], "ad_set": obj["ad_set"],
                     "ad": obj["ad"] if ad is None else ad, "change_type": ctype, "old_value": ov, "new_value": nv,
                     "why": "", "status": "pending", "source": f"snapshot {d_old} -> {d_new}"})

    for k, n in new.items():
        o = old.get(k)
        if o is None:
            add(n, "created", "", n["status"]); continue
        if o["status"] != n["status"]:
            add(n, "status", o["status"], n["status"])
        for f in ["budget", "bid"]:
            if o[f] != n[f] and (n["campaign"], n["ad_set"], f) not in groups:
                groups.add((n["campaign"], n["ad_set"], f))  # budgets repeat on every ad row; log once per ad set
                add(n, f, o[f], n[f], level="ad_set" if n["ad_set"] else "campaign", ad="")
    for k, o in old.items():
        if k not in new:
            add(o, "removed from export", o["status"], "")
    upsert(db, "pending", rows)
    print(f"{len(rows)} changes between {d_old} and {d_new}.")
    cmd_show(a, db)


def parse_extra(x):
    try:
        d = json.loads(x) if isinstance(x, str) else (x or {})
    except ValueError:
        return "", str(x)[:200]
    if isinstance(d, dict):
        return str(d.get("old_value", "")), str(d.get("new_value", d.get("value", "")))
    return "", str(d)[:200]


def cmd_import_activity(a, db):
    data = json.load(open(a.file))
    items = data.get("data", data) if isinstance(data, dict) else data
    rows = []
    for it in items:
        when = it.get("event_time", "")
        date, time = (when[:10], when[11:16]) if len(when) >= 16 else (when[:10], "")
        otype = str(it.get("object_type", "")).upper()
        name = it.get("object_name", "")
        ov, nv = parse_extra(it.get("extra_data", ""))
        rows.append({"date": date, "time": time, "platform": a.platform, "account_label": a.account,
                     "level": {"CAMPAIGN": "campaign", "ADSET": "ad_set", "AD": "ad"}.get(otype, otype.lower()),
                     "campaign": name if otype == "CAMPAIGN" else it.get("campaign_name", ""),
                     "ad_set": name if otype == "ADSET" else it.get("adset_name", ""),
                     "ad": name if otype == "AD" else "",
                     "change_type": it.get("translated_event_type") or it.get("event_type", ""),
                     "old_value": ov, "new_value": nv, "why": "", "status": "pending",
                     "source": f"{a.source} activity log"})
    upsert(db, "pending", rows)
    print(f"Imported {len(rows)} activity rows.")
    cmd_show(a, db)


def table(title, rows, cols):
    print(f"\n{title}")
    if not rows:
        print("  (none)"); return
    w = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in cols}
    print("  # | " + " | ".join(c.ljust(w[c]) for c in cols))
    for i, r in enumerate(rows, 1):
        print(f"  {i} | " + " | ".join(str(r.get(c, "")).ljust(w[c]) for c in cols))


def pending_rows(db):
    rows = select(db, "pending")
    rows.sort(key=lambda r: (r["date"], r["time"], r["platform"], r["account_label"], r["campaign"], r["ad_set"], r["ad"], r["change_type"]))
    for r in rows:
        r["object"] = " / ".join(x for x in [r["ad_set"], r["ad"]] if x) or "(campaign)"
        r["change"] = f'{r["change_type"]}: {r["old_value"] or "-"} -> {r["new_value"] or "-"}'
        r["why_shown"] = r["why"] or NOT_GIVEN
    return rows


def cmd_show(a, db):
    rows = pending_rows(db)
    table("What happened", rows, ["date", "platform", "campaign", "object", "change"])
    table("Why", rows, ["campaign", "change", "why_shown"])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = argparse.ArgumentParser(add_help=False)
    base.add_argument("--store", default="paid-social-data")
    acct = argparse.ArgumentParser(add_help=False)
    acct.add_argument("--platform", required=True)
    acct.add_argument("--account", required=True, help="your own label for the account, never an ad account ID")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot", parents=[base, acct]); s.add_argument("--export", required=True); s.add_argument("--date")
    sub.add_parser("diff", parents=[base, acct])
    i = sub.add_parser("import-activity", parents=[base, acct]); i.add_argument("--file", required=True); i.add_argument("--source", default="MCP")
    sub.add_parser("show", parents=[base])
    a = p.parse_args()
    db = connect(a.store)
    {"snapshot": cmd_snapshot, "diff": cmd_diff, "import-activity": cmd_import_activity, "show": cmd_show}[a.cmd](a, db)


if __name__ == "__main__":
    main()
