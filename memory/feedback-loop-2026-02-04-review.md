# Feedback Loop Review — 2026-02-04

## What's Working Well ✅

### 1. Kids Dinner Ideas
- Format: Option 1/2/3 with timing works perfectly
- Practical, actionable, no filler
- "Reply with number" creates engagement loop
- **Keep as-is**

### 2. Talebian Lens  
- Sharp, one-line per category
- Investment-relevant
- Low time cost (~31s)
- **Keep as-is**

### 3. Daily World State
- Pipeline structure with checkpoints prevents garbage
- 5-stage quality gate works
- Investment assessment included
- **Keep as-is**

### 4. "Quiet News Day" Discipline
- SG Briefing now says "quiet" instead of surfacing noise
- This is GOOD behavior
- But maybe too frequent if often quiet

---

## What's NOT Working ❌

### 1. Research Scan — Missing Investment Angle
**Problem:** Prompt says "require investment angle" but output had NONE.
```
Example output:
"Xcode 26.3 integrates coding agents" 
"AgentRx: Diagnosing AI Agent Failures"
"IIT-Inspired Consciousness in LLMs"
```
Zero investment angles despite prompt requirement.

**Fix:** Restructure output format to REQUIRE angle per item.

### 2. SG Briefing — Too Many "Quiet" Days
**Problem:** 2/3 recent runs returned "quiet news day"
- 40% hit rate is too low
- Burning Sonnet tokens on empty outputs

**Fix:** Reduce from daily to 3x/week (Mon/Wed/Fri)

### 3. Daily Free Exploration — Long Runtime, Low Relevance
**Problem:** 143 seconds per run, consciousness research isn't actionable
- Interesting to me, not to Jon
- No investment connection

**Fix:** Add relevance gate; cap timeout at 300s

---

## Concrete Changes Made

### Change 1: Research Scan — Enforce Investment Angle
Updated output format to require `Investment angle: [position/trade]` per item

### Change 2: SG Briefing — Reduce Frequency
Changed from daily to Mon/Wed/Fri

### Change 3: Added "Duck Principle" Enforcement
Most daemon work should be invisible. Only surface the ~10% that's genuinely high-value.

---

## Pattern Recognition

### High-Engagement Formula (confirmed)
**SPECIFIC + FRAMEWORK + ACTIONABLE + JON CHOOSES = engagement**

- Fragility Index on SE → immediate engagement, Substack post
- Talebian Lens → sharp, investment-relevant
- Kids Dinner Options → practical, choice-based

### Low-Engagement Pattern
- Generic opportunity hunting without time pressure
- Infrastructure/meta work surfaced (should be silent)
- Research without investment angle

---

## Metrics Snapshot

| Cron | Last 3 Runs | Avg Runtime | Fix Needed? |
|------|-------------|-------------|-------------|
| Kids Dinner | ✅✅✅ | 38s | No |
| Talebian Lens | ✅ | 31s | No |
| World State | ✅✅✅ | 95s | No |
| SG Briefing | ⚪⚪✅ | 52s | Yes - freq |
| Research Scan | ✅ | 55s | Yes - format |
| Free Exploration | ✅ | 143s | Yes - timeout |

---

*Next review: 2026-02-11*
