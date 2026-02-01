# Financial APIs Reference

Research conducted: 2026-02-01

Jon has accounts with Benzinga, Danelfin, and potentially FMP. This doc covers integration status and options.

---

## 1. Financial Modeling Prep (FMP)

**Status:** Listed in TOOLS.md as configured, but API key not found in environment  
**Docs:** https://site.financialmodelingprep.com/developer/docs  
**Base URL:** `https://financialmodelingprep.com/stable/`

### Capabilities
- Real-time stock prices
- Financial statements (quarterly/annual)
- Historical prices (1min to daily)
- Stock screener
- Company search (by ticker, name, CIK, CUSIP, ISIN)
- SEC filings

### Authentication
```bash
# Header
apikey: YOUR_API_KEY

# OR URL param
?apikey=YOUR_API_KEY
```

### Example Endpoints
```bash
# Quote
GET /stable/quote/NVDA?apikey=KEY

# Income statement
GET /stable/income-statement/NVDA?period=annual&apikey=KEY

# Historical prices
GET /stable/historical-price-full/NVDA?apikey=KEY
```

### Action Needed
- [ ] Verify FMP API key exists and is accessible
- [ ] Add to environment if available

---

## 2. Benzinga

**Status:** Jon has account, no API key provided  
**Docs:** https://docs.benzinga.com  
**Pricing:** ~$300/month (based on Reddit reports)

### Capabilities
- News API (real-time, historical, by ticker)
- Signals API (analyst ratings, price targets)
- Calendar API (earnings, dividends, IPOs, FDA)
- Movers API
- Options data

### Key Features
- Python client: https://github.com/Benzinga/benzinga-python-client
- OpenAPI spec available
- Delta queries for real-time ingestion (`updatedSince` param)

### Authentication
```bash
# Header or query param
Authorization: Bearer YOUR_TOKEN
# or
?token=YOUR_TOKEN
```

### Example Endpoints
```bash
# News by ticker
GET /api/v2/news?tickers=NVDA&token=KEY

# Earnings calendar
GET /api/v2/calendar/earnings?token=KEY

# Analyst ratings
GET /api/v2/calendar/ratings?tickers=NVDA&token=KEY
```

### Action Needed
- [ ] Determine if Jon wants to pay ~$300/mo for API access
- [ ] If yes, get API key and configure

---

## 3. Danelfin

**Status:** Jon has account, no API key provided  
**Docs:** https://danelfin.com/docs/api  
**Pricing:** 
- Basic: $X/year (1,000 calls/month, 120/min)
- Expert: $X/year (10,000 calls/month, 240/min)
- Elite: $X/year (100,000 calls/month, 1,200/min)

### Capabilities
- AI Score (1-10 overall stock rating)
- Technical Score
- Fundamental Score
- Sentiment Score
- Low Risk Score
- Historical data since 2017
- US stocks and ETFs only

### Key Value
> "US-listed stocks with the highest AI Score (10/10) have outperformed the market by an average of +21.05% after 3 months (annualized alpha)"

### Authentication
```bash
# Header
x-api-key: YOUR_API_KEY
```

### Example Endpoints
```bash
# Get scores for a ticker
GET https://apirest.danelfin.com/ranking?ticker=NVDA

# Get top 100 stocks for a date
GET https://apirest.danelfin.com/ranking?date=2026-01-31

# Filter by minimum AI score
GET https://apirest.danelfin.com/ranking?date=2026-01-31&aiscore_min=8
```

### Response Format
```json
{
  "2026-01-31": {
    "aiscore": 8,
    "fundamental": 7,
    "technical": 9,
    "sentiment": 6,
    "low_risk": 5
  }
}
```

### Action Needed
- [ ] Check if Jon has API access or just web account
- [ ] If API available, get key and configure
- [ ] Most valuable for: stock screening, building watchlists

---

## 4. Other Free Options

### Yahoo Finance (via yfinance)
```bash
pip install yfinance
```
```python
import yfinance as yf
nvda = yf.Ticker("NVDA")
nvda.info  # Company info
nvda.history(period="1mo")  # Price history
```
- Free, no API key
- Rate limits apply
- Good for basic quotes and history

### Alpha Vantage
- Free tier: 25 requests/day
- Paid: starts at $50/month
- Good for technical indicators

---

## Recommended Priority

1. **FMP** - Verify if key exists, most versatile free/cheap option
2. **Danelfin** - Best bang for buck if Jon wants AI scores for screening
3. **Benzinga** - Only if news/signals are critical ($300/mo is steep)
4. **yfinance** - Use for quick quotes when other APIs unavailable

---

## Integration Checklist

| API | Key Available | Configured | Tested |
|-----|--------------|------------|--------|
| FMP | ❓ Need to verify | ❌ | ❌ |
| Benzinga | ❌ Not provided | ❌ | ❌ |
| Danelfin | ❌ Not provided | ❌ | ❌ |
| yfinance | ✅ No key needed | ✅ | ❌ |

---

*Next step: Ask Jon which APIs he has active keys for*
