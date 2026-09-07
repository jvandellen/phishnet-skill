# Phish.net API v5 Reference

Base URL: `https://api.phish.net/v5`. All requests require `apikey` as a GET or POST parameter. Every column listed for a method can be used both as a URL filter (`/{method}/{column}/{value}.json`) and as an `order_by` value.

Authoritative docs: https://docs.phish.net/ (full reference at /about-the-api, machine-readable version at /llms.txt, examples at /examples). If a query fails unexpectedly or a column seems wrong, fetch the live docs rather than guessing — the API evolves.

## Methods

| Method | Returns | Notes |
|---|---|---|
| `artists` | Artist data | Columns: `id`, `artist`, `slug`. Phish is artistid 1; side projects (Trey, Mike, Page, Fishman bands) have their own IDs. |
| `shows` | Show data | Columns: `showid`, `showyear`, `showmonth`, `showday`, `showdate`, `permalink`, `exclude_from_stats`, `venueid`, `setlist_notes`, `venue`, `city`, `state`, `country`, `artistid`, `artist_name`, `tourid`, `tour_name`, `created_at`, `updated_at`. |
| `setlists` | Setlist data | One row per song performance. Query by `showdate`, `showid`, `song`, or (preferred) `slug` — the URL-friendly song name. |
| `songs` | Song catalog | Basic song data: song name, slug, times played, debut, last played, current gap. |
| `songdata` | Extended song data | Includes lyrics and history text. Lyrics are copyrighted — do not reproduce them; summarize or link instead. |
| `venues` | Venue data | Special method — see below. |
| `jamcharts` | Jam chart entries | Fan-curated notable jams with commentary. Query by `slug` for one song's chart. |
| `attendance` | Show attendance | Special method — see below. |
| `reviews` | Show reviews | Special method. User-written reviews; treat as opinion, respect copyright (quote sparingly). |
| `users` | User data | Special method. Look up by username/uid, e.g. for a user's show attendance. |

## URL shapes

```
/v5/{method}.json                      # entire table — slow and huge, avoid naked calls
/v5/{method}/{id}.json                 # one record
/v5/{method}/{column}/{value}.json     # filter
```

Query params: `apikey` (required), `order_by`, `direction` (`asc` default / `desc`), `limit`, `callback` (JSONP wrap), `_noheader` (HTML format only). Formats: `.json`, `.html`, some methods `.xml`.

## Response envelope

JSON responses include a header with an error indicator and an `error_message`, plus a `data` array of row objects. Check for errors first; an invalid key, bad method, or empty result each report differently. An empty `data` array on a valid query means no matches (e.g., no show on that date).

## Setlist row fields (commonly used)

`showid`, `showdate`, `permalink`, `showyear`, `uniqueid`, `set` (`1`, `2`, `3`, `e`/`e2` for encores), `position` (order within the show), `songid`, `song`, `slug`, `trans_mark`, `footnote`, `isjamchart`, `jamchart_description`, `gap` (shows since last performance), `venue`, `venueid`, `city`, `state`, `country`, `artistid`, `artist_name`, `tourid`, `tour_name`, `reviews`, `rating`.

Transition marks (`trans_mark`) trail each song:
- `, ` — full stop between songs
- ` > ` — segue
- ` -> ` — seamless/jammed segue

Rebuild a setlist by grouping rows on `set`, sorting by `position`, and joining song names with their transition marks. Encore renders as "Encore:" (set `e`).

## Gaps and "last time played"

- The `songs` method and setlist rows both carry gap data; a song's `gap` on a setlist row is the number of Phish shows since its previous performance at that point in time.
- For current gap / LTP: query `/v5/setlists/slug/{slug}.json`, filter `artistid == 1`, take the max `showdate`. Cross-check against `/v5/songs` data when available.
- `exclude_from_stats` on shows flags non-canonical performances (e.g., some guest appearances) — respect it for stats questions.

## Special methods: attendance, reviews, users, venues

These have extra rules on Phish.net's side (rate limits, auth for user-specific writes, privacy expectations). Read-only lookups by column generally work like other methods, but:
- Don't enumerate or scrape user data in bulk.
- Attendance write operations require user-level auth (authkey) — out of scope for this skill; direct the user to Phish.net itself for check-ins.
- Reviews are copyrighted user writing — quote at most a short phrase with attribution.

## Rate limiting and caching

- API responses are server-cached ~5 minutes.
- Cache locally; refresh at least every 24 h (setlists change after post-show review).
- Rapid repeated requests can get an API key disabled. Prefer one broad query + local filtering over many narrow queries when reasonable (but never a naked `/setlists.json`).

## Attribution

Data is maintained by volunteers via Phish.net, a project of the non-profit Mockingbird Foundation. Credit "Phish.net / The Mockingbird Foundation" in anything user-facing built from this data. Usage is governed by their terms of use (linked from docs.phish.net).
