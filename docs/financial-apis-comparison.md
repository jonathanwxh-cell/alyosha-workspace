# Financial APIs Comparison

*Research for market intelligence integration*

---

## Current Status

| API | Status | Key Available | Monthly Cost |
|-----|--------|---------------|--------------|
| **yfinance** | ✅ Working | N/A (free) | $0 |
| **FMP** | ✅ Working | Yes | Free tier (limited) |
| **Benzinga** | ❌ No key | Jon has account | ~$300/mo |
| **Danelfin** | ❌ No key | Jon has account | Varies by plan |

---

## 1. Financial Modeling Prep (FMP)

**Status:** ✅ Integrated

**What we have:**
- `scripts/fmp-client.py` — full Python client
- Quote, profile, key metrics, search
- Watchlist summaries, company snapshots

**Free tier limitations:**
- No earnings calendar
- No analyst estimates
- No stock news
- No screener
- Must fetch quotes individually (no bulk)

**To unlock more:** Upgrade to Starter ($14/mo) or Premium ($29/mo)

**Best for:** Basic quotes, company profiles, financial metrics

---

## 2. Benzinga

**Status:** ❌ Needs API key

**What it offers:**

### News API
- Real-time financial news
- Filter by ticker, category, date
- Sentiment data included
- Good for: News alerts, sentiment tracking

### Ratings API (Analyst Upgrades/Downgrades)
- Analyst actions with price targets
- Analyst accuracy metrics
- Good for: Tracking smart money signals

### Calendar APIs
- **Earnings:** Dates, EPS estimates, surprises
- **Dividends:** Ex-dates, amounts, yields
- **Economics:** FOMC, jobs, CPI dates
- **FDA:** Drug approvals calendar
- **IPO:** Upcoming IPOs
- **Conference Calls:** Scheduled calls

### Signals API
- Option activity alerts
- Unusual volume
- Insider transactions

**Pricing:** ~$300/mo for full API access

**Best for:** News, analyst ratings, calendars — real-time market intelligence

**Integration complexity:** Medium (REST API, Python client available on GitHub)

---

## 3. Danelfin

**Status:** ❌ Needs API key

**What it offers:**

### AI Scores (1-10)
- **AI Score:** Overall probability of beating market in 3 months
- **Fundamental Score:** Based on financial metrics
- **Technical Score:** Based on price/volume patterns
- **Sentiment Score:** Market sentiment analysis
- **Low Risk Score:** Risk assessment

### Key Features
- Historical score data for backtesting
- Sector/industry filtering
- Buy/sell track record
- Works for stocks AND ETFs

### API Plans
| Plan | Calls/month | Rate limit | Price |
|------|-------------|------------|-------|
| Basic | 1,000 | 120/min | ? |
| Expert | 10,000 | 240/min | ? |
| Elite | 100,000 | 1,200/min | ? |

**Best for:** Screening stocks, identifying high-probability setups

**Integration complexity:** Low (simple REST API)

---

## Comparison Matrix

| Feature | FMP | Benzinga | Danelfin |
|---------|-----|----------|----------|
| Real-time quotes | ✅ | ✅ | ❌ |
| Company profiles | ✅ | ✅ | ❌ |
| Financial metrics | ✅ | ✅ | ❌ |
| News | ❌ (paid) | ✅ | ❌ |
| Analyst ratings | ❌ | ✅ | ❌ |
| Earnings calendar | ❌ (paid) | ✅ | ❌ |
| AI stock scores | ❌ | ❌ | ✅ |
| Stock screening | ❌ (paid) | ❌ | ✅ |
| Historical data | ✅ | ✅ | ✅ |
| Python client | ✅ (custom) | ✅ (official) | ❌ (easy to build) |

---

## Recommended Integration Priority

### If budget allows ONE addition:
**Benzinga** — Most comprehensive for market intelligence (news + ratings + calendars)

### For screening/stock picking:
**Danelfin** — AI scores are unique value-add, not available elsewhere

### For basic upgrades:
**FMP Starter ($14/mo)** — Unlocks screener, earnings, analyst estimates

---

## Integration Roadmap

### Phase 1: Maximize Current Tools
- [x] FMP client built and working
- [x] yfinance for backup quotes
- [ ] Add more FMP endpoints (if they work on free tier)

### Phase 2: Benzinga (if key provided)
- Build `scripts/benzinga-client.py`
- Priority endpoints: Ratings, Earnings Calendar, News
- Integrate into morning briefings

### Phase 3: Danelfin (if key provided)
- Build `scripts/danelfin-client.py`
- Daily "Top AI Scores" scan
- Track score changes on watchlist

---

## Action Items for Jon

1. **Benzinga:** Do you have API credentials? Check cloud.benzinga.com
2. **Danelfin:** Is API access included in your subscription?
3. **FMP upgrade:** Worth $14/mo for earnings calendar + screener?

---

*Updated: 2026-02-02*
