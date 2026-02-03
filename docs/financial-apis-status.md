# Financial APIs Status

*Last updated: 2026-02-03*

---

## ✅ Active (Keys Available)

### FMP (Financial Modeling Prep)
- **Tier:** Ultimate ($149/mo)
- **Client:** `scripts/fmp-client.py`
- **Key:** `~/.secure/fmp.env`
- **Features:**
  - Real-time quotes (global)
  - Company profiles & key metrics
  - Earnings call transcripts ✅
  - Stock peers
  - Market movers (gainers/losers)
  - Sector performance

```bash
python3 scripts/fmp-client.py quote NVDA
python3 scripts/fmp-client.py profile NVDA
python3 scripts/fmp-client.py movers
```

---

## 🟡 Ready (Need API Keys)

### Benzinga (~$300/mo)
- **Client:** `scripts/benzinga-client.py`
- **Key location:** `~/.secure/benzinga.env`
- **Best for:**
  - Real-time news with sentiment
  - Analyst ratings & price targets
  - Earnings calendar
  - Options activity
  
```bash
# When key available:
python3 scripts/benzinga-client.py news NVDA
python3 scripts/benzinga-client.py ratings NVDA
```

### Danelfin (Pricing TBD)
- **Client:** `scripts/danelfin-client.py`
- **Key location:** `~/.secure/danelfin.env`
- **Best for:**
  - AI stock scores (1-10)
  - Factor analysis
  - Stock screening

```bash
# When key available:
python3 scripts/danelfin-client.py score NVDA
python3 scripts/danelfin-client.py top --aiscore-min 9
```

### Finnhub (FREE tier available)
- **Client:** `scripts/finnhub-client.py`
- **Key:** Get free at https://finnhub.io/register
- **Free tier:** 60 calls/minute
- **Best for:**
  - News sentiment scores
  - Insider transactions & MSPR
  - Analyst recommendations
  - Earnings surprises

```bash
# After getting free key:
echo "FINNHUB_API_KEY=your_key" > ~/.secure/finnhub.env
python3 scripts/finnhub-client.py test
python3 scripts/finnhub-client.py sentiment NVDA
python3 scripts/finnhub-client.py insider NVDA
```

---

## 🔧 Other Tools (No API Needed)

### yfinance
- **Script:** `scripts/stock-quote.py`
- **Cost:** Free
- **Use:** Quick quotes, backup when FMP unavailable

```bash
python3 scripts/stock-quote.py NVDA AAPL MSFT
```

### OpenInsider (Web Scrape)
- **URL:** http://openinsider.com/search?q=NVDA
- **Cost:** Free
- **Use:** Insider transaction data

### Transcript Analysis
- **Scripts:**
  - `scripts/transcript-analyzer.py` — single call analysis
  - `scripts/transcript-compare.py` — quarter comparison
  - `scripts/deep-analyzer.py` — full qualitative analysis

```bash
python3 scripts/transcript-compare.py NVDA --quarters 4
python3 scripts/deep-analyzer.py NVDA --transcript
```

---

## 📊 Comparison Matrix

| API | Cost | News | Sentiment | Insider | Transcripts | Ratings |
|-----|------|------|-----------|---------|-------------|---------|
| **FMP** | $149/mo | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Benzinga** | ~$300/mo | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Danelfin** | TBD | ❌ | ✅ (AI) | ❌ | ❌ | ❌ |
| **Finnhub** | FREE | ✅ | ✅ | ✅ | ❌ | ✅ |
| **yfinance** | FREE | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 🎯 Recommended Stack

**Current (minimal cost):**
1. FMP (already have) — transcripts, fundamentals
2. Finnhub (free) — sentiment, insider, news
3. yfinance (free) — backup quotes

**Full stack (if budget allows):**
1. FMP — transcripts, fundamentals
2. Benzinga — news, ratings, earnings
3. Finnhub — sentiment, insider (free supplement)

---

## 📝 Integration Notes

### Adding a new key
```bash
echo "API_NAME_API_KEY=your_key" > ~/.secure/apiname.env
chmod 600 ~/.secure/apiname.env
```

### Testing a client
```bash
python3 scripts/[client].py test
```

### Watchlist across APIs
```bash
# FMP
python3 scripts/fmp-client.py watchlist NVDA,AAPL,MSFT

# Finnhub (when key ready)
python3 scripts/finnhub-client.py watchlist NVDA,AAPL,MSFT
```

---

## 🚀 Action Items

1. [ ] Get Finnhub free API key
2. [ ] Evaluate Benzinga vs alternatives
3. [ ] Add FRED API for macro data (credit spreads)
4. [ ] Consider Unusual Whales for options flow
