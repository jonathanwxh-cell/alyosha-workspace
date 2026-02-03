# Financial Tools Guide
**For Jon's Market Intelligence Stack**

---

## Quick Reference

| Tool | Status | Best For | Cost |
|------|--------|----------|------|
| **FMP** | ✅ Active | Quotes, profiles, peers, fundamentals | $149/mo (Ultimate) |
| **yfinance** | ✅ Active | Quick quotes, free backup | Free |
| **Benzinga** | ⏳ Needs key | News, ratings, earnings calendar | ~$300/mo |
| **Danelfin** | ⏳ Needs key | AI stock scores, screening | Varies |

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

## 4. Danelfin — AWAITING KEY

**Status:** ⏳ Client built, needs API key  
**Client:** `scripts/danelfin-client.py`  
**Docs:** https://danelfin.com/docs/api

### To Activate

```bash
echo "DANELFIN_API_KEY=your_key_here" > ~/.secure/danelfin.env
python3 scripts/danelfin-client.py score NVDA
```

### Planned Commands

```bash
# AI scores (1-10)
python3 scripts/danelfin-client.py score NVDA
python3 scripts/danelfin-client.py watchlist NVDA,AAPL,MSFT

# Screening
python3 scripts/danelfin-client.py top --aiscore-min 9

# Sectors
python3 scripts/danelfin-client.py sectors
```

### Score Breakdown

| Score | Meaning |
|-------|---------|
| **AI Score** | Overall composite (1-10) |
| **Fundamental** | Financial health |
| **Technical** | Price momentum/patterns |
| **Sentiment** | News/social sentiment |
| **Low Risk** | Volatility/drawdown risk |

### Best For
- **AI-powered stock screening**
- **Quick buy/sell signals**
- **Sector rotation ideas**
- **Risk assessment**

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
