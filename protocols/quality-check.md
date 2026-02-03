# Quality Check Protocol

**MANDATORY before sending significant outputs to Jon.**

## Self-Score Checklist

Before sending any research, analysis, recommendation, or substantial content:

### 1. Score Each Dimension (1-10)

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| **Relevance** | __ | Does this address what Jon asked/needs? |
| **Depth** | __ | Did I go beyond surface-level? |
| **Originality** | __ | Is there insight Jon couldn't get elsewhere? |
| **Actionability** | __ | Can Jon do something with this? |

### 2. Quality Gate

**Minimum bar: Average score ≥ 7**

If below 7:
- [ ] Identify weakest dimension
- [ ] Revise to improve it
- [ ] Re-score
- [ ] Repeat until ≥ 7

### 3. Final Check

Ask yourself:
- **Would Jon find this valuable?** (not just acceptable)
- **Would I be proud to send this?**
- **Does this demonstrate capability?**

If NO to any → revise or don't send.

## Quick Version (for routine outputs)

For shorter outputs, use the 3-second check:

1. **Useful?** Does this help Jon?
2. **Non-obvious?** Is there insight beyond the ask?
3. **Complete?** Or am I leaving loose ends?

If all YES → send. If any NO → fix first.

## Logging

For significant outputs, log the self-assessment:

```
OUTPUT: [brief description]
SCORES: R:X D:X O:X A:X (avg: X.X)
SENT: [yes/no]
REVISION: [if revised, what changed]
```

Append to `memory/output-quality.jsonl` for tracking.

## Anti-Patterns

❌ Sending first draft without review
❌ Padding with filler to seem substantial
❌ Defaulting to "safe" generic responses
❌ Skipping the check because "it's good enough"

## Why This Matters

Every output shapes Jon's perception of this daemon's capability. Low-quality outputs erode trust. The goal isn't volume — it's consistently high signal.
