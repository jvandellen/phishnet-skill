#!/usr/bin/env python3
"""Minimal Phish.net API v5 client. Stdlib only.

Usage:
  python phishnet.py <method> [column value | id] [options]

Examples:
  python phishnet.py setlists showdate 1997-11-22
  python phishnet.py shows showyear 2026 --order-by showdate --limit 20
  python phishnet.py jamcharts slug tweezer --raw
  python phishnet.py songs slug ghost

API key: --apikey flag, else PHISHNET_API_KEY env var.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://api.phish.net/v5"
TRANS = {",": ", ", ">": " > ", "->": " -> "}


def build_url(method, path_parts, params):
    path = "/".join([method] + [urllib.parse.quote(str(p)) for p in path_parts])
    return f"{BASE}/{path}.json?{urllib.parse.urlencode(params)}"


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "phishnet-skill/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if payload.get("error") not in (False, 0, None, "", "0"):
        msg = payload.get("error_message") or payload.get("error")
        raise SystemExit(f"API error: {msg}")
    return payload.get("data", [])


def render_setlist(rows):
    """Group setlist rows into a human-readable setlist."""
    shows = {}
    for r in rows:
        shows.setdefault(r["showid"], []).append(r)
    out = []
    for showid, songs in shows.items():
        songs.sort(key=lambda r: int(r.get("position", 0)))
        first = songs[0]
        out.append(f"{first['showdate']} — {first.get('venue','?')}, "
                   f"{first.get('city','?')}, {first.get('state') or first.get('country','?')}"
                   f"  [{first.get('artist_name','?')}]")
        sets = {}
        order = []
        for r in songs:
            s = str(r.get("set", "?"))
            if s not in sets:
                sets[s] = []
                order.append(s)
            mark = TRANS.get((r.get("trans_mark") or "").strip(), "  ")
            sets[s].append(r["song"] + mark.rstrip() if r is songs[-1] else r["song"] + mark)
        for s in order:
            label = {"e": "Encore", "e2": "Encore 2", "e3": "Encore 3"}.get(s, f"Set {s}")
            line = "".join(sets[s]).rstrip(" ,>-")
            out.append(f"  {label}: {line}")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Phish.net API v5 client")
    ap.add_argument("method", help="artists|shows|setlists|songs|songdata|venues|jamcharts|attendance|reviews|users")
    ap.add_argument("path", nargs="*", help="[column value] or [id]")
    ap.add_argument("--order-by")
    ap.add_argument("--direction", choices=["asc", "desc"])
    ap.add_argument("--limit", type=int)
    ap.add_argument("--apikey", default=os.environ.get("PHISHNET_API_KEY"))
    ap.add_argument("--raw", action="store_true", help="print raw JSON data array")
    ap.add_argument("--url-only", action="store_true", help="print the request URL (key redacted) and exit")
    args = ap.parse_args()

    if not args.apikey and not args.url_only:
        sys.exit("No API key. Set PHISHNET_API_KEY or pass --apikey. Get one at https://phish.net/api/keys")

    params = {"apikey": args.apikey or "YOUR_API_KEY"}
    for k in ("order_by", "direction", "limit"):
        v = getattr(args, k.replace("-", "_"), None) or getattr(args, k, None)
        if v:
            params[k] = v

    url = build_url(args.method, args.path, params)
    if args.url_only:
        print(url.replace(params["apikey"], "REDACTED"))
        return

    data = fetch(url)
    if args.raw or args.method != "setlists":
        json.dump(data, sys.stdout, indent=2)
        print()
    else:
        print(render_setlist(data) if data else "No results.")


if __name__ == "__main__":
    main()
