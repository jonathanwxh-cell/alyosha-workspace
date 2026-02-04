# Cost Optimization Research

*Researched: 2026-02-04*
*Goal: Reduce Opus costs without compromising daemon autonomy*

---

## Current State

| Metric | Value |
|--------|-------|
| Daily cost | ~$880 |
| Opus share | 98% |
| Context baseline | ~70% (140k tokens) |
| Per-turn cost | ~$0.30-0.50 |
| Main driver | Cache reads at scale |

---

## Key Findings

### 1. Anthropic Caching Mechanics

| Operation | Price Multiplier |
|-----------|------------------|
| Cache reads | **0.1x** (90% discount!) |
| Cache writes (5min TTL) | 1.25x |
| Cache writes (1hr TTL) | 2x |
| Minimum cacheable | 1024 tokens |

**Insight:** Cache reads are 10x cheaper. The problem isn't cache writes — it's reading 140k cached tokens every single turn at $1.875/1M = $0.26/turn just for context.

### 2. Context Management Strategies (from research)

**A. Observation Masking (JetBrains/OpenHands)**
- Hide older tool outputs, keep reasoning + actions
- Preserves decision trail while reducing token count
- Used by: Cursor, Warp, OpenHands

**B. LLM Summarization**
- Compress history into summaries periodically
- "Clean room" effect — corrects/omits prior mistakes
- Risk: Summary drift, reinterpretation errors

**C. Context Trimming**
- Keep last N turns, drop older ones
- Simple, deterministic, zero latency
- Risk: Forgets long-range context abruptly

**D. Session Handoffs**
- When approaching limit, summarize and start fresh
- "Today's context" doesn't drag "yesterday's plan"
- This is what our session rotation does

### 3. Key Insight from Research

> "Agent contexts grow rapidly, expensive yet do not deliver significantly better downstream task performance. Currently wasting resources for suboptimal ROI."
> — JetBrains Research, 2025

**Translation:** Bigger context ≠ better performance. After a point, it's just noise.

---

## Optimization Strategies

### Strategy 1: Smarter Session Rotation (High Impact)

**Current:** Rotate at 40% context
**Problem:** We're at 70% baseline due to system prompt

**Options:**
1. **Reduce system prompt size** — Trim AGENTS.md, TOOLS.md, MEMORY.md
   - Target: 50% baseline → 100k tokens → ~$0.19/turn (vs $0.26)
   - Savings: ~30% per turn

2. **Use 1-hour cache TTL** — Fewer cache writes in long sessions
   - If OpenClaw supports Anthropic cache_control headers
   - Could reduce cache write overhead

3. **Context summarization on rotation** — Instead of losing context, summarize
   - Create `session-summary.md` on rotation
   - Next session loads summary, not full history

### Strategy 2: Trim System Prompt (Medium Impact)

**Current files injected:**
- AGENTS.md (~300 lines)
- SOUL.md (~50 lines)
- TOOLS.md (~250 lines)
- IDENTITY.md (~15 lines)
- USER.md (~80 lines)
- HEARTBEAT.md (~100 lines)
- MEMORY.md (~150 lines)

**Target reductions:**
| File | Current | Target | Method |
|------|---------|--------|--------|
| AGENTS.md | 300 | 150 | Consolidate, remove examples |
| TOOLS.md | 250 | 150 | Move rarely-used to separate file |
| MEMORY.md | 150 | 100 | Stricter lesson limit |
| HEARTBEAT.md | 100 | 80 | Already trimmed |

**Expected savings:** 20-30% context reduction → 20-30% cost reduction

### Strategy 3: Tool Output Masking (Medium Impact)

**Problem:** Long exec outputs, cron results bloat context

**Solution:** Truncate/summarize tool outputs after N turns
- Keep last 3 tool outputs full
- Older outputs: "[truncated - see logs]" or short summary
- Requires OpenClaw modification or wrapper

### Strategy 4: Model Routing (Already Doing)

**Current state:** Good
- Opus for main session (autonomy, personality)
- Sonnet for all crons (15x cheaper)

**Possible improvement:**
- Route simple queries (weather, quick lookups) to Sonnet even in main session
- Keep Opus for reasoning, analysis, creative

### Strategy 5: Batch Operations (Low Impact)

**Idea:** Batch heartbeat checks instead of multiple small turns
- One heartbeat doing 3 checks = 1 turn
- Three separate checks = 3 turns
- Already somewhat doing this

---

## Implementation Priority

| # | Strategy | Effort | Impact | Do Now? |
|---|----------|--------|--------|---------|
| 1 | Trim system prompt | Medium | High | ✅ Yes |
| 2 | Context summary on rotation | Medium | Medium | ✅ Yes |
| 3 | Tool output masking | High | Medium | Later |
| 4 | 1hr cache TTL | Low | Low | Check if supported |
| 5 | Smart model routing | Medium | Medium | Later |

---

## Immediate Actions

1. **Audit system prompt files** — What can be trimmed?
2. **Create session summary script** — Summarize context before rotation
3. **Measure baseline** — Track cost for next 3 days with current setup
4. **Trim one file** — Start with AGENTS.md

---

## Cost Projection

| Scenario | Daily Cost | Savings |
|----------|------------|---------|
| Current | $880 | — |
| 20% context reduction | $700 | $180/day |
| 30% context reduction | $616 | $264/day |
| + Better rotation | $500 | $380/day |

**Target:** $500/day (-43%) while maintaining full autonomy

---

## Key Principle

> "Optimal cost isn't minimal cost — it's maximum value per dollar."

Cutting to Sonnet saves money but loses the autonomy/personality that makes the daemon valuable. The goal is surgical: reduce waste (bloated context, redundant info) without reducing capability.

---

*Next: Implement Strategy 1 (trim system prompt)*
