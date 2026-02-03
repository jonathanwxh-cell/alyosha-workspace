# Financial APIs Comparison

*Last updated: 2026-02-02*

## Quick Reference

| API | Status | Cost | Best For |
|-----|--------|------|----------|
| **FMP** | ✅ Active | $149/mo (Ultimate) | Full-stack financial data |
| **yfinance** | ✅ Active | Free | Quick quotes, basic data |
| **Benzinga** | ⏳ Need key | ~$300/mo | News, ratings, calendars |
| **Danelfin** | ⏳ Need key | Varies | AI stock scores |

---

## 1. Financial Modeling Prep (FMP) ✅

**Status:** Fully integrated and working

**Tier:** Ultimate ($149/mo) — all features unlocked

**Client:** `scripts/fmp-client.py`

### Endpoints Available

| Endpoint | Command | Notes |
|----------|---------|-------|
| Real-time quotes | `fmp-client.py quote NVDA` | Global markets |
| Company profile | `fmp-client.py profile NVDA` | Company details |
| Key metrics | `fmp-client.py metrics NVDA` | Valuation ratios |
| Earnings transcripts | `fmp-client.py transcript NVDA 2025 Q3` | Full text |
| Market movers | `fmp-client.py movers` | Gainers/losers |
| Watchlist snapshot | `fmp-client.py watchlist NVDA,AMD` | Multi-quote |

### Unique Features
- Earnings call transcripts (full text)
- Global exchange coverage (.T, .L, .SI)
- Institutional ownership
- Insider trading data
- SEC filings

### Rate Limits
- Generous on Ultimate tier
- No known issues

---

## 2. yfinance (Free) ✅

**Status:** Working

**Client:** `scripts/stock-quote.py`

### Features
- Basic quotes
- Historical prices
- Options chains
- Basic fundamentals

### Limitations
- Yahoo's ToS technically discourages scraping
- Rate limits on heavy use
- Data occasionally delayed

### Use When
- Quick quotes without API cost
- Historical price analysis
- Prototype before using paid APIs

---

## 3. Benzinga ⏳

**Status:** Client ready, waiting for API key

**Cost:** ~$300/mo (Jon's subscription)

**Client:** `scripts/benzinga-client.py`

### Endpoints Available

| Endpoint | Command | Best For |
|----------|---------|----------|
| News | `benzinga-client.py news NVDA` | Recent headlines |
| Ratings | `benzinga-client.py ratings NVDA` | Analyst actions |
| Earnings calendar | `benzinga-client.py earnings NVDA` | Upcoming reports |
| Watchlist intel | `benzinga-client.py watchlist NVDA,AMD,TSM` | Combined view |

### Unique Features
- **Real-time news** with sentiment signals
- **Analyst ratings** with price targets
- **Earnings surprises** historical data
- **Guidance changes** tracking
- **IPO calendar**
- **Economic events** calendar

### Why Use It
Benzinga is the **news and sentiment** specialist. Use for:
- Breaking news alerts
- Analyst rating changes
- Pre-earnings research
- Market sentiment

### Setup
```bash
# Create key file
echo "BENZINGA_API_KEY=your_key_here" > ~/.secure/benzinga.env
chmod 600 ~/.secure/benzinga.env

# Test
python3 scripts/benzinga-client.py test
```

---

## 4. Danelfin ⏳

**Status:** Client ready, waiting for API key

**Cost:** Varies by plan

**Client:** `scripts/danelfin-client.py`

### Endpoints Available

| Endpoint | Command | Returns |
|----------|---------|---------|
| Stock score | `danelfin-client.py score NVDA` | AI score (1-10) |
| Top picks | `danelfin-client.py top --aiscore-min 9` | Best-rated stocks |
| Watchlist | `danelfin-client.py watchlist NVDA,AMD` | Multi-score view |
| Sectors | `danelfin-client.py sectors` | Sector performance |

### Score Components
- **AI Score (1-10):** Overall rating
- **Fundamental:** Financial health
- **Technical:** Price patterns
- **Sentiment:** Market mood
- **Low Risk:** Stability

### Why Use It
Danelfin provides **AI-powered stock scoring**. Use for:
- Screening for high-probability trades
- Quick sentiment check
- Ranking watchlist by AI score
- Finding momentum plays

### Setup
```bash
# Create key file
echo "DANELFIN_API_KEY=your_key_here" > ~/.secure/danelfin.env
chmod 600 ~/.secure/danelfin.env

# Test
python3 scripts/danelfin-client.py score AAPL
```

---

## API Combination Strategy

### Daily Workflow
1. **Morning:** FMP for watchlist prices + Benzinga for overnight news
2. **Pre-market:** Danelfin scores for momentum picks
3. **During day:** yfinance for quick quotes (free)
4. **Research:** FMP transcripts + Benzinga ratings

### Event-Driven
- **Earnings approaching:** FMP historical + Benzinga estimates
- **News breaks:** Benzinga real-time
- **Screening:** Danelfin top picks + FMP fundamentals
- **Deep dive:** FMP full profile + transcripts

### Cost Optimization
- Use yfinance for basic quotes (free)
- Reserve FMP for detailed research (already paid)
- Benzinga for news-heavy days
- Danelfin for quick screening

---

## Keys Needed

```bash
# Already configured
~/.secure/fmp.env         # FMP Ultimate

# Need from Jon
~/.secure/benzinga.env    # Benzinga API key
~/.secure/danelfin.env    # Danelfin API key
```

To get keys:
1. **Benzinga:** Login to cloud.benzinga.com → API Keys
2. **Danelfin:** Check subscription → API access

---

## Quick Test Commands

```bash
# FMP (working)
python3 scripts/fmp-client.py quote NVDA

# yfinance (working)
python3 scripts/stock-quote.py NVDA

# Benzinga (needs key)
python3 scripts/benzinga-client.py test

# Danelfin (needs key)  
python3 scripts/danelfin-client.py score NVDA
```
