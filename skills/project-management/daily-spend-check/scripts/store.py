"""Local database for the Skill Library: one SQLite file, standard library only (Python 3.9+).

Every skill that saves data copies this same file into its scripts/ folder, so each skill works on its own.
The database lives at <store>/paid-social.db (default store: ./paid-social-data). It is private: keep it out of git.

Command line:
  python3 store.py init   [--store paid-social-data]          create the database and tables
  python3 store.py export [--store paid-social-data]          write every table to CSV (opens in Google Sheets)
  python3 store.py import-csv --table daily_metrics --file daily-metrics.csv [--store ...]
"""
import argparse
import csv
import pathlib
import sqlite3

TABLES = {
    "history": ["date", "time", "platform", "account_label", "level", "campaign", "ad_set", "ad",
                "change_type", "old_value", "new_value", "why", "status", "source"],
    "pending": ["date", "time", "platform", "account_label", "level", "campaign", "ad_set", "ad",
                "change_type", "old_value", "new_value", "why", "status", "source"],
    "snapshots": ["date", "platform", "account_label", "level", "campaign", "ad_set", "ad", "status", "budget", "bid"],
    "daily_metrics": ["date", "platform", "account_label", "campaign", "ad_set", "ad", "spend", "impressions", "reach",
                      "link_clicks", "results", "result_type", "revenue", "frequency", "video_3s_plays", "thruplays"],
    "moments": ["date_found", "account_label", "platform", "moment_type", "metric", "before", "after", "change_pct",
                "period", "linked_changes", "public_ready"],
    "accounts": ["account_label", "platform", "time_zone", "notes"],
}
KEYS = {
    "history": ["date", "time", "platform", "account_label", "campaign", "ad_set", "ad", "change_type", "old_value", "new_value"],
    "pending": ["date", "time", "platform", "account_label", "campaign", "ad_set", "ad", "change_type", "old_value", "new_value"],
    "snapshots": ["date", "platform", "account_label", "campaign", "ad_set", "ad"],
    "daily_metrics": ["date", "platform", "account_label", "campaign", "ad_set", "ad"],
    "moments": ["account_label", "platform", "moment_type", "metric", "period"],
    "accounts": ["account_label", "platform"],
}


def connect(store="paid-social-data"):
    folder = pathlib.Path(store).expanduser()
    folder.mkdir(parents=True, exist_ok=True)
    gi = folder / ".gitignore"
    if not gi.exists():
        gi.write_text("# Private paid social data. Never commit.\n*\n")
    db = sqlite3.connect(folder / "paid-social.db")
    db.row_factory = sqlite3.Row
    for t, cols in TABLES.items():
        db.execute(f"CREATE TABLE IF NOT EXISTS {t} ({', '.join(c + ' TEXT' for c in cols)}, "
                   f"UNIQUE({', '.join(KEYS[t])}) ON CONFLICT REPLACE)")
    return db


def upsert(db, table, rows):
    """Insert rows (dicts). A row with the same key replaces the old one."""
    cols = TABLES[table]
    db.executemany(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                   [[("" if r.get(c) is None else str(r.get(c))) for c in cols] for r in rows])
    db.commit()


def insert_new(db, table, rows):
    """Insert rows, keeping any existing row with the same key (used for history, so reasons are never overwritten)."""
    cols = TABLES[table]
    db.executemany(f"INSERT OR IGNORE INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
                   [[("" if r.get(c) is None else str(r.get(c))) for c in cols] for r in rows])
    db.commit()


def select(db, table, where="", params=()):
    q = f"SELECT * FROM {table}" + (f" WHERE {where}" if where else "")
    return [dict(r) for r in db.execute(q, params)]


def export(db, store):
    out = pathlib.Path(store).expanduser() / "csv"
    out.mkdir(parents=True, exist_ok=True)
    for t, cols in TABLES.items():
        with (out / f"{t.replace('_', '-')}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(select(db, t))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["init", "export", "import-csv"])
    p.add_argument("--store", default="paid-social-data")
    p.add_argument("--table", choices=list(TABLES)); p.add_argument("--file")
    a = p.parse_args()
    db = connect(a.store)
    if a.cmd == "init":
        print(f"Database ready at {pathlib.Path(a.store) / 'paid-social.db'}")
    elif a.cmd == "export":
        print(f"Exported tables to {export(db, a.store)}")
    else:
        rows = list(csv.DictReader(open(a.file, newline="", encoding="utf-8-sig")))
        upsert(db, a.table, rows)
        print(f"Imported {len(rows)} rows into {a.table}")


if __name__ == "__main__":
    main()
