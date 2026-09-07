# Tracking Phish Videos on YouTube

Use the YouTube Data API v3 to find and track Phish videos: official uploads, full-show and single-song footage, couch-tour streams, and fan recordings.

## API key (separate from Phish.net)

Requires a Google API key with "YouTube Data API v3" enabled — free at https://console.cloud.google.com/ (Create project → Enable YouTube Data API v3 → Credentials → API key).

1. Check env var `YOUTUBE_API_KEY`.
2. If absent, ask the user. Same handling rules as the Phish.net key: never echo it back, never hardcode it, never store it in memory.

## Quota strategy (matters!)

Default quota is 10,000 units/day. `search.list` costs **100 units per call**; `playlistItems.list` and `channels.list` cost **1 unit**. So:

- To track a channel's videos, resolve the channel once, get its `uploads` playlist ID, and page through `playlistItems` — 1 unit per 50 videos.
- Reserve `search.list` for date/keyword hunting across all of YouTube ("Phish 7/4/2026 Tweezer").
- Cache results locally; a "new videos since last check" tracker should diff against stored video IDs, not re-search.

## Key channels

Resolve channel IDs at runtime via `channels.list?forHandle=<handle>` — don't hardcode IDs from memory. Handles worth knowing:

- `@phish` — official Phish channel (music videos, official releases, Dinner and a Movie)
- `@LivePhish` — official live content
- Fan/archival channels vary; let the user name theirs.

## Endpoints (base: https://www.googleapis.com/youtube/v3)

```
# Resolve a handle to channel + uploads playlist
GET /channels?part=contentDetails,snippet&forHandle=phish&key=KEY
  → items[0].contentDetails.relatedPlaylists.uploads

# List uploads (newest first), 1 unit per page
GET /playlistItems?part=snippet&playlistId=UU...&maxResults=50&key=KEY
  → snippet.title, snippet.publishedAt, snippet.resourceId.videoId

# Search (100 units) — date-scoped show footage
GET /search?part=snippet&q=Phish+2026-09-04&type=video&order=date
    &publishedAfter=2026-09-04T00:00:00Z&maxResults=25&key=KEY

# Video details (duration, view count) for found IDs, 1 unit
GET /videos?part=contentDetails,statistics,snippet&id=ID1,ID2&key=KEY
```

Video URL: `https://www.youtube.com/watch?v={videoId}`.

## Show-footage search tips

Fans title uploads inconsistently. For a show on YYYY-MM-DD, try queries combining:
- `Phish M/D/YY` and `Phish YYYY-MM-DD`
- `Phish <venue>` or `Phish <city> <year>`
- `Phish <song> <year>` for a specific jam
Filter with `publishedAfter` = show date to skip older shows at the same venue, and sanity-check titles/durations (a full set is 60+ min; a single song 5–30 min).

## scripts/phishtube.py

```bash
export YOUTUBE_API_KEY=...
python scripts/phishtube.py uploads phish --limit 25        # official channel uploads
python scripts/phishtube.py uploads LivePhish --limit 50
python scripts/phishtube.py search "Phish Dick's 2026" --after 2026-09-04
python scripts/phishtube.py show 2026-09-04                 # date-variant search helper
python scripts/phishtube.py details VIDEO_ID [VIDEO_ID...]  # durations/views
```

`--raw` prints raw JSON on any subcommand. Same environment note as the Phish.net script: needs network access to googleapis.com (Claude Code yes; claude.ai sandbox no — fall back to handing the user URLs/curl with a key placeholder).

## Combining with Phish.net data

The powerful workflow: pull a setlist from the Phish.net API, then search YouTube per set or per jam-chart-worthy song. E.g., jam chart flags a 20-minute Ghost → `search "Phish Ghost <showdate>"` → confirm via video duration. Credit Phish.net for setlist data as usual; YouTube results are just links, but respect uploaders — link, don't rip.
