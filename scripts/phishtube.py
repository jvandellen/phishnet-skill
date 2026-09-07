#!/usr/bin/env python3
"""Track Phish videos on YouTube via the YouTube Data API v3. Stdlib only.

Usage:
  python phishtube.py uploads <channel_handle> [--limit N]
  python phishtube.py search "<query>" [--after YYYY-MM-DD] [--limit N]
  python phishtube.py show YYYY-MM-DD [--limit N]
  python phishtube.py details VIDEO_ID [VIDEO_ID ...]

API key: --apikey flag, else YOUTUBE_API_KEY env var.
Quota notes: uploads/details cost 1 unit per call; search costs 100.
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://www.googleapis.com/youtube/v3"


def get(endpoint, **params):
    url = f"{BASE}/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "phishnet-skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body)["error"]["message"]
        except Exception:
            msg = body[:300]
        raise SystemExit(f"YouTube API error {e.code}: {msg}")


def uploads_playlist(handle, key):
    data = get("channels", part="contentDetails,snippet", forHandle=handle.lstrip("@"), key=key)
    items = data.get("items") or []
    if not items:
        raise SystemExit(f"No channel found for handle @{handle.lstrip('@')}")
    ch = items[0]
    return (ch["snippet"]["title"],
            ch["contentDetails"]["relatedPlaylists"]["uploads"])


def cmd_uploads(args, key):
    title, playlist = uploads_playlist(args.target, key)
    vids, token = [], None
    while len(vids) < args.limit:
        params = dict(part="snippet", playlistId=playlist,
                      maxResults=min(50, args.limit - len(vids)), key=key)
        if token:
            params["pageToken"] = token
        page = get("playlistItems", **params)
        for it in page.get("items", []):
            s = it["snippet"]
            vids.append({"videoId": s["resourceId"]["videoId"],
                         "title": s["title"],
                         "published": s["publishedAt"]})
        token = page.get("nextPageToken")
        if not token:
            break
    return {"channel": title, "videos": vids}


def cmd_search(args, key, query=None):
    params = dict(part="snippet", q=query or args.target, type="video",
                  order="date", maxResults=min(50, args.limit), key=key)
    if args.after:
        params["publishedAfter"] = f"{args.after}T00:00:00Z"
    page = get("search", **params)
    return {"query": params["q"],
            "videos": [{"videoId": it["id"]["videoId"],
                        "title": it["snippet"]["title"],
                        "channel": it["snippet"]["channelTitle"],
                        "published": it["snippet"]["publishedAt"]}
                       for it in page.get("items", [])]}


def cmd_show(args, key):
    y, m, d = args.target.split("-")
    query = f"Phish {int(m)}/{int(d)}/{y[2:]} OR \"Phish {args.target}\""
    if not args.after:
        args.after = args.target
    return cmd_search(args, key, query=query)


def cmd_details(args, key):
    ids = ",".join([args.target] + args.extra)
    page = get("videos", part="contentDetails,statistics,snippet", id=ids, key=key)
    return {"videos": [{"videoId": it["id"],
                        "title": it["snippet"]["title"],
                        "channel": it["snippet"]["channelTitle"],
                        "duration": it["contentDetails"]["duration"],
                        "views": it.get("statistics", {}).get("viewCount")}
                       for it in page.get("items", [])]}


def main():
    ap = argparse.ArgumentParser(description="Phish on YouTube")
    ap.add_argument("command", choices=["uploads", "search", "show", "details"])
    ap.add_argument("target", help="channel handle | query | date | video ID")
    ap.add_argument("extra", nargs="*", help="additional video IDs for 'details'")
    ap.add_argument("--after", help="YYYY-MM-DD publishedAfter filter")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--apikey", default=os.environ.get("YOUTUBE_API_KEY"))
    ap.add_argument("--raw", action="store_true")
    args = ap.parse_args()

    if not args.apikey:
        sys.exit("No API key. Set YOUTUBE_API_KEY or pass --apikey "
                 "(enable 'YouTube Data API v3' at console.cloud.google.com).")

    result = {"uploads": cmd_uploads, "search": cmd_search,
              "show": cmd_show, "details": cmd_details}[args.command](args, args.apikey)

    if args.raw:
        json.dump(result, sys.stdout, indent=2)
        print()
        return
    vids = result.get("videos", [])
    header = result.get("channel") or result.get("query") or ""
    if header:
        print(f"# {header}  ({len(vids)} videos)")
    for v in vids:
        date = (v.get("published") or "")[:10]
        dur = f"  [{v['duration']}]" if v.get("duration") else ""
        ch = f"  ({v['channel']})" if v.get("channel") and not result.get("channel") else ""
        print(f"{date}  {v['title']}{ch}{dur}")
        print(f"          https://www.youtube.com/watch?v={v['videoId']}")


if __name__ == "__main__":
    main()
