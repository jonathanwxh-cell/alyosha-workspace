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

- **Benzinga:** ⏳ **CLIENT READY — NEEDS KEY**
  - Client: `scripts/benzinga-client.py`
  - Commands: `news`, `ratings`, `earnings`, `watchlist`, `test`
  - Best for: Real-time news, analyst ratings, earnings calendar
  - Status: Waiting for API key (~$300/mo)
  - **To activate:** 
    ```bash
    echo "BENZINGA_API_KEY=your_key" > ~/.secure/benzinga.env
    python3 scripts/benzinga-client.py test
    ```

- **Danelfin:** ⏳ **CLIENT READY — NEEDS KEY**
  - Client: `scripts/danelfin-client.py`
  - Commands: `score`, `top`, `watchlist`, `sectors`
  - Best for: AI stock scores (1-10), screening top picks
  - Status: Waiting for API key
  - **To activate:**
    ```bash
    echo "DANELFIN_API_KEY=your_key" > ~/.secure/danelfin.env
    python3 scripts/danelfin-client.py score NVDA
    ```

**Comparison:** `docs/financial-apis-comparison.md`

### Transcript Analysis (internal tool)
- **Script:** `scripts/transcript-analyzer.py SYMBOL YEAR QUARTER`
- **Purpose:** Deep analysis for research, NOT for broadcast
- **Signals extracted:**
  - Loughran-McDonald sentiment (finance-specific lexicon)
  - Hedging vs certainty language ratio
  - Prepared remarks vs Q&A tone gap
  - Key phrase extraction
- **Usage:** Background research before earnings, historical tone comparisons
- **Research basis:** Berkeley/Georgia Tech papers on NLP earnings analysis

**Example:**
```bash
python3 scripts/transcript-analyzer.py NVDA 2025 Q3
python3 scripts/transcript-analyzer.py NVDA --compare  # Last 4 quarters
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
  - **COST CONSTRAINT:** Use sparingly — only when voice genuinely adds value
  - Good for: storytelling, kids content, occasional audio briefing
  - Skip for: regular updates, analysis, quick messages
- **ElevenLabs:** Not needed unless better voices wanted later

Add whatever helps you do your job. This is your cheat sheet.

### Security
- **fail2ban:** ✅ Installed, protecting SSH (5 retries, 1hr ban)
- **Secure serve:** Use `scripts/secure-serve.sh` for temp file hosting (binds localhost only)
- **Monthly audit:** Cron runs 1st of month, 3am SGT
- **Tunnel cleanup:** Kill cloudflared processes after use
