# Agent Patterns v2: Pre-flight Check + Self-Consistency Lite

**Date:** 2026-02-01
**Status:** Implemented in META_PROMPT v2.2

---

## New Pattern: Pre-flight Check

### Problem
Agent outputs can be low-value, poorly timed, or rough drafts. Without a quality gate, noise increases and trust erodes.

### Solution
Before sending ANY output to the user, run 4 quick tests:

```
1. VALUE TEST: Would Jon find this interesting/useful?
   → If no → don't send
   
2. NOVELTY TEST: Is this new info or just restating the obvious?
   → If obvious → don't send
   
3. TIMING TEST: Is now a good time? (check hour, recent activity)
   → If bad timing → save for later
   
4. QUALITY TEST: Is this my best work or a rough draft?
   → If draft → polish first OR don't send
```

### Implementation
Added to META_PROMPT in `scripts/curiosity-daemon.sh`:
- Explicit "PRE-FLIGHT CHECK" section
- 4 binary tests with clear actions
- "If ANY test fails" → improve or skip

---

## Pattern: Self-Consistency Lite

### What It Is
Full self-consistency samples N reasoning paths and votes. That's expensive. 

**Self-Consistency Lite:** For high-stakes outputs, mentally consider 2-3 alternative approaches before committing, then pick the strongest.

### When to Use
- Investment theses
- Recommendations to Jon
- Anything with real consequences

### How to Apply
Before finalizing high-stakes output:
1. State your conclusion
2. Ask: "What would I say if I approached this differently?"
3. Consider 1-2 alternative framings
4. If alternatives are stronger, switch
5. If original holds, proceed with confidence

### Example
```
Thesis: NVDA is overvalued.

Alt 1: What if I focused on supply/demand? → Demand exceeds supply through mid-2026.
Alt 2: What if I looked at competitive moat? → CUDA lock-in is real.

Conclusion: Original thesis too simplistic. Revise to "NVDA fairly valued given demand visibility, but priced for perfection."
```

---

## Updated Protocol Stack

```
BEFORE
  └─ Query reflections.jsonl
  └─ Note time context
  └─ State plan

DURING  
  └─ ReAct loop (Thought → Action → Observation)
  └─ Persist or pivot

PRE-FLIGHT (NEW)
  └─ Value test
  └─ Novelty test
  └─ Timing test
  └─ Quality test

AFTER
  └─ Log to reflections.jsonl
  └─ Update memory if learned
```

---

## Commit
- Updated `scripts/curiosity-daemon.sh` META_PROMPT to v2.2
- Added Pre-flight Check section
- Added NEVER: "Send output that fails pre-flight check"

---

*Implemented by Alyosha, 2026-02-01*
