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
- **Twitter/X scraper:** `apify/twitter-scraper` — weekly cron (Wed 10am SGT)
  - Queries: SpaceX IPO, AI capex, NVDA sentiment, world models
  - Budget: ~50 tweets/query, 4 queries = ~$2-4/week
- Default to Brave + web_fetch for research

### Financial Data
- **yfinance (FREE, working):** `scripts/stock-quote.py NVDA AAPL MSFT`
  - No API key needed, good for quick quotes
  - Installed and tested ✅
  
- **Financial Modeling Prep (FMP):** ✅ Configured
  - Docs: https://site.financialmodelingprep.com/developer/docs
  - Base URL: `https://financialmodelingprep.com/stable/`
  - Key: `.secure/fmp.env`
  - Note: Use `/stable/` endpoints (v3 deprecated)

- **Benzinga:** Jon has account, ~$300/mo for API
  - Docs: https://docs.benzinga.com
  - Best for: News, analyst ratings, earnings calendar
  - Status: ❌ No API key provided

- **Danelfin:** Jon has account, pricing varies
  - Docs: https://danelfin.com/docs/api
  - Best for: AI stock scores (1-10), screening
  - Status: ❌ No API key provided

Full research: `docs/financial-apis.md`

### Moltbook (AI Agent Social Network)
- **Profile:** https://moltbook.com/u/AlyoshaSG
- **Status:** Pending claim (needs Jon's tweet verification)
- **Credentials:** `~/.config/moltbook/credentials.json`
- **Skill files:** `skills/moltbook/`
- **Heartbeat:** Check every 4+ hours once claimed

Add whatever helps you do your job. This is your cheat sheet.
