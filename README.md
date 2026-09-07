# phishnet-skill

A [Claude skill](https://docs.claude.com) for querying the [Phish.net API v5](https://docs.phish.net/) — setlists, shows, songs, jam charts, venues, gaps, and tour data.

Phish.net is a project of the non-profit [Mockingbird Foundation](https://mbird.org/). This skill just consumes their API; the data is theirs, built by volunteers. Credit them in anything you build with it.

## What's in here

```
phishnet/
├── SKILL.md                     # skill instructions (triggering, query patterns, etiquette)
├── references/
│   └── api-reference.md         # full method/column reference, setlist field semantics
└── scripts/
    └── phishnet.py              # stdlib-only CLI client
```

## Setup

1. Get a free API key at https://phish.net/api/keys (requires a Phish.net account).
2. `export PHISHNET_API_KEY=your_key`

## CLI usage

```bash
python scripts/phishnet.py setlists showdate 1997-11-22
python scripts/phishnet.py setlists slug tweezer --raw
python scripts/phishnet.py shows showyear 2026 --order-by showdate --limit 20
python scripts/phishnet.py jamcharts slug ghost --raw
python scripts/phishnet.py shows showyear 1994 --url-only   # print request URL, no call
```

Setlist queries render human-readable setlists with transition marks preserved (`>` segue, `->` jam segue); everything else prints JSON.

## As a Claude skill

Install the packaged `.skill` file (or point Claude Code at this directory). Claude will then handle questions like "what did Phish play at Hampton 11/22/97", "current gap on Harpua", or "jam chart versions of Tweezer from Fall '97" by querying the API directly.

Works fully in environments with network access (Claude Code, local agents). In sandboxed claude.ai chats, api.phish.net is unreachable, so the skill falls back to generating curl commands and analyzing pasted results.

## Notes

- Respect Phish.net's rate limits; cache locally and refresh within 24h.
- Setlist and show data includes side projects — filter `artistid == 1` for Phish proper.
- Not affiliated with Phish.net or the Mockingbird Foundation.
