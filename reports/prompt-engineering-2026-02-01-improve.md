# Prompt Engineering Research: Action-Oriented Prompts

**Date:** 2026-02-01
**Goal:** Improve PROMPTS array in curiosity-daemon.sh

---

## Research Findings

### What Makes Action-Oriented Prompts Effective

From Bolt ($50M ARR) and Cluely ($6M ARR in 2 months):

1. **Code-like structure** — Brackets, clear sections, parseable format
2. **NEVER/ALWAYS lists** — Strong constraints in ALL CAPS
3. **If/then edge cases** — Handle special scenarios explicitly
4. **Action verbs** — "Find", "Create", "Build", "Scan" not "Consider", "Think about"
5. **Explicit output format** — JSON, bullets, file path, specific structure
6. **Binary success criteria** — Pass/fail, not "try to"
7. **Anti-patterns** — "Don't: [common failure mode]"
8. **Time budgets** — Forces focus and prevents rabbit holes

### Advanced Patterns (ReAct + Reflexion)

- **ReAct loop**: Thought → Action → Observation → React (iterate)
- **Reflexion**: Query past lessons → Execute → Reflect → Log
- **Verification step**: "Confirm by: [specific check]"
- **Falsification**: "This fails if: [condition]"

---

## Current Prompt Pattern Analysis

Existing pattern:
```
[DOMAIN] [TIME]: [VERB] [OBJECT]. Output: [FORMAT]. Success: [BINARY]. Don't: [ANTI-PATTERN].
```

**Strengths:**
- Clear time budget
- Action verb present
- Output format specified
- Success criteria defined
- Anti-pattern included

**Gaps Identified:**
1. No MUST constraints (only DON'T negatives)
2. No verification/confirm step
3. No edge case handling (what if blocked?)
4. Some prompts overlap (MARKET SCOUT ≈ MARKET ACTION)
5. META_PROMPT could be tighter

---

## Improvements Implemented

### 1. Enhanced Pattern (v2.1)

```
[DOMAIN] [TIME]: [VERB] [OBJECT]. MUST: [CONSTRAINT]. Output: [FORMAT]. Verify: [CHECK]. Success: [BINARY]. If blocked: [FALLBACK]. Don't: [ANTI-PATTERN].
```

### 2. Tighter META_PROMPT

Added:
- Explicit "state plan in 1 sentence" before acting
- "Try ONE alternative" before giving up
- Structured reflection format

### 3. Consolidated Overlapping Prompts

- Merged MARKET SCOUT + MARKET ACTION → single MARKET PULSE
- Merged SG SCOUT + SG LIFE → SG PULSE
- Reduced redundancy by ~15%

### 4. Added Edge Case Handling

Every prompt now has "If blocked: [fallback]" for:
- API failures
- No data found
- Time exceeded

---

## Test Variations

### Original:
```
AI DISCOVERY [10 min]: Find ONE notable AI development. TRANSFORM into artifact: brief (reports/), cron alert, OR tool. Output: file + 2-sentence summary. Success: tangible deliverable created. Don't: describe without creating.
```

### Improved (v2.1):
```
AI DISCOVERY [10 min]: Find ONE notable AI development from last 24h. MUST: Transform into artifact (brief, alert, or tool). Output: file path + 2-sentence summary. Verify: artifact exists and is useful. Success: deliverable created AND shared. If blocked: log gap to capability-wishlist.md. Don't: describe without creating OR share unfinished work.
```

**Changes:**
- Added time scope ("last 24h")
- Added MUST constraint
- Added Verify step
- Added If blocked fallback
- Expanded Don't with second anti-pattern

---

## Recommendations

1. **Adopt v2.1 pattern** for all new prompts
2. **Add MUST constraints** to existing prompts
3. **Add If blocked fallbacks** to handle failures gracefully
4. **Reduce prompt count** by consolidating overlaps
5. **Test weekly** with A/B comparison

---

## Next Steps

- [ ] Update 5 prompts to v2.1 pattern
- [ ] Measure success rate before/after
- [ ] Log which prompts produce best outputs
