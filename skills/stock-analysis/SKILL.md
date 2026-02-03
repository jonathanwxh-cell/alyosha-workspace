---
name: stock-analysis
description: Deep qualitative stock analysis using transcript NLP, tone trends, insider data, and risk frameworks. Use when asked to analyze a stock, evaluate a company, assess management quality, or research an investment. Triggers on: stock analysis, company analysis, earnings analysis, management assessment, investment research, ticker deep-dive.
---

# Stock Analysis Skill

Comprehensive 7-dimension qualitative analysis framework for stocks.

## Quick Start

```bash
# Full analysis workflow
python3 scripts/transcript-compare.py TICKER --quarters 4
python3 scripts/deep-analyzer.py TICKER --transcript
python3 scripts/finnhub-client.py insider TICKER
python3 scripts/finnhub-client.py recommend TICKER
```

## The 7 Dimensions

| # | Dimension | Tool | Key Signal |
|---|-----------|------|------------|
| 1 | Transcript tone | `deep-analyzer.py --transcript` | Deflection %, guidance quality |
| 2 | Tone trends | `transcript-compare.py` | QoQ conviction/hedging shift |
| 3 | Insider activity | `finnhub-client.py insider` | Net buy/sell pattern |
| 4 | Analyst sentiment | `finnhub-client.py recommend` | Consensus trend |
| 5 | Industry position | Manual + references/industry-framework.md | Porter's forces |
| 6 | Risk/reward | references/risk-framework.md | Scenario analysis |
| 7 | Second-order | references/second-order.md | What's priced in |

## Transcript Signals

### Red Flags
- **Deflection >20%**: Management dodging Q&A questions
- **Hedging spike**: Uncertainty language increasing QoQ
- **Conviction drop**: Confidence language declining
- **Prepared vs Q&A gap >0.5**: Sugarcoating in scripted remarks
- **Blame externalization**: "Macro," "one-time" without ownership

### Green Flags
- **Deflection <10%**: Forthcoming, answering directly
- **Specific guidance >80%**: Clear visibility
- **Stable/improving confidence ratio**: Genuine conviction

## Insider Signals

| Pattern | Interpretation |
|---------|----------------|
| Cluster buying (3+ insiders) | Strong bullish signal |
| All sells, no buys | Cautious (may be comp-related) |
| CEO/CFO buying | Very bullish |
| CFO selling large | Yellow flag |

## Analysis Workflow

1. **Run transcript comparison** (4 quarters minimum)
2. **Check latest call** for specific signals
3. **Pull insider data** from Finnhub
4. **Check analyst consensus** trend
5. **Apply industry framework** (see references/)
6. **Build scenario analysis** with kill criteria
7. **Identify non-consensus insight**

## Output Format

Always produce structured output:

```markdown
# [TICKER] Analysis — [DATE]

**Thesis:** [1 sentence]
**Confidence:** HIGH/MEDIUM/LOW
**Key insight:** [what you see that consensus doesn't]

## Transcript Signals
| Signal | Value | Assessment |
|--------|-------|------------|
| Deflection | X% | 🟢/🟡/🔴 |
| Conviction trend | +/-X | 🟢/🟡/🔴 |
| Guidance | X% specific | 🟢/🟡/🔴 |

## Tone Trends (4Q)
[quarter comparison table]

## Alternative Data
- **Insider:** [pattern]
- **Analyst:** [consensus]

## Risk/Reward
| Scenario | Prob | Return | Key Assumption |
|----------|------|--------|----------------|
| Bull | % | +% | |
| Base | % | +% | |
| Bear | % | -% | |

**Fragility:** HIGH/MEDIUM/LOW

## Kill Criteria
Exit if: [specific conditions]
```

## API Requirements

- **FMP** (required): Transcripts, fundamentals
- **Finnhub** (required): Insider, recommendations
- Keys at: `~/.secure/fmp.env`, `~/.secure/finnhub.env`

## References

- `references/industry-framework.md` — Porter's forces, cycle analysis
- `references/risk-framework.md` — Scenario analysis, fragility assessment
- `references/second-order.md` — What's priced in, consensus analysis
