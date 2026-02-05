# Trading Goal: Closed Feedback Loop Design

*Sketch for autonomous self-learning*

## Current Gap

```
Research → Score → Propose → [Jon 👍/👎] → Execute → [Outcome] → ???
                                                          ↓
                                              (not connected back)
```

## Proposed Loop

```
Research → Score → Propose → Approve → Execute → Outcome
    ↑                                               ↓
    └──────────── Auto-Adjust ←─────────────────────┘
```

---

## Components Needed

### 1. Outcome Tracker (`memory/goals/trading/outcomes.jsonl`)

Every closed trade logs:
```json
{
  "timestamp": "2026-02-15T10:00:00Z",
  "ticker": "RTX",
  "strategy": "wheel_csp",
  "entry_score": 8.2,
  "thesis_at_entry": "Defense sector momentum, post-earnings pullback",
  "entry_price": 118.50,
  "exit_price": 125.00,
  "result": "win",
  "return_pct": 5.5,
  "days_held": 21,
  "what_worked": "Thesis was correct, sector continued strong",
  "what_failed": null,
  "sector": "industrials"
}
```

### 2. Learning Weights (`memory/goals/trading/learning-weights.json`)

Auto-adjusted parameters:
```json
{
  "score_threshold": {
    "current": 7.5,
    "history": [
      {"date": "2026-02-05", "value": 8.0, "reason": "initial"},
      {"date": "2026-02-10", "value": 7.5, "reason": "lowered after 3 good 7.5+ misses"}
    ]
  },
  "sector_weights": {
    "industrials": 1.2,
    "healthcare": 1.0,
    "energy": 0.8,
    "tech": 1.0
  },
  "strategy_confidence": {
    "wheel_csp": 1.0,
    "pmcc": 1.0,
    "credit_spread": 0.9
  }
}
```

### 3. Feedback Analyzer (Weekly Cron)

```python
# scripts/feedback-loop.py

def analyze_outcomes():
    """Analyze trade outcomes and propose adjustments."""
    
    outcomes = load_outcomes()
    weights = load_weights()
    
    # Win rate by sector
    sector_performance = {}
    for o in outcomes:
        sector = o['sector']
        if sector not in sector_performance:
            sector_performance[sector] = {'wins': 0, 'losses': 0}
        if o['result'] == 'win':
            sector_performance[sector]['wins'] += 1
        else:
            sector_performance[sector]['losses'] += 1
    
    # Adjust sector weights based on performance
    for sector, perf in sector_performance.items():
        win_rate = perf['wins'] / (perf['wins'] + perf['losses'])
        if win_rate > 0.6:
            weights['sector_weights'][sector] *= 1.1  # Boost
        elif win_rate < 0.4:
            weights['sector_weights'][sector] *= 0.9  # Reduce
    
    # Threshold adjustment
    # If we passed on trades that would have won, lower threshold
    # If we took trades that lost, raise threshold
    
    return adjustments

def apply_adjustments(adjustments):
    """Apply weight changes to influence future scoring."""
    # Update learning-weights.json
    # Notify Jon of changes
    pass
```

### 4. Score Integration

Opportunity Hunter reads weights:
```
base_score = thesis_alignment + risk_reward + timing + confidence
adjusted_score = base_score * sector_weight * strategy_confidence

if adjusted_score >= threshold:
    trigger_deep_analyst()
```

### 5. Approval Feedback

When Jon approves/rejects:
- 👍 → Log as "approved", track to outcome
- 👎 → Log rejection reason, learn from it
- If Jon overrides (approves 7.2 score) → signal to lower threshold

---

## Implementation Phases

### Phase 1: Outcome Tracking (Now)
- Create outcomes.jsonl format
- Manual logging when trades close
- Basic win/loss tracking

### Phase 2: Weight System (Week 2)
- Create learning-weights.json
- Opportunity Hunter reads weights
- Manual weight adjustment based on review

### Phase 3: Auto-Adjustment (Week 3+)
- Weekly cron analyzes outcomes
- Proposes weight changes
- Auto-applies small changes (<10%)
- Alerts Jon for larger changes

---

## Anti-Patterns to Avoid

1. **Overfitting** — Don't adjust on 1-2 trades, need sample size
2. **Recency bias** — Weight recent outcomes but don't ignore history
3. **Runaway adjustment** — Cap adjustment rate (max ±10% per week)
4. **Ignoring context** — Market regime matters (bull vs bear)

---

## Success Metrics

- System should converge on profitable thresholds
- Sector weights should reflect actual edge
- Fewer good trades missed (lower false negative rate)
- Fewer bad trades taken (lower false positive rate)

---

*Draft: 2026-02-05. Implement incrementally.*
