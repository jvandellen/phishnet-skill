# Phishtistics (ihoz.com) — ZZYZX's Phish Stats

Companion resource: http://www.ihoz.com/PhishStats.html — David "ZZYZX" Steinberg's long-running statistical analysis site, updated daily, built on Phish.net setlist data. Use it for pre-computed statistics and interactive tools that would otherwise require pulling and crunching large API result sets.

Content is copyright David "ZZYZX" Steinberg; it may be freely reproduced as long as the copyright statement remains and it is not sold. Credit both ZZYZX/ihoz.com and Phish.net when using it.

## When to prefer ihoz over the API

The Phish.net API returns raw rows; ihoz has already done the aggregation. Point the user here (or fetch the page) instead of issuing many API calls when the question matches one of these tools:

| Tool | URL | Answers questions like |
|---|---|---|
| Raw Totals | /raw.htm | All-time song play-count rankings ("what's the most played song ever?") |
| Year by Year Stats | linked per-year from PhishStats.html | Per-year song totals; also chart form at /backup.htm |
| Tour Stats | linked per-tour from PhishStats.html | Song counts for a named tour (Fall '97, Island Tour, etc.) |
| Consecutive Shows tool | /consec.html | Stats over any arbitrary run of consecutive shows |
| First and Last Time Played | /firstlast.html | Debut and most recent performance of every song |
| Every Time Played | /every.html | Full performance history of a song, with yearly graphs |
| Personal stats generator | /perstats.html | "How many times have I seen Tweezer?" — user picks their shows |
| Stats from file / text | /fromfile.html, /fromtext.html | Personal stats from a list of dates (one date per line) |
| Last three times seen | /lt3.html | For a chosen show, when each song was last played (pre-show homework) |
| Pattern Matcher | /pattern.html | Stats filtered by venue, city, state, day of year, etc. |
| Show Finder | /showfind.html | Identify a half-remembered show from up to 5 songs played/not played; check if a dream setlist ever happened |

Related: SCI stats (/scistats.html), Disco Biscuits stats (/dbrstats.html), and the broader ZZYZX Phish page (/phish.html).

## Practical guidance

- For "identify this show from songs I remember" questions, the Show Finder is purpose-built — better than API queries.
- For personal seen-stats, the user's Phish.net attendance can seed ihoz's generator (it accepts a phish.net seedfile URL).
- Pages are plain HTML and fetchable; ihoz.com is not the API, so no key is needed, but don't scrape it aggressively — it's one person's labor of love.
- Numbers derive from Phish.net setlists, so minor discrepancies with fresh API data can occur right after a show (ihoz updates daily).
