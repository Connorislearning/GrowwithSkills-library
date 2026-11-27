"""Meta Marketing API fallback, for when no Meta Ads MCP tool is available. Python 3.9+, standard library only.

Usage:
  python3 meta_api.py activities --account client-a [--since 2026-11-27] [--until 2026-11-27] [--store paid-social-data]
  python3 meta_api.py insights   --account client-a [--since ...] [--until ...] [--result-action purchase]

Credentials come ONLY from environment variables, or from a .env file in the current folder that git ignores:
  META_ACCESS_TOKEN=...        a token with ads_read permission
  META_AD_ACCOUNT_ID=act_...   the ad account to read
  META_API_VERSION=v23.0       optional; set it to the version in Meta's current docs
Never put these in a file you commit. The ad account ID is used only for the request; the database stores
your --account label instead.

`activities` reads the account's change history (the activities edge) and saves it as pending changes.
`insights` reads daily ad-level results and saves them to the daily_metrics table.
This script has not been tested against a live account in the public repo; check the output the first time.
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from store import connect, upsert  # noqa: E402


def load_env():
    env = pathlib.Path(".env")
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    token, acct = os.environ.get("META_ACCESS_TOKEN"), os.environ.get("META_AD_ACCOUNT_ID")
    if not token or not acct:
        sys.exit("Set META_ACCESS_TOKEN and META_AD_ACCOUNT_ID as environment variables or in a git-ignored .env file.")
    if not acct.startswith("act_"):
        acct = "act_" + acct
    return token, acct, os.environ.get("META_API_VERSION", "v23.0")


def get_all(url, params, token):
    params = dict(params, access_token=token)
    url = url + "?" + urllib.parse.urlencode(params)
    out = []
    while url:
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                page = json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            sys.exit(f"Meta API error {e.code}: {body[:500]}")  # the token is never printed
        out += page.get("data", [])
        url = page.get("paging", {}).get("next")
    return out


def cmd_activities(a):
    token, acct, ver = load_env()
    items = get_all(f"https://graph.facebook.com/{ver}/{acct}/activities",
                    {"fields": "event_time,event_type,translated_event_type,object_type,object_name,extra_data,actor_name",
                     "since": a.since, "until": a.until, "limit": 500}, token)
    path = pathlib.Path(a.store).expanduser() / "raw" / "meta" / f"{a.until}_activities.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"data": items}, indent=1))
    print(f"Fetched {len(items)} activity rows; saved raw copy to {path}")
    os.execvp(sys.executable, [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "changes.py"),
                               "import-activity", "--file", str(path), "--platform", "meta", "--account", a.account,
                               "--store", a.store, "--source", "Meta Marketing API"])


def action(lst, name):
    return sum(float(x.get("value", 0)) for x in (lst or []) if x.get("action_type") == name)


def cmd_insights(a):
    token, acct, ver = load_env()
    items = get_all(f"https://graph.facebook.com/{ver}/{acct}/insights",
                    {"level": "ad", "time_increment": 1, "time_range": json.dumps({"since": a.since, "until": a.until}),
                     "fields": "campaign_name,adset_name,ad_name,spend,impressions,reach,inline_link_clicks,frequency,"
                               "actions,action_values,video_thruplay_watched_actions", "limit": 500}, token)
    rows = [{"date": i["date_start"], "platform": "meta", "account_label": a.account, "campaign": i.get("campaign_name", ""),
             "ad_set": i.get("adset_name", ""), "ad": i.get("ad_name", ""), "spend": i.get("spend", 0),
             "impressions": i.get("impressions", 0), "reach": i.get("reach", 0), "link_clicks": i.get("inline_link_clicks", 0),
             "results": action(i.get("actions"), a.result_action), "result_type": a.result_action,
             "revenue": action(i.get("action_values"), a.result_action), "frequency": i.get("frequency", ""),
             "video_3s_plays": action(i.get("actions"), "video_view"),
             "thruplays": action(i.get("video_thruplay_watched_actions"), "video_view")} for i in items]
    upsert(connect(a.store), "daily_metrics", rows)
    print(f"Saved {len(rows)} daily ad rows ({a.since} to {a.until}) to daily_metrics.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    today = dt.date.today().isoformat()
    for name in ["activities", "insights"]:
        s = sub.add_parser(name)
        s.add_argument("--account", required=True, help="your own label, never the ad account ID")
        s.add_argument("--since", default=today); s.add_argument("--until", default=today)
        s.add_argument("--store", default="paid-social-data")
        if name == "insights":
            s.add_argument("--result-action", default="purchase", help="action_type that counts as a result, e.g. purchase or lead")
    a = p.parse_args()
    {"activities": cmd_activities, "insights": cmd_insights}[a.cmd](a)


if __name__ == "__main__":
    main()
