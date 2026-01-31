# 📊 Watchlist Intelligence Tool

A CLI tool for generating stock watchlist briefings with news aggregation and sentiment analysis.

## Features

- **Configurable Watchlist**: Track any tickers with priority levels
- **Sentiment Analysis**: Rule-based scoring of headlines (bullish/bearish/neutral)
- **Multiple Output Formats**: Human-readable, brief summary, or JSON
- **Caching**: 1-hour cache to avoid redundant API calls
- **Modular Design**: Easily integrate with different news sources

## Quick Start

```bash
# View help
node intel.js --help

# Generate briefing (pipe news data in)
cat news.json | node intel.js

# Brief summary only
cat news.json | node intel.js --brief

# JSON output for automation
cat news.json | node intel.js --json

# Single ticker
cat news.json | node intel.js --ticker NVDA
```

## Configuration

Edit `watchlist.json` to customize your watchlist:

```json
{
  "tickers": [
    { "symbol": "NVDA", "name": "NVIDIA", "priority": "high" },
    { "symbol": "AMD", "name": "AMD", "priority": "high" }
  ],
  "settings": {
    "maxNewsPerTicker": 5,
    "sentimentThreshold": 0.3
  }
}
```

## News Data Format

The tool expects news data piped via stdin in this format:

```json
{
  "NVDA": {
    "headlines": [
      "NVIDIA stock surges on AI demand",
      "Data center revenue hits record"
    ]
  },
  "AMD": {
    "headlines": [
      "AMD unveils new MI455X at CES 2026"
    ]
  }
}
```

## Integration with OpenClaw

This tool is designed to work with OpenClaw's `web_search` capability:

1. Agent searches for news on each ticker
2. Agent compiles headlines into JSON
3. Agent pipes data through `intel.js`
4. Agent delivers formatted briefing

## Sentiment Keywords

**Bullish signals**: surge, rally, beat, upgrade, growth, breakthrough, momentum
**Bearish signals**: drop, crash, miss, downgrade, concern, risk, layoff

## Output Example

```
═══════════════════════════════════════════════════════════
  📊 WATCHLIST INTELLIGENCE BRIEFING
  Generated: 2026-01-31 02:23:20 UTC
═══════════════════════════════════════════════════════════

📈 QUICK SUMMARY
─────────────────
  🟢 Bullish: NVDA, AMD, TSMC
  🔴 Bearish: INTC

⭐ NVDA — NVIDIA
  Sentiment: 🟢 bullish (score: 0.8)
  Recent Headlines:
    • NVIDIA stock surges on record AI chip demand
    • Data center revenue exceeds expectations
```

## Files

- `intel.js` - Main CLI tool
- `watchlist.json` - Ticker configuration
- `run-briefing.sh` - Bash wrapper
- `.cache/` - Cached news data (auto-generated)

---

*Built for Jon by Alyosha 🕯️*
