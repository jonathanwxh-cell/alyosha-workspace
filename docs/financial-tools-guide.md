# Financial Tools Guide
**For Jon's Market Intelligence Stack**

---

## Quick Reference

| Tool | Status | Best For | Cost |
|------|--------|----------|------|
| **FMP** | ✅ Active | Quotes, profiles, peers, fundamentals | $149/mo (Ultimate) |
| **Finnhub** | ✅ Active | News, insider trading, recommendations | Free |
| **Alpha Vantage** | ✅ Key ready | Technical indicators, fundamentals | Free |
| **yfinance** | ✅ Active | Quick quotes, free backup | Free |
| **Danelfin** | ⏳ Needs key | AI stock scores, screening | ~$20-200/mo |
| **Benzinga** | ⏳ Needs key | News, ratings, earnings calendar | ~$300/mo |

---

## 1. FMP (Financial Modeling Prep) — PRIMARY

**Status:** ✅ Active, Ultimate Tier  
**Client:** `scripts/fmp-client.py`  
**Key:** `~/.secure/fmp.env`

### Working Commands

```bash
# Quotes
python3 scripts/fmp-client.py quote NVDA AAPL MSFT
python3 scripts/fmp-client.py watchlist NVDA,AMD,AVGO,SMCI

# Company info
python3 scripts/fmp-client.py profile NVDA
python3 scripts/fmp-client.py metrics NVDA
python3 scripts/fmp-client.py snapshot NVDA   # Full summary

# Market movers
python3 scripts/fmp-client.py gainers
python3 scripts/fmp-client.py losers
python3 scripts/fmp-client.py movers          # Combined summary
python3 scripts/fmp-client.py sectors

# Search
python3 scripts/fmp-client.py search nvidia
```

### FMP Features by Tier

| Feature | Free | Starter | Ultimate ✅ |
|---------|------|---------|-------------|
| Real-time quotes | ✅ | ✅ | ✅ |
| Company profiles | ✅ | ✅ | ✅ |
| Financial statements | ✅ | ✅ | ✅ |
| Key metrics | ✅ | ✅ | ✅ |
| Stock peers | ✅ | ✅ | ✅ |
| Earnings transcripts | ❌ | ❌ | ✅ |
| Institutional holders | ❌ | ✅ | ✅ |
| Insider trading | ❌ | ✅ | ✅ |
| News API | ❌ | ✅ | ✅ |

### Programmatic Usage

```python
from scripts import fmp_client as fmp

# Initialize
fmp.init()

# Get data
quotes = fmp.quote(['NVDA', 'AMD'])
profile = fmp.profile('NVDA')
peers = fmp.stock_peers('NVDA')
metrics = fmp.key_metrics('NVDA')

# Formatted output
print(fmp.watchlist_summary(['NVDA', 'AMD', 'AVGO']))
print(fmp.market_movers_summary())
print(fmp.company_snapshot('NVDA'))
```

---

## 2. yfinance — FREE BACKUP

**Status:** ✅ Active  
**Client:** `scripts/stock-quote.py`  
**Cost:** Free (no API key needed)

### Usage

```bash
python3 scripts/stock-quote.py NVDA AAPL MSFT
```

### Programmatic Usage

```python
import yfinance as yf

# Single stock
nvda = yf.Ticker("NVDA")
print(nvda.info['currentPrice'])
print(nvda.info['marketCap'])

# Multiple stocks
tickers = yf.Tickers("NVDA AMD AAPL")
for symbol in tickers.tickers:
    print(f"{symbol}: ${tickers.tickers[symbol].info['currentPrice']}")
```

### Best For
- Quick quotes when FMP rate-limited
- Historical price data
- Options chains
- Free tier backup

---

## 3. Benzinga — AWAITING KEY

**Status:** ⏳ Client built, needs API key  
**Client:** `scripts/benzinga-client.py`  
**Docs:** https://docs.benzinga.com

### To Activate

```bash
echo "BENZINGA_API_KEY=your_key_here" > ~/.secure/benzinga.env
python3 scripts/benzinga-client.py test
```

### Planned Commands

```bash
# News (their strongest feature)
python3 scripts/benzinga-client.py news NVDA
python3 scripts/benzinga-client.py watchlist NVDA,AAPL,MSFT

# Analyst ratings
python3 scripts/benzinga-client.py ratings NVDA

# Earnings calendar
python3 scripts/benzinga-client.py earnings NVDA
python3 scripts/benzinga-client.py calendar --type earnings
```

### Best For
- **Real-time news** (faster than FMP)
- **Analyst ratings** with price targets
- **Earnings calendar** with estimates
- **Economic calendar**

---

## 4. Finnhub — FREE TIER

**Status:** ✅ Active  
**Client:** `scripts/finnhub-client.py`  
**Key:** `~/.secure/finnhub.env`  
**Docs:** https://finnhub.io/docs/api

### Usage

```bash
# Quotes & news
python3 scripts/finnhub-client.py quote NVDA
python3 scripts/finnhub-client.py news NVDA

# Analyst info
python3 scripts/finnhub-client.py recommend NVDA    # Analyst recommendations
python3 scripts/finnhub-client.py sentiment NVDA    # News sentiment score

# Insider activity
python3 scripts/finnhub-client.py insider NVDA

# Earnings
python3 scripts/finnhub-client.py earnings NVDA

# Multi-ticker
python3 scripts/finnhub-client.py watchlist NVDA,AAPL,MSFT
```

### Best For
- **Insider trading data** (free, good quality)
- **Analyst recommendations** (buy/hold/sell counts)
- **News sentiment scores**
- **Peer companies**

---

## 5. Danelfin — AWAITING KEY

**Status:** ⏳ Client built, needs API key  
**Client:** `scripts/danelfin-client.py`  
**Docs:** https://danelfin.com/docs/api

### To Activate

```bash
echo "DANELFIN_API_KEY=your_key_here" > ~/.secure/danelfin.env
python3 scripts/danelfin-client.py score NVDA
```

### Commands

```bash
# Get AI scores for a ticker
python3 scripts/danelfin-client.py score NVDA

# Score history (30 days)
python3 scripts/danelfin-client.py history NVDA 30

# Top stocks by AI Score
python3 scripts/danelfin-client.py top              # Top 100 today
python3 scripts/danelfin-client.py top10            # Perfect AI Score 10

# Screening
python3 scripts/danelfin-client.py screen 8         # AI Score >= 8
python3 scripts/danelfin-client.py trading          # AI >= 7, Low Risk >= 6

# Sectors
python3 scripts/danelfin-client.py sectors          # List all
python3 scripts/danelfin-client.py sector energy    # Sector history

# Multiple tickers
python3 scripts/danelfin-client.py watchlist NVDA,RTX,UNH
```

### Score Breakdown

| Score | Meaning | Signal |
|-------|---------|--------|
| **AI Score** | Overall composite (1-10) | 8-10 = Strong Buy, 1-3 = Sell |
| **Fundamental** | Financial health | Earnings, margins, growth |
| **Technical** | Price momentum/patterns | Charts, trends |
| **Sentiment** | News/social sentiment | Market buzz |
| **Low Risk** | Volatility/drawdown | Higher = safer |

### Why Danelfin?
- **Track record:** AI Score 10 stocks outperform S&P 500 by ~21% (annualized)
- **Historical data:** Back to 2017 for backtesting
- **Simple signals:** Just check the score, act on 8+

### Best For
- **AI-powered stock screening** (integrates with trading goal)
- **Quick buy/sell signals**
- **Sector rotation ideas**
- **Risk assessment**

### Pricing
| Plan | Calls/mo | Cost |
|------|----------|------|
| Basic | 1,000 | ~$20/mo |
| Expert | 10,000 | ~$50/mo |
| Elite | 100,000 | ~$200/mo |

---

## 5. Transcript Analysis — INTERNAL TOOL

**Status:** ✅ Active  
**Client:** `scripts/transcript-analyzer.py`

### Usage

```bash
# Analyze single transcript
python3 scripts/transcript-analyzer.py NVDA 2025 Q3

# Compare across quarters
python3 scripts/transcript-analyzer.py NVDA --compare
```

### What It Extracts
- Loughran-McDonald sentiment (finance-specific lexicon)
- Hedging vs certainty language ratio
- Prepared remarks vs Q&A tone gap
- Key phrase extraction
- Quarter-over-quarter tone changes

### Best For
- Pre-earnings research
- Historical sentiment comparison
- Detecting management confidence shifts

---

## Integration Patterns

### Daily Watchlist Check

```bash
# Quick morning check
python3 scripts/fmp-client.py watchlist NVDA,AMD,AVGO,SMCI,TSM

# With movers context
python3 scripts/fmp-client.py movers
```

### Pre-Earnings Research

```bash
# 1. Check earnings date
python3 scripts/fmp-client.py earnings NVDA

# 2. Review transcript history (when Benzinga active)
python3 scripts/transcript-analyzer.py NVDA --compare

# 3. Check AI score (when Danelfin active)
python3 scripts/danelfin-client.py score NVDA
```

### News Monitoring

```bash
# FMP news (if available)
python3 scripts/fmp-client.py news NVDA

# Benzinga news (when active - faster/better)
python3 scripts/benzinga-client.py news NVDA
```

---

## Cron Integration

Several crons use these tools:

| Cron | Tool | Purpose |
|------|------|---------|
| Morning Watchlist | FMP | Daily price snapshot |
| Watchlist Alerts | FMP | Price threshold alerts |
| Earnings Week Ahead | FMP | Upcoming earnings check |
| NVDA Dashboard | FMP | Earnings prep data |

---

## Next Steps

1. **Get Benzinga key** → Activate news/ratings
2. **Get Danelfin key** → Activate AI scores
3. **Build unified intel CLI** → Single command for full brief

---

## Troubleshooting

### FMP "Legacy Endpoint" Error
FMP deprecated v3/v4 endpoints in Aug 2025. Use stable API:
- Base URL: `https://financialmodelingprep.com/stable`
- Check docs: https://site.financialmodelingprep.com/developer/docs

### Rate Limits
- FMP Ultimate: Generous, rarely hit
- Benzinga: Varies by plan
- yfinance: Unofficial, can be throttled

### Missing Data
- Some endpoints return `[]` for certain tickers
- Check ticker format (e.g., TSM vs 2330.TW)
- Try alternative source (yfinance as backup)

---

*Last updated: 2026-02-02*
