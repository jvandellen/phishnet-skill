# Phish.in — Live Audio Archive (API v2 + MCP)

https://phish.in is an open-source archive of live Phish audience recordings (source: github.com/jcraigk/phishin). It covers the complete setlist catalog — shows without recordings are marked `audio_status: "missing"`. Use it when the user wants to *listen*: streamable audio, track durations, per-track MP3 links, jam tags, or "play me that Ghost."

Free, no warranty, "please be nice" — no API key required for read endpoints. Interactive docs (Swagger): https://phish.in/api-docs

## Choosing between sources

| Need | Source |
|---|---|
| Canonical setlists, gaps, jam chart commentary, reviews | Phish.net API (`api-reference.md`) |
| Pre-computed stats, show-finder | ihoz.com (`phishstats.md`) |
| Audio streams, track times, MP3 links, audio-oriented tags | **phish.in** |
| Video footage | YouTube (`youtube.md`) |

Phish.net remains the setlist authority (phish.in ingests from it); cite Phish.net for "what was played," phish.in for "listen here."

## MCP server (best option in claude.ai)

Phish.in exposes an MCP endpoint: **`POST https://phish.in/mcp`** (server card at `/.well-known/mcp/server-card.json`). Tools: `list_shows`, `get_show`, `list_songs`, `get_song`, `list_venues`, `get_venue`, `list_tours`, `get_tour`, `list_years`, `list_tags`, `get_tag`, `list_playlists`, `get_playlist`, `get_audio_track`, `search`, `stats`.

If the user is in claude.ai and wants live phish.in data, suggest adding it as a custom connector (Settings → Connectors → Add custom connector → URL `https://phish.in/mcp`). Once connected, prefer those MCP tools over constructing REST calls.

## REST API v2

Base: `https://phish.in/api/v2` — JSON, paginated (`page`, `per_page`), sorted via `sort=column:direction` (e.g. `sort=date:desc`).

```
GET /shows                       # filters: year, year_range (1997-1998), venue_slug,
                                 #   tag_slug, start_date, end_date, us_state
GET /shows/:date                 # one show by YYYY-MM-DD, with tracks + audio URLs
GET /shows/random
GET /shows/day_of_year/:date     # "this day in Phish history"
GET /songs        /songs/:slug   # song catalog and per-song performance list
GET /tracks       /tracks/:id    # individual recordings; includes mp3 URL, duration
GET /venues       /venues/:slug
GET /tours        /tours/:slug
GET /years                       # era/year summaries with show counts
GET /tags                        # audio tags (jams, teases, guests, etc.)
GET /search/:term                # cross-entity search
```

Writes (playlists, likes) require user auth — out of scope; send users to the site.

## Useful patterns

- **"Play/hear that jam"**: `GET /shows/:date` → find the track by title → give the track's phish.in URL (and duration). Durations here are a good cross-check for jam length questions.
- **"This day in Phish history"**: `/shows/day_of_year/:date` beats assembling it from Phish.net queries.
- **Longest versions**: `/songs/:slug` returns performances with durations — sortable without extra math.
- **Missing audio**: `audio_status: "missing"` means the show happened but no recording is archived — don't report it as "no such show."

## scripts/phishin.py

```bash
python scripts/phishin.py show 1997-11-22            # tracks + stream URLs
python scripts/phishin.py song tweezer --sort duration:desc --limit 10
python scripts/phishin.py day-of-year 2026-09-07     # this day in history
python scripts/phishin.py search "big cypress"
python scripts/phishin.py random
```

No key needed. Same environment caveat: needs network access to phish.in (Claude Code yes; claude.ai sandbox no — use the MCP connector there instead, which is strictly better anyway).

## Etiquette

Free community project run by one maintainer. Cache, paginate politely, don't bulk-download audio programmatically. Credit "Phish.in" for audio and "Phish.net" for underlying setlist data.
