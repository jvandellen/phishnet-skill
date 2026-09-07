---
name: phishnet
description: Query the Phish.net API v5 for Phish setlists, shows, songs, jam charts, venues, reviews, and attendance data; find live audio recordings, track durations, and streams via Phish.in (API v2 and its MCP server); and track Phish videos on YouTube (official channel uploads, show/jam footage, couch tour streams) via the YouTube Data API. Use this skill whenever the user asks about Phish shows or setlists ("what did they play at...", "when was the last..."), song performance history or gaps, jam chart entries, venue history, tour dates, show ratings/reviews, listening to or streaming a Phish show or jam, longest versions of a song, "this day in Phish history", finding video of a Phish show or jam, new uploads from Phish's YouTube channels, or anything referencing Phish.net or Phish.in data — even if they don't mention the API by name. Also use it when building tools, scripts, or reports that consume Phish.net, Phish.in, or Phish YouTube data.
---

# Phish.net API Skill

Query the Phish.net API v5 (a project of the non-profit Mockingbird Foundation) for authoritative Phish show, setlist, song, and venue data.

## API key (required)

Every request needs an API key passed as `apikey` in the query string.

1. Check for an environment variable: `PHISHNET_API_KEY`.
2. If absent, ask the user for their key. Keys are free at https://phish.net/api/keys (requires a Phish.net account).
3. Never print the key back to the user, embed it in shared artifacts, or store it in memory files. In generated code, read it from an environment variable — never hardcode it into client-side JavaScript or committed code.

## Request structure

Base URL: `https://api.phish.net/v5`

Three URL shapes:

```
/v5/{method}.json?apikey=KEY                     # everything (avoid — huge/slow)
/v5/{method}/{id}.json?apikey=KEY                # one record by ID
/v5/{method}/{column}/{value}.json?apikey=KEY    # filter by any column
```

Methods: `artists`, `attendance`, `jamcharts`, `reviews`, `setlists`, `shows`, `songs`, `songdata`, `users`, `venues`.

Optional query params: `order_by` (any column), `direction` (`asc`/`desc`), `limit` (max results), `callback` (JSONP). Formats: `.json` (default choice), `.html`, sometimes `.xml`.

Responses are JSON with an error/header envelope and a `data` array. Always check the error field before processing `data`.

### Common query patterns

```
# Setlist for a specific date
/v5/setlists/showdate/1997-11-22.json

# Every performance of a song (prefer slug over name)
/v5/setlists/slug/tweezer.json

# All shows in a year, chronological
/v5/shows/showyear/1997.json?order_by=showdate

# Shows in a state
/v5/shows/state/MI.json

# Jam chart entries for a song
/v5/jamcharts/slug/ghost.json

# Venue by ID, song catalog, etc.
/v5/venues/{venueid}.json
/v5/songs.json
```

Show columns usable as filters or `order_by`: `showid`, `showyear`, `showmonth`, `showday`, `showdate`, `permalink`, `venueid`, `venue`, `city`, `state`, `country`, `artistid`, `artist_name`, `tourid`, `tour_name`.

Note: `shows` and `setlists` include side projects (Trey, Mike, etc.). Filter to `artistid = 1` or `artist_name = "Phish"` when the user means Phish proper — a "last time played" answer is wrong if a TAB performance sneaks in.

For full method/column details, gap-calculation guidance, and setlist-data quirks, read `references/api-reference.md`.

For pre-computed statistics — all-time play counts, per-tour/per-year totals, "identify a show from songs I remember" (Show Finder), personal seen-stats — read `references/phishstats.md` and use ZZYZX's Phishtistics site (ihoz.com) instead of aggregating many API calls yourself.

## Phish.in audio archive

For listening — streamable recordings, per-track MP3 links and durations, "longest Tweezers", "this day in Phish history" — read `references/phishin.md` and use `scripts/phishin.py` (no API key needed):

```bash
python scripts/phishin.py show 1997-11-22          # tracks + stream URLs
python scripts/phishin.py song tweezer --sort duration:desc --limit 10
python scripts/phishin.py day-of-year 2026-09-07
```

Phish.in also runs an MCP server at `https://phish.in/mcp` — in claude.ai, suggest the user add it as a custom connector for live audio-archive queries without any sandbox limitation. Phish.net stays the setlist authority; phish.in is where the audio lives.

## YouTube video tracking

For finding or tracking Phish videos (official uploads, full-show or single-jam footage, "is there video of that Tweezer?"), read `references/youtube.md` and use `scripts/phishtube.py`. It needs a separate free Google API key (`YOUTUBE_API_KEY` env var; same never-echo/never-store handling as the Phish.net key).

```bash
python scripts/phishtube.py uploads phish --limit 25       # official channel
python scripts/phishtube.py show 2026-09-04                # footage from a show date
python scripts/phishtube.py search "Phish Ghost 1997" --after 1997-11-01
```

Quota matters: channel-uploads listing costs 1 unit, search costs 100 (10,000/day budget) — prefer uploads listing and cache video IDs when tracking. The best workflow combines both APIs: pull the setlist/jam chart from Phish.net, then search YouTube for the flagged jams by song + date.

## How to run queries

**Environments with network access (Claude Code, etc.):** use `scripts/phishnet.py` — a stdlib-only CLI wrapper:

```bash
export PHISHNET_API_KEY=...   # if not already set
python scripts/phishnet.py setlists showdate 1997-11-22
python scripts/phishnet.py shows showyear 2026 --order-by showdate --limit 20
python scripts/phishnet.py jamcharts slug tweezer --raw   # raw JSON to stdout
```

**Sandboxed claude.ai:** the code sandbox can't reach api.phish.net, and the site bot-blocks web_fetch. Don't burn turns retrying — construct the exact URL and hand the user a ready-to-run curl command (with `YOUR_API_KEY` placeholder), e.g. `curl "https://api.phish.net/v5/setlists/showdate/1997-11-22.json?apikey=YOUR_API_KEY"`, and offer to parse/analyze the JSON they paste back. For anything beyond a one-off lookup, suggest running `scripts/phishnet.py` in Claude Code where it works directly.

## Interpreting results

- Setlist rows are one row per song performance with `set` (1, 2, 3, e for encore), `position`, `song`, `trans_mark` (`,` pause, `>` segue, `->` seamless jam segue), `footnote`, plus show/venue fields. Reassemble sets in `position` order and preserve transition marks — "Tweezer > Prince Caspian" and "Tweezer, Prince Caspian" mean different things to a fan.
- "Last time played" / gap questions: sort that song's setlist rows by `showdate` descending, filter to Phish, and count intervening Phish shows for the gap.
- Jam chart entries are fan-curated notable versions — quote their descriptions as Phish.net commentary, not objective fact.

## Etiquette and attribution

- Cache locally rather than re-requesting; the API caches ~5 minutes server-side. Refresh cached data at least every 24 hours (setlists get corrected after review). Heavy or rapid-fire usage can get a key disabled — batch sensibly and use `limit`.
- When presenting Phish.net data in reports, artifacts, or apps, credit Phish.net / The Mockingbird Foundation. Their data is volunteer-built and attribution is a condition of use.
- `attendance`, `reviews`, and `users` are "special methods" with additional rules — read `references/api-reference.md` before using them.
