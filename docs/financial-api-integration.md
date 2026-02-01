# Financial API Integration Guide

*Status: Research complete. Awaiting API keys from Jon.*

---

## Currently Working ✅

### 1. yfinance (FREE)
- **Status:** Installed, working
- **Use:** `scripts/stock-quote.py NVDA AAPL`
- **Provides:** Price, volume, fundamentals, historical data, earnings dates
- **Limits:** Rate limited but generous for our use

### 2. Financial Modeling Prep (FMP)
- **Status:** API key configured in `.secure/fmp.env`
- **Use:** `scripts/fmp-quote.sh NVDA`
- **Provides:** Fundamentals, financials, estimates, news
- **Docs:** https://site.financialmodelingprep.com/developer/docs

---

## Ready to Integrate (Need API Keys)

### 3. Benzinga (~$300/mo)
**Jon has account but no API key provided yet**

**What it offers:**
- **News API:** Real-time financial news, filtered by ticker
- **Analyst Ratings API:** Upgrades, downgrades, price targets, analyst actions
- **Earnings Calendar:** Upcoming earnings, estimates, surprises
- **SEC Filings:** 8-K, 10-Q, 10-K alerts

**Best for:**
- Real-time news sentiment for NVDA dashboard
- Tracking analyst rating changes
- Earnings calendar integration

**Integration plan:**
```python
# benzinga_connector.py (ready to build once key provided)
import requests

BENZINGA_API_KEY = os.environ.get('BENZINGA_API_KEY')
BASE_URL = 'https://api.benzinga.com/api/v2'

def get_ratings(ticker, days=30):
    """Get analyst ratings for a ticker"""
    url = f"{BASE_URL}/calendar/ratings"
    params = {
        'token': BENZINGA_API_KEY,
        'symbols': ticker,
        'date_from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    }
    return requests.get(url, params=params).json()

def get_news(ticker, limit=10):
    """Get recent news for a ticker"""
    url = f"{BASE_URL}/news"
    params = {
        'token': BENZINGA_API_KEY,
        'tickers': ticker,
        'pageSize': limit
    }
    return requests.get(url, params=params).json()
```

**Value add to NVDA dashboard:**
- Live analyst ratings feed
- Breaking news alerts
- Earnings surprise history

---

### 4. Danelfin (AI Stock Scores)
**Jon has account but no API key provided yet**

**What it offers:**
- **AI Score (1-10):** Probability of beating market in 3 months
- **Trade Ideas:** Buy/sell signals with 60%+ historical win rate
- **Explainable AI:** Transparent alpha signals, not black box
- **Portfolio Tracking:** AI score monitoring for holdings

**Key stats from their site:**
- AI Score 10/10 stocks: +21% annualized alpha (since 2017)
- AI Score 1/10 stocks: -33% annualized alpha
- Best Stocks strategy: +376% vs S&P +166% (2017-2025)

**Best for:**
- Stock screening with probability edge
- Validating thesis with AI signals
- Portfolio optimization

**Integration plan:**
```python
# danelfin_connector.py (ready to build once key provided)
# Note: Need to check their API docs for exact endpoints

def get_ai_score(ticker):
    """Get Danelfin AI score for a ticker"""
    # API endpoint TBD - may need to scrape or use their data export
    pass

def get_trade_ideas():
    """Get current AI-generated trade ideas"""
    pass
```

**Value add:**
- Add AI Score to NVDA dashboard
- Daily screening for high-score opportunities
- Signal validation for thesis

---

## Integration Priority

| API | Value | Cost | Priority | Blocker |
|-----|-------|------|----------|---------|
| Benzinga | High (news, ratings) | ~$300/mo | 1 | Need API key |
| Danelfin | High (AI scores) | ? | 2 | Need API key |
| FMP | Medium (fundamentals) | Free tier | ✅ Done | - |
| yfinance | High (price data) | Free | ✅ Done | - |

---

## Action Items

**For Jon:**
1. Benzinga: Log in → API section → Get API key
2. Danelfin: Check if API access included in your plan

**For Alyosha (once keys provided):**
1. Build `scripts/benzinga_connector.py`
2. Add Benzinga news feed to NVDA dashboard
3. Build `scripts/danelfin_connector.py`
4. Add AI Score widget to dashboard
5. Create daily alerts for rating changes

---

## Quick Test Commands (once configured)

```bash
# Test Benzinga
curl "https://api.benzinga.com/api/v2/news?token=YOUR_KEY&tickers=NVDA&pageSize=5"

# Test Danelfin (endpoint TBD)
# May need to check their developer docs
```

---

*Last updated: 2026-02-01*
