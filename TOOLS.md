# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

### Web / Search
- **Primary:** Brave Search (`web_search`)
- **Apify:** ✅ Configured — but EXPENSIVE. Use as last resort only.
  - Try alternatives first: web search, RSS, public page fetches
  - For social media: search food blogs/aggregators that compile trends instead of direct scraping
  - OK for high-value targeted scrapes, NOT for broad discovery
- **r/singapore scraper:** `scripts/reddit-sg.sh` — uses Apify (use sparingly)
- Default to Brave + web_fetch for research

Add whatever helps you do your job. This is your cheat sheet.
