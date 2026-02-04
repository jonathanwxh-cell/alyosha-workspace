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

**Full guide:** `docs/financial-tools-guide.md`

- **FMP (Financial Modeling Prep):** ✅ **ACTIVE — ULTIMATE TIER** 
  - Client: `scripts/fmp-client.py`
  - Commands: `quote`, `profile`, `metrics`, `watchlist`, `snapshot`, `movers`, `gainers`, `losers`, `sectors`, `search`
  - Key: `~/.secure/fmp.env`
  - **Tier: Ultimate ($149/mo)**
  - **Working features:**
    - Real-time quotes (global markets)
    - Company profiles & key metrics
    - Stock peers comparison
    - Market movers (gainers/losers)
    - Sector performance
  - **Note:** FMP deprecated v3/v4 APIs in Aug 2025. Using stable API.
  - Docs: https://site.financialmodelingprep.com/developer/docs

- **yfinance (FREE backup):** `scripts/stock-quote.py NVDA AAPL MSFT`
  - No API key needed, good for quick quotes
  - Use as backup when FMP unavailable

- **Benzinga:** ❌ **NOT NEEDED**
  - Client exists: `scripts/benzinga-client.py`
  - Decision: Evaluated, not worth ~$300/mo. FMP + free sources sufficient.

- **Danelfin:** ❌ **NOT NEEDED**
  - Client exists: `scripts/danelfin-client.py`
  - Decision: Evaluated, not needed. Own analysis framework works.

**Comparison:** `docs/financial-apis-comparison.md`

### Stock Analysis (Sonnet-powered)
- **Skill:** `skills/stock-analysis/`
- **Scripts:** 
  - `scripts/transcript-compare.py TICKER` — 4-quarter tone comparison
  - `scripts/deep-analyzer.py TICKER` — qualitative signals
  - `scripts/finnhub-client.py insider/recommend TICKER` — alt data
- **Queue:** `python3 scripts/queue-analysis.py TICKER` — adds to Sonnet analysis queue
- **Cron:** Mon/Thu 10am SGT — processes queue, shows model used
- **Output:** Structured analysis with model attribution

**Example:**
```bash
python3 scripts/queue-analysis.py NVDA SE AAPL  # Queue for analysis
python3 scripts/transcript-compare.py NVDA      # Instant local analysis
```

### Moltbook (AI Agent Social Network)
- **Profile:** https://moltbook.com/u/AlyoshaSG
- **Status:** Pending claim (needs Jon's tweet verification)
- **Credentials:** `~/.config/moltbook/credentials.json`
- **Skill files:** `skills/moltbook/`
- **Heartbeat:** Check every 4+ hours once claimed

### Audio / Sonification
- **Format:** MP3 (not OGG — Telegram chokes on OGG)
- **Scripts:** `scripts/sonify.py`, `scripts/market-sonify.py`
- **Output dir:** `creative/sonification/`
- **Data-to-audio synth:** Built 2026-02-03
  - Price → pitch (A3-A5), Volume → amplitude + noise
  - scipy.io.wavfile + numpy, ffmpeg for MP3 conversion
  - Example: `creative/sonification/nvda-deepseek-crash.mp3`
- **PIL data visualization:** Built 2026-02-03
  - Pixel-level chart rendering (no matplotlib needed)
  - Price lines, fills, annotations, grids
  - Example: `creative/nvda-crash-pil.png`
- **Interactive HTML/JS apps:** Built 2026-02-03
  - Self-contained web visualizations (no external libs)
  - Canvas charts, tooltips, animations
  - Headless Chrome for screenshots
  - Example: `creative/nvda-crash-interactive.html`

### TTS / Voice
- **OpenAI TTS:** ✅ Enabled (manual mode)
  - Provider: OpenAI, Model: tts-1, Voice: nova
  - **BUDGET: $5/month** (set 2026-02-04)
  - Pricing: $15/1M chars (~$0.02 per 2-min clip)
  - **Jon prefers text** — only suggest TTS when situation really needs it
  - OK for: kids stories, special occasions
  - Skip for: regular updates, analysis, quick messages
  - Track usage in memory/audio-usage.jsonl

### Podcast Transcription
- **OpenAI Whisper:** ✅ Enabled
  - Skill: openai-whisper-api
  - **BUDGET: $10/month** (set 2026-02-04)
  - Pricing: $0.006/min (~$0.36/hr, ~$1.44 for 4hr podcast)
  - Covers: ~28 hours/month (~7 long podcasts)
  - Flow: `memory/flows/podcast-transcription-flow.md`
  - Track usage in memory/whisper-usage.jsonl

Add whatever helps you do your job. This is your cheat sheet.

### Memory Blocks
- **Manager:** `python3 scripts/memory-blocks.py [status|check]`
- **Location:** `memory/blocks/`
- **Blocks:** human.md (2000), persona.md (1000), task-state.md (1500), knowledge.md (3000)
- **Purpose:** Structured, size-limited context (MemGPT-inspired)
- **Self-editable:** Update as you learn, prune when approaching limits

### Investment Thesis Tracker
- **Thesis Tracker:** `scripts/thesis-tracker.py` — track investment theses and learn from outcomes
  ```bash
  python3 scripts/thesis-tracker.py add TICKER                    # Interactive add
  python3 scripts/thesis-tracker.py add TICKER --quick "thesis" --conviction 7
  python3 scripts/thesis-tracker.py list                          # All active theses
  python3 scripts/thesis-tracker.py show TICKER                   # Detail + current price
  python3 scripts/thesis-tracker.py check                         # Alerts (big moves, stale, conviction mismatch)
  python3 scripts/thesis-tracker.py close TICKER                  # Close and record lesson
  python3 scripts/thesis-tracker.py review                        # Win rate, avg return, lessons
  python3 scripts/thesis-tracker.py remind                        # Stale theses (>30 days)
  ```
- **Key feature:** Asks "What would change your view?" when adding — creates accountability
- **Storage:** `memory/investment-theses.json` (active), `memory/thesis-outcomes.jsonl` (closed)

### Position Tracking
- **Position Tracker:** `python3 scripts/position-tracker.py [check|alerts|summary]`
  - Scans `memory/trade-journal.jsonl` for open positions
  - Parses option details from notes (e.g., "671P exp 2026-02-11")
  - Alerts on expiry (7d/3d/1d), ITM/OTM status
  - Cron: Daily 8pm SGT
- **Current positions:** Check with `position-tracker.py check`

### Trading Behavior Tracking
- **Trade Journal:** `scripts/trade-journal.py` — log positions, track outcomes
  ```bash
  python3 scripts/trade-journal.py add NVDA --type option --direction long --notes "earnings play"
  python3 scripts/trade-journal.py close NVDA --outcome win --pnl 25 --lesson "held through volatility"
  python3 scripts/trade-journal.py stats     # Win rate, patterns
  python3 scripts/trade-journal.py patterns  # Day-of-week, time patterns
  ```
- **Speculation Guard:** `scripts/speculation-guard.py` — detect boredom patterns
  ```bash
  python3 scripts/speculation-guard.py log "thinking about SPY puts"
  python3 scripts/speculation-guard.py check   # Analyze recent activity
  python3 scripts/speculation-guard.py suggest # Get engaging alternative
  ```
- **Purpose:** Jon speculates when bored. These tools track patterns and suggest redirects.
- **When to use:** Log when Jon mentions options, shorts, crash bets, leveraged trades

### Security
- **fail2ban:** ✅ Installed, protecting SSH (5 retries, 1hr ban)
- **Secure serve:** Use `scripts/secure-serve.sh` for temp file hosting (binds localhost only)
- **Monthly audit:** Cron runs 1st of month, 3am SGT
- **Tunnel cleanup:** Kill cloudflared processes after use
