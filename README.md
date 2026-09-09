# phishnet-skill

A [Claude skill](https://docs.claude.com) covering four Phish data sources: the [Phish.net API v5](https://docs.phish.net/) (setlists, shows, jam charts, gaps), [Phish.in](https://phish.in) (live audio archive — API v2 and MCP server), [ZZYZX's Phishtistics](http://www.ihoz.com/PhishStats.html) (pre-computed stats), and the YouTube Data API (video tracking).

Phish.net is a project of the non-profit [Mockingbird Foundation](https://mbird.org/). This skill just consumes their API; the data is theirs, built by volunteers. Credit them in anything you build with it.

## What's in here

```
phishnet/
├── SKILL.md                     # skill instructions (triggering, query patterns, etiquette)
├── references/
│   ├── api-reference.md         # Phish.net method/column reference, setlist semantics
│   ├── phishin.md               # Phish.in audio archive (API v2 + MCP server)
│   ├── phishstats.md            # ZZYZX Phishtistics (ihoz.com) tools
│   └── youtube.md               # YouTube Data API v3 video tracking
├── scripts/
│   ├── phishnet.py              # stdlib-only Phish.net CLI client
│   ├── phishin.py               # stdlib-only Phish.in audio client (no key)
│   └── phishtube.py             # stdlib-only YouTube video tracker
└── dist/
    └── phishnet.skill           # packaged skill, rebuilt by CI on every source push
```

## Install

### Claude.ai (web/mobile)

1. Download [`dist/phishnet.skill`](dist/phishnet.skill) — always current; CI rebuilds it on every source change.
2. In Claude.ai: **Settings → Capabilities → Skills → Upload skill**, and select the file.
3. Ask Claude a Phish question ("what did they play 12/31/99?") — the skill triggers automatically.

Note: claude.ai's sandbox can't reach the APIs directly. For live audio-archive queries there, also add Phish.in's MCP server as a custom connector: **Settings → Connectors → Add custom connector** → `https://phish.in/mcp`. For Phish.net queries, Claude will hand you curl commands and analyze the results you paste.

### Claude Code (full live API access — recommended)

Copy the skill into your personal skills directory:

```bash
git clone https://github.com/jvandellen/phishnet-skill.git
mkdir -p ~/.claude/skills
cp -r phishnet-skill ~/.claude/skills/phishnet
rm -rf ~/.claude/skills/phishnet/.git ~/.claude/skills/phishnet/dist
```

(Or symlink the clone: `ln -s "$PWD/phishnet-skill" ~/.claude/skills/phishnet` — Claude Code follows symlinks and picks up your edits.) For a single project instead, use `<repo>/.claude/skills/phishnet/`.

Then set keys in your environment as needed (see Setup below) and just ask — Claude Code queries the APIs directly.

## Setup

- **Phish.net** (setlists/gaps/jam charts): free key at https://phish.net/api/keys → `export PHISHNET_API_KEY=...`
- **Phish.in** (audio): no key needed.
- **YouTube** (video tracking): free Google Cloud key with "YouTube Data API v3" enabled → `export YOUTUBE_API_KEY=...`
- **ihoz.com** (stats): no key; it's a website, not an API.

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
