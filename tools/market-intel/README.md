# 📊 Market Intelligence Tool

A command-line tool that aggregates market data and semiconductor news into a clean briefing format.

## Features

- **Real-time quotes** from Yahoo Finance (no API key needed)
- **Fear & Greed Index** from CNN
- **Semiconductor focus** with NVDA, AMD, TSM, AVGO, INTC, MU
- **Major indices** tracking (SPY, QQQ, DIA)
- **News aggregation** for semiconductor/AI topics
- **Market status** awareness (open/pre-market/after-hours/weekend)

## Usage

```bash
# Full briefing
node market-intel.js

# Quick summary (no news)
node market-intel.js --quick

# JSON output (for programmatic use)
node market-intel.js --json
```

## Output Format

The briefing includes:
1. Market status (open/closed/pre-market)
2. Fear & Greed indicator
3. Major indices performance
4. Semiconductor sector quotes
5. Recent semiconductor/AI news
6. NVDA spotlight summary

## Integration with OpenClaw

This tool can be called by the agent during:
- Morning briefings
- On-demand market checks
- Scheduled cron jobs

---

*Built by Alyosha 🕯️ for Jon*
