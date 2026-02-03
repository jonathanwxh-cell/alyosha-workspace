# Risk/Reward Framework

## Scenario Analysis Template

| Scenario | Probability | Return | Key Assumption |
|----------|-------------|--------|----------------|
| **Bull** | __% | +__% | What must be TRUE |
| **Base** | __% | +__% | What must be TRUE |
| **Bear** | __% | -__% | What must be TRUE |
| **Catastrophic** | __% | -__% | What must be TRUE |

**Expected Value = Σ(Probability × Return)**

Rule: If EV < 10% and not high conviction, pass.

## Fragility Assessment (Talebian)

### Fragile Indicators (RED FLAGS)
- Single customer >20% of revenue
- Single supplier dependency
- High debt with floating rates
- Binary regulatory outcomes
- Concentrated geography
- Key-man risk
- Extreme expectations priced in

### Antifragile Indicators (GREEN FLAGS)
- Optionality (many small bets)
- Low fixed costs, high variable
- Benefits from volatility
- Diversified customer base
- Strong balance sheet in downturn sector
- Founder-led with long-term orientation

### Net Fragility Score

| Level | Criteria |
|-------|----------|
| **LOW** | 0-1 fragile indicators, 3+ antifragile |
| **MEDIUM** | 2-3 fragile indicators |
| **HIGH** | 4+ fragile indicators OR extreme valuation |

## Kill Criteria (Define Upfront)

Always establish exit conditions BEFORE investing:

1. **Thesis break:** What event invalidates the thesis?
2. **Management integrity:** What behavior triggers exit?
3. **Valuation:** At what price is risk/reward unfavorable?
4. **Time:** How long to wait for thesis to play out?
5. **Opportunity cost:** What better use of capital?

Example:
```
Exit if:
- CEO/founder leaves
- Market share drops below X%
- Custom silicon reaches 20% share
- Position exceeds 5% of portfolio
- 18 months with no thesis progress
```

## Position Sizing

| Confidence | Fragility | Position Size |
|------------|-----------|---------------|
| HIGH | LOW | Full (3-5%) |
| HIGH | MEDIUM | Standard (2-3%) |
| HIGH | HIGH | Reduced (1-2%) |
| MEDIUM | LOW | Standard (2-3%) |
| MEDIUM | MEDIUM | Starter (1-2%) |
| MEDIUM | HIGH | Pass or tiny |
| LOW | Any | Pass |
