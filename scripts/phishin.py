#!/usr/bin/env python3
"""Query the Phish.in API v2 (live audio archive). Stdlib only. No API key needed.

Usage:
  python phishin.py show YYYY-MM-DD
  python phishin.py song <slug> [--sort duration:desc] [--limit N]
  python phishin.py day-of-year YYYY-MM-DD
  python phishin.py search "<term>"
  python phishin.py random
  python phishin.py shows --year 1997 [--venue-slug slug] [--us-state VT] [--limit N]
"""
import argparse
import json
import sys
import urllib.parse
import urllib.request

BASE = "https://phish.in/api/v2"


def get(path, **params):
    qs = f"?{urllib.parse.urlencode({k: v for k, v in params.items() if v})}" if any(params.values()) else ""
    url = f"{BASE}/{path}{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": "phishnet-skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"phish.in API error {e.code} for {path}")


def fmt_ms(ms):
    if not ms:
        return "?"
    s = int(ms) // 1000
    return f"{s // 60}:{s % 60:02d}"


def print_show(show):
    print(f"{show.get('date')} — {show.get('venue_name', '?')}, "
          f"{(show.get('venue') or {}).get('location', '')}".rstrip(", "))
    if show.get("audio_status") == "missing":
        print("  (no audio archived for this show)")
    cur_set = None
    for t in show.get("tracks", []):
        if t.get("set_name") != cur_set:
            cur_set = t.get("set_name")
            print(f"  {cur_set}:")
        tags = " ".join(f"[{tg['name']}]" for tg in t.get("tags", [])) if t.get("tags") else ""
        print(f"    {t['title']}  ({fmt_ms(t.get('duration'))}) {tags}")
        if t.get("mp3_url"):
            print(f"      {t['mp3_url']}")


def main():
    ap = argparse.ArgumentParser(description="Phish.in audio archive client")
    ap.add_argument("command", choices=["show", "song", "day-of-year", "search", "random", "shows"])
    ap.add_argument("target", nargs="?", help="date | song slug | search term")
    ap.add_argument("--sort")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--year")
    ap.add_argument("--venue-slug")
    ap.add_argument("--us-state")
    ap.add_argument("--raw", action="store_true")
    args = ap.parse_args()

    if args.command == "show":
        data = get(f"shows/{args.target}")
    elif args.command == "random":
        data = get("shows/random")
    elif args.command == "day-of-year":
        data = get(f"shows/day_of_year/{args.target}")
    elif args.command == "search":
        data = get(f"search/{urllib.parse.quote(args.target)}")
    elif args.command == "song":
        data = get(f"songs/{args.target}", sort=args.sort, per_page=args.limit)
    elif args.command == "shows":
        data = get("shows", year=args.year, venue_slug=args.venue_slug,
                   us_state=args.us_state, per_page=args.limit, sort=args.sort)

    if args.raw:
        json.dump(data, sys.stdout, indent=2)
        print()
        return

    if args.command in ("show", "random", "day-of-year"):
        shows = data.get("shows", [data]) if isinstance(data, dict) else data
        for s in (shows if isinstance(shows, list) else [shows]):
            print_show(s)
            print()
    elif args.command == "song":
        print(f"# {data.get('title', args.target)} — {data.get('tracks_count', '?')} recordings")
        for t in data.get("tracks", [])[:args.limit]:
            print(f"{t.get('show_date')}  {fmt_ms(t.get('duration'))}  {t.get('venue_name','')}")
            if t.get("mp3_url"):
                print(f"    {t['mp3_url']}")
    elif args.command == "shows":
        for s in data.get("shows", []):
            print(f"{s.get('date')}  {s.get('venue_name','?')}  "
                  f"({s.get('duration') and fmt_ms(s['duration']) or '?'})"
                  f"{'  [no audio]' if s.get('audio_status') == 'missing' else ''}")
    else:
        json.dump(data, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
