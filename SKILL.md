---
name: phishnet
description: Query the Phish.net API v5 for Phish setlists, shows, songs, jam charts, venues, reviews, and attendance data. Use this skill whenever the user asks about Phish shows or setlists ("what did they play at...", "when was the last..."), song performance history or gaps, jam chart entries, venue history, tour dates, show ratings/reviews, or anything referencing Phish.net data — even if they don't mention the API by name. Also use it when building tools, scripts, or reports that consume Phish.net data.
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
