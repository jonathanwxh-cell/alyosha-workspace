# Financial Tools Status

**Updated:** 2026-02-04

## Active APIs (Keys Configured)

### 1. FMP (Financial Modeling Prep) ✅ ULTIMATE TIER
**Key:** `~/.secure/fmp.env`
**Cost:** ~$149/mo
**Client:** `scripts/fmp-client.py`

**Working Commands:**
```bash
python3 scripts/fmp-client.py quote NVDA AAPL
python3 scripts/fmp-client.py profile NVDA
python3 scripts/fmp-client.py metrics NVDA
python3 scripts/fmp-client.py watchlist NVDA,AAPL,MSFT
python3 scripts/fmp-client.py gainers
python3 scripts/fmp-client.py losers
python3 scripts/fmp-client.py sectors
python3 scripts/fmp-client.py search nvidia
```

**Best for:** Real-time quotes, company profiles, key metrics, market movers

---

### 2. Finnhub ✅ FREE TIER
**Key:** `~/.secure/finnhub.env`
**Cost:** Free (60 calls/min)
**Client:** `scripts/finnhub-client.py`

**Working Commands:**
```bash
python3 scripts/finnhub-client.py recommend NVDA    # Analyst recommendations
python3 scripts/finnhub-client.py insider NVDA      # Insider transactions
python3 scripts/finnhub-client.py news NVDA         # Company news
```

**Best for:** Analyst ratings, insider trading, sentiment (premium)

**Sample output (NVDA recommendations):**
- Strong Buy: 25, Buy: 39, Hold: 7, Sell: 1, Strong Sell: 0

---

## Ready But Need Keys

### 3. Benzinga ⏳ CLIENT READY
**Key needed:** `~/.secure/benzinga.env`
**Cost:** ~$300/mo OR **FREE via AWS Marketplace** (basic news only)
**Client:** `scripts/benzinga-client.py`

**Commands (once key added):**
```bash
python3 scripts/benzinga-client.py news NVDA
python3 scripts/benzinga-client.py ratings NVDA
python3 scripts/benzinga-client.py earnings NVDA
python3 scripts/benzinga-client.py movers
python3 scripts/benzinga-client.py calendar --type earnings
```

**Best for:** Real-time news, analyst ratings, earnings calendar

**FREE OPTION:** AWS Marketplace has Benzinga Basic Financial News API (free tier)
- https://aws.amazon.com/marketplace/pp/prodview-xwgvhwowjmw3g

---

### 4. Danelfin ⏳ CLIENT READY
**Key needed:** `~/.secure/danelfin.env`
**Cost:** Paid plans only (API access ~$50-200/mo)
**Client:** `scripts/danelfin-client.py`

**Commands (once key added):**
```bash
python3 scripts/danelfin-client.py score NVDA       # AI score 1-10
python3 scripts/danelfin-client.py top              # Top scoring stocks
python3 scripts/danelfin-client.py sectors          # Sector analysis
python3 scripts/danelfin-client.py watchlist NVDA,AAPL
```

**Best for:** AI-generated stock scores, screening

---

## Free APIs Worth Adding

### Alpha Vantage (FREE)
- Real-time + historical prices
- 50+ technical indicators
- News sentiment (AI-powered)
- Free tier: 25 calls/day
- https://www.alphavantage.co/

### EODHD (FREE TIER)
- Historical EOD prices
- 150,000+ tickers globally
- Options data
- https://eodhd.com/

### yfinance (FREE - NO KEY)
- Already using as backup: `scripts/stock-quote.py`
- No rate limits (unofficial Yahoo scraper)
- Good for quick quotes

---

## Current Coverage

| Need | Tool | Status |
|------|------|--------|
| Real-time quotes | FMP, yfinance | ✅ |
| Company fundamentals | FMP | ✅ |
| Analyst ratings | Finnhub | ✅ |
| Insider trading | Finnhub | ✅ |
| Market movers | FMP | ✅ |
| News | (need Benzinga) | ⏳ |
| Earnings calendar | (need Benzinga) | ⏳ |
| AI stock scores | (need Danelfin) | ⏳ |
| Technical indicators | (could add Alpha Vantage) | 📋 |

---

## Recommendations

1. **Get Benzinga Free Tier** via AWS Marketplace for news
2. **Add Alpha Vantage** for technical indicators + sentiment
3. **Danelfin** only if want AI scores (paid)
