# Financial Modeling Prep (FMP) Integration Guide

*Last Updated: 2026-02-02*

---

## Status: ✅ Working

FMP API is configured and operational. The key is stored in `.secure/fmp.env`.

---

## Quick Start

```bash
# Get quote for a single stock
python3 scripts/fmp-client.py quote NVDA

# Get quotes for multiple stocks
python3 scripts/fmp-client.py quote NVDA AAPL MSFT

# Watchlist summary (formatted for Telegram)
python3 scripts/fmp-client.py watchlist NVDA,AAPL,MSFT,GOOGL

# Company snapshot
python3 scripts/fmp-client.py snapshot NVDA

# Search for companies
python3 scripts/fmp-client.py search nvidia
```

---

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `quote` | Real-time price, change, volume | `fmp-client.py quote NVDA` |
| `profile` | Company details (sector, CEO, etc.) | `fmp-client.py profile NVDA` |
| `metrics` | Key financial metrics | `fmp-client.py metrics NVDA` |
| `search` | Search by company name | `fmp-client.py search nvidia` |
| `watchlist` | Formatted summary for list | `fmp-client.py watchlist NVDA,AAPL` |
| `snapshot` | Full company overview | `fmp-client.py snapshot NVDA` |
| `movers` | Top gainers/losers* | `fmp-client.py movers` |
| `sectors` | Sector performance* | `fmp-client.py sectors` |

*May require higher API tier

---

## API Tier Limitations

Current tier appears to be **Free/Basic**. Some endpoints return empty:
- ❌ Earnings calendar (empty)
- ❌ Analyst estimates (empty)
- ❌ Stock news (empty)
- ❌ Stock screener (empty)
- ❌ Bulk quotes (must fetch individually)
- ❌ Market movers (empty)

**Working endpoints:**
- ✅ Quote (individual)
- ✅ Profile
- ✅ Key metrics
- ✅ Ratios
- ✅ Search
- ✅ Sector performance

---

## Python API Usage

```python
# Import and initialize
import sys
sys.path.insert(0, 'scripts')
import importlib
fmp = importlib.import_module('fmp-client')
fmp.init()

# Get quote
quotes = fmp.quote(['NVDA', 'AAPL'])
for q in quotes:
    print(f"{q['symbol']}: ${q['price']}")

# Get profile
profile = fmp.profile('NVDA')
print(profile['description'])

# Get key metrics
metrics = fmp.key_metrics('NVDA', limit=1)
print(f"P/E: {metrics[0].get('peRatio')}")

# Generate watchlist summary (for Telegram)
summary = fmp.watchlist_summary(['NVDA', 'AAPL', 'MSFT'])
print(summary)

# Company snapshot (markdown)
snapshot = fmp.company_snapshot('NVDA')
print(snapshot)
```

---

## Integration with Cron Jobs

### Daily Market Check
```python
# In a cron job prompt:
# 1. Run: python3 scripts/fmp-client.py watchlist NVDA,AAPL,MSFT,GOOGL,META
# 2. Include output in daily briefing
```

### NVDA Dashboard Data
The NVDA dashboard at `tools/nvda-dashboard/` can use this for live quotes.

---

## Upgrading API Tier

If Jon wants more capabilities, FMP offers paid tiers:
- **Starter ($14/mo):** Stock screener, historical data
- **Premium ($29/mo):** News, analyst ratings, earnings calendar
- **Enterprise:** Full access

Benzinga and Danelfin remain **not configured** (no API keys provided).

---

## Troubleshooting

### Empty responses
Most likely a tier limitation. Check if endpoint requires paid tier.

### API key issues
```bash
cat ~/.openclaw/workspace/.secure/fmp.env
# Should show: FMP_API_KEY=...
```

### Rate limits
Free tier has rate limits. If seeing 429 errors, wait and retry.

---

## Next Steps

1. **Ask Jon:** Does he want to upgrade FMP tier for more data?
2. **Benzinga:** Would require API key (~$300/mo) - worth it for news/ratings?
3. **Danelfin:** AI scores for screening - need to check if Jon has API access or just web

