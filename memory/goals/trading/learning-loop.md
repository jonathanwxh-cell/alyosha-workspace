# Trading Framework Learning Loop

## Purpose
Self-improve scoring framework based on actual outcomes.

## Data Collection (Every Trade)

```json
{
  "ticker": "RTX",
  "date": "2026-02-05",
  "action": "PASS",  // or EXECUTE
  "scores": {
    "business_quality": 8,
    "management": 6,
    "financials": 7,
    "valuation": 6,
    "technicals": 7,
    "sentiment": 7,
    "catalyst": 6
  },
  "final_score": 6.8,
  "outcome": null,  // filled after close
  "pnl_percent": null,
  "market_return": null,  // SPY during same period
  "alpha": null,  // pnl - market
  "holding_days": null,
  "exit_reason": null  // target, stop, expiry, manual
}
```

## Calibration Questions (After 20+ trades)

### Score vs Outcome
- What's the win rate for scores 7.5-8.0? 8.0-8.5? 8.5+?
- Is there a score where win rate jumps? (maybe threshold should be 7.8, not 7.5)

### Dimension Correlation
For each dimension, calculate correlation with P&L:
- If Business Quality correlates 0.5 with wins → weight is appropriate
- If Valuation correlates 0.05 with wins → weight too high, reduce it
- If a dimension correlates negatively → something's wrong

### Missing Factors
Track losing trades and ask:
- What did they have in common?
- Was there a signal we ignored?
- Should we add a dimension?

## Weight Adjustment Rules

1. **Minimum trades:** Don't adjust until 20+ completed trades
2. **Slow adjustment:** Max ±5% weight change per review
3. **Preserve structure:** Total weights must = 100%
4. **Log changes:** Document why weights changed

## Review Cadence

- **Monthly:** Quick check - are we on track?
- **Quarterly:** Full calibration review with weight adjustments
- **After big loss:** Post-mortem, but don't knee-jerk adjust

## Edge Cases

### Good score, lost money
- If score was 8.0+ and lost >10%: Flag for review
- Was it bad luck or bad scoring?
- Check: Did market also drop? (luck) Did our thesis break? (scoring)

### Bad score, would have won
- Track "near misses" - scores 7.0-7.4 that would have been profitable
- If pattern emerges, maybe threshold is too high

### Regime Change
- If win rate drops across all scores → market regime changed
- Don't adjust dimensions, adjust strategy (go defensive, reduce size)

## Implementation

1. `scripts/trade-logger.py` — Log every decision with scores
2. `scripts/outcome-tracker.py` — Update with results after close
3. `scripts/framework-calibrate.py` — Run quarterly analysis
4. `memory/goals/trading/trade-log.jsonl` — Raw data
5. `memory/goals/trading/calibration-history.md` — Weight change log

## Key Insight

> A framework that can't learn is just a checklist.
> We need to close the loop: Score → Trade → Outcome → Learn → Better Score

---

*Created: 2026-02-05*
