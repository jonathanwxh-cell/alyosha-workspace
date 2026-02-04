# Model Tiering Exploration

*Analysis date: 2026-02-04*
*Status: EXPLORATION ONLY — no implementation without approval*

---

## Executive Summary

Model tiering can reduce LLM costs 50-85% while retaining 95%+ quality. Current setup is **already well-optimized** — the main opportunity is expanding Haiku usage for mechanical tasks.

**Current allocation:**
- ✅ Opus: Interactive sessions (appropriate)
- ✅ Sonnet: All crons (33 crons, all Sonnet — correct)
- ⚠️ Haiku: Underutilized

**Bottom line:** The biggest win isn't restructuring — it's identifying Haiku-suitable tasks currently using Sonnet.

---

## Pricing Analysis

### Current Rates (per million tokens)

| Model | Input | Output | vs Opus |
|-------|-------|--------|---------|
| Opus 4.5 | $5 | $25 | 1x |
| Sonnet 4.5 | $3 | $15 | ~1.7x cheaper |
| Haiku 4.5 | $1 | $5 | 5x cheaper |

### Cost Ratios

- Sonnet is **40% cheaper** than Opus on input, **40% cheaper** on output
- Haiku is **5x cheaper** than Opus
- Haiku is **3x cheaper** than Sonnet

### Real Numbers (Hypothetical 1M requests/month, 1K in + 500 out tokens each)

| Scenario | Monthly Cost |
|----------|--------------|
| All Opus | $8,750 |
| Current (Opus main + Sonnet crons) | ~$4,000-5,000 |
| With Haiku for mechanical | ~$2,500-3,500 |
| Aggressive Haiku | ~$1,500-2,000 |

---

## Task Classification Framework

### Tier 1: Haiku ($1/$5) — Mechanical Tasks

**Characteristics:**
- No reasoning required
- Structured input/output
- Classification or extraction
- Format conversion
- Simple Q&A with clear answers

**Candidate tasks from current crons:**
- `Daily Cost Log` — just runs a script, reports result
- `Auto-Commit to GitHub` — runs script, brief report
- `NVDA Dashboard Refresh` — fetch data, report errors only
- `Semantic Search Health Check` — status check, no analysis
- `GitHub Release Monitor` — event detection, simple alert
- `Model Release Watch` — same pattern

**Potential Haiku expansion:**
- Script execution + simple status reporting
- JSON parsing and reformatting
- Simple threshold checks (move > X%)
- Deduplication checks before complex work

### Tier 2: Sonnet ($3/$15) — Analysis & Synthesis

**Characteristics:**
- Moderate reasoning
- Research and synthesis
- Following structured prompts
- Quality output generation
- Most cron workloads

**Current Sonnet tasks (correct allocation):**
- Daily World State Analysis
- Research Scan
- Fragility Index Weekly
- Macro Pulse
- Kids Dinner Ideas
- All research/synthesis crons

### Tier 3: Opus ($5/$25) — Complex Reasoning

**Characteristics:**
- Multi-step reasoning
- Ambiguous instructions
- Creative problem-solving
- Strategic planning
- Interactive conversation

**Current Opus tasks (correct allocation):**
- Main interactive session (this conversation)
- Complex debugging
- Architecture decisions
- Meta/self-improvement work

---

## Routing Strategies Comparison

### 1. Rule-Based Routing (Current Approach)

**How it works:** Manually assign model per task type

**Pros:**
- Predictable costs
- No routing overhead
- Simple to understand
- Easy to debug

**Cons:**
- Requires manual classification
- Misses nuance within task types
- Suboptimal when task varies

**Verdict:** ✅ Already using this. Works well for our cron-based system.

### 2. ML-Based Routing (RouteLLM)

**How it works:** Trained classifier predicts optimal model per query

**Pros:**
- 85% cost reduction possible
- Handles nuance
- Self-optimizing with feedback

**Cons:**
- Adds latency (~11-50ms)
- Requires setup/training
- Black box decisions
- Overkill for our volume

**Verdict:** ❌ Unnecessary complexity for our use case. Better for high-volume APIs.

### 3. LLM-Based Classification

**How it works:** Use cheap model to classify, then route

**Pros:**
- Handles novel queries
- More flexible than rules

**Cons:**
- Adds cost (classification call)
- Adds latency
- Meta-inefficiency (LLM to decide which LLM)

**Verdict:** ❌ Not worth it. Classification cost eats savings for our volume.

### 4. Hybrid: Rule-Based with Haiku Expansion

**How it works:** Keep current Opus/Sonnet split, add Haiku layer for mechanical

**Pros:**
- Low risk
- Easy to implement
- Meaningful savings
- No new infrastructure

**Cons:**
- Requires identifying Haiku-suitable tasks
- Some trial-and-error

**Verdict:** ✅ **RECOMMENDED APPROACH**

---

## Proposed Tiering (If Implemented)

### Phase 1: Haiku for Mechanical (Low Risk)

**Move to Haiku:**
1. `Daily Cost Log` — script + brief report
2. `Auto-Commit to GitHub` — script + result
3. `NVDA Dashboard Refresh` — fetch + error check
4. `Semantic Search Health Check` — status only
5. `Weekly Disk Cleanup` — script + result

**Estimated savings:** ~$20-50/month on these crons alone

### Phase 2: Conditional Routing (Medium Risk)

**Haiku first, escalate if needed:**
- Check scripts run successfully → Haiku reports
- Complex error → escalate to Sonnet
- Research tasks → always Sonnet
- Interactive → always Opus

### Phase 3: Task-Adaptive (Higher Complexity)

**Per-cron decision logic:**
- Morning check crons: Haiku (silent unless alert)
- Analysis crons: Sonnet (synthesis required)
- Interactive: Opus (reasoning required)

---

## Risk Analysis

### Risks of Aggressive Downtiering

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Quality degradation | Medium | Medium | Start with obvious mechanical tasks |
| Missed insights | Low | Medium | Keep analysis tasks on Sonnet |
| Debug difficulty | Low | Low | Log which model was used |
| Silent failures | Medium | Medium | Haiku + error escalation |

### Risks of NOT Changing

| Risk | Likelihood | Impact |
|------|------------|--------|
| Higher costs | High | Low-Medium |
| Over-paying for simple tasks | High | Low |

**Assessment:** Current setup is not broken. Changes are optimization, not necessity.

---

## Recommendations

### Do Now (No Approval Needed)
1. ✅ Already done: Sonnet for all crons
2. ✅ Already done: Opus for interactive

### Consider (Requires Approval)
1. **Haiku pilot:** Move 5 mechanical crons to Haiku
2. **Monitor quality:** Track any degradation
3. **Expand gradually:** If successful, identify more candidates

### Don't Do
1. ❌ ML-based routing — overkill for volume
2. ❌ LLM classification layer — adds cost
3. ❌ Aggressive downtiering — quality risk

---

## Open Questions

1. **Volume tracking:** Do we have usage data to quantify actual savings?
2. **Quality metrics:** How would we detect Haiku quality issues?
3. **Escalation logic:** How should Haiku tasks escalate to Sonnet on failure?
4. **Budget target:** Is there a specific cost ceiling we're optimizing toward?

---

## Decision Framework

```
IF task == "script + status report"
   → Haiku

ELSE IF task == "analysis/synthesis/research"
   → Sonnet
   
ELSE IF task == "interactive/reasoning/ambiguous"
   → Opus
   
ELSE
   → Default to Sonnet (safe choice)
```

---

## Summary Table

| Tier | Model | Cost/MTok | Use For | Don't Use For |
|------|-------|-----------|---------|---------------|
| 1 | Haiku | $1/$5 | Scripts, status, formatting | Any analysis |
| 2 | Sonnet | $3/$15 | Research, synthesis, structured | Complex reasoning |
| 3 | Opus | $5/$25 | Interactive, planning, ambiguous | Mechanical tasks |

---

## Next Steps (If Approved)

1. Pick 5 mechanical crons for Haiku pilot
2. Update cron configs with `model: "anthropic/claude-haiku-3"`
3. Monitor for 1 week
4. Measure savings + quality
5. Expand or revert based on results

---

*This is exploration only. No changes made. Awaiting feedback.*
