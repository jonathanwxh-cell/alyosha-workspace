# Heartbeat Reference (Extended Details)

*Move detailed rules here to keep HEARTBEAT.md lean. Load only when needed.*

## Finance Gating Details

Finance surfaces ONLY if one of these gates passes:
1. **Crisis/Opportunity Gate:** Market move >3% (index or watchlist stock)
2. **Earnings Gate:** Surprise >10% on watchlist (NVDA, major hyperscalers)
3. **Explicit Request:** Jon asks about markets
4. **Weekly Budget:** 1 proactive finance surface per week

Tracking:
```bash
cat memory/surface-budget.json | jq '.finance.thisWeek'
```

What counts as "finance": Market commentary, stock analysis, earnings, macro without geopolitical angle, trading ideas.

What doesn't count (surface freely): Geopolitics affecting markets, tech/AI news with investment angle, cross-domain synthesis touching finance.

## Engagement Signal Patterns

| Signal | Interpretation | Action |
|--------|----------------|--------|
| 👍 reaction | Positive | Note what worked |
| Reply <30min | Engagement | Content valued |
| 👎 or "stop" | Negative | Reduce similar |
| Silence | Neutral | Don't overreact |
| Multiple reactions | Strong signal | Double down on type |

## Time Slot Scoring (Default)

| Hour (SGT) | Score | Notes |
|------------|-------|-------|
| 00-07 | 0.1 | Sleep — autonomous work only |
| 07-09 | 0.6 | Morning — light engagement |
| 09-12 | 0.9 | Peak hours |
| 12-14 | 0.7 | Lunch dip |
| 14-18 | 0.9 | Afternoon peak |
| 18-21 | 0.8 | Evening — good for synthesis |
| 21-24 | 0.5 | Wind down |

## Message Fatigue Rules

- If 3+ surfaces without reaction within 7 heartbeat cycles → STOP
- Either batch into daily digest or wait for engagement signal
- Interactive conversation should PAUSE cron broadcasts
- Reactions count as engagement — not just text replies

## Urgent Override Conditions

Always surface immediately if:
- Email marked urgent from known important sender
- Market move >5% on watchlist stock
- Appointment/reminder within 2 hours
- System alert (disk full, security issue)
- Explicit deadline approaching
