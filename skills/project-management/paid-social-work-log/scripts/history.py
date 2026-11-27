"""Why it happened: confirm pending changes into the history table, and rebuild history.csv. Python 3.9+, standard library only.

Usage:
  python3 history.py confirm --why "1=scaling winner" --why "2=CPA 2x target"   (numbers match `changes.py show`)
  python3 history.py confirm --all-ok                                         (save all as listed)
  python3 history.py add --platform meta --account client-a --campaign "Prospecting" --change "paused 3 ads" --why "fatigue"
  python3 history.py rebuild                                                   (write history.csv from the database)
  python3 history.py show [--days 7]
All commands take --store (default paid-social-data).
A change with no reason from the user is saved as why "not given", status "unconfirmed". The script never writes a reason
the user did not give, and never overwrites a reason already saved.
"""
import argparse
import csv
import datetime as dt
import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from changes import pending_rows, table  # noqa: E402
from store import TABLES, connect, insert_new, select  # noqa: E402

NOT_GIVEN = "not given"


def cmd_confirm(a, db):
    rows = pending_rows(db)
    if not rows:
        sys.exit("No pending changes.")
    reasons = {}
    for item in a.why or []:
        n, _, text = item.partition("=")
        if not n.strip().isdigit() or not text.strip():
            sys.exit(f'Bad --why "{item}". Use the form 3="reason".')
        reasons[int(n)] = text.strip()
    for i, r in enumerate(rows, 1):
        if i in reasons:
            r["why"], r["status"] = reasons[i], "confirmed"
        else:
            r["why"] = NOT_GIVEN
            r["status"] = "confirmed" if a.all_ok else "unconfirmed"
    insert_new(db, "history", rows)
    db.execute("DELETE FROM pending"); db.commit()
    print(f"Saved {len(rows)} changes to history. {sum(r['status'] == 'unconfirmed' for r in rows)} unconfirmed.")
    cmd_rebuild(a, db)


def cmd_add(a, db):
    row = {"date": a.date or dt.date.today().isoformat(), "time": a.time or dt.datetime.now().strftime("%H:%M"),
           "platform": a.platform, "account_label": a.account,
           "level": "ad" if a.ad else ("ad_set" if a.ad_set else "campaign"), "campaign": a.campaign,
           "ad_set": a.ad_set or "", "ad": a.ad or "", "change_type": a.change, "old_value": a.old or "",
           "new_value": a.new or "", "why": a.why or NOT_GIVEN, "status": "confirmed" if a.why else "unconfirmed",
           "source": "told by user"}
    insert_new(db, "history", [row])
    print("Added 1 change to history.")
    cmd_rebuild(a, db)


def cmd_set_why(a, db):
    n = db.execute("UPDATE history SET why=?, status='confirmed' WHERE rowid=? AND why=?", (a.why, a.id, NOT_GIVEN)).rowcount
    db.commit()
    print("Updated." if n else "No unconfirmed row with that id.")
    cmd_rebuild(a, db)


def cmd_rebuild(a, db):
    rows = select(db, "history")
    rows.sort(key=lambda r: (r["date"], r["time"], r["platform"], r["account_label"], r["campaign"]))
    path = pathlib.Path(a.store).expanduser() / "history.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=TABLES["history"]); w.writeheader(); w.writerows(rows)
    print(f"Rebuilt {path} ({len(rows)} rows).")


def cmd_show(a, db):
    since = (dt.date.today() - dt.timedelta(days=a.days)).isoformat()
    rows = [dict(r, id=r["rowid"]) for r in db.execute("SELECT rowid, * FROM history WHERE date >= ? ORDER BY date, time", (since,))]
    table(f"History since {since}", rows, ["id", "date", "platform", "campaign", "change_type", "new_value", "why", "status"])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    base = argparse.ArgumentParser(add_help=False); base.add_argument("--store", default="paid-social-data")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("confirm", parents=[base]); c.add_argument("--why", action="append"); c.add_argument("--all-ok", action="store_true")
    ad = sub.add_parser("add", parents=[base])
    for f in ["platform", "account", "campaign", "change"]:
        ad.add_argument(f"--{f}", required=True)
    for f in ["ad-set", "ad", "old", "new", "why", "date", "time"]:
        ad.add_argument(f"--{f}")
    sw = sub.add_parser("set-why", parents=[base], help="add a reason later to an unconfirmed row (id from show)")
    sw.add_argument("--id", type=int, required=True); sw.add_argument("--why", required=True)
    sub.add_parser("rebuild", parents=[base])
    sh = sub.add_parser("show", parents=[base]); sh.add_argument("--days", type=int, default=7)
    a = p.parse_args()
    db = connect(a.store)
    {"confirm": cmd_confirm, "add": cmd_add, "set-why": cmd_set_why, "rebuild": cmd_rebuild, "show": cmd_show}[a.cmd](a, db)


if __name__ == "__main__":
    main()
