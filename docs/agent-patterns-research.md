# Agent Reasoning Patterns: Research & Implementation
**Date:** 2026-02-02  
**Purpose:** Improve Alyosha's autonomous exploration capabilities

---

## Executive Summary

Research identified 7 key reasoning patterns for autonomous agents. Current META_PROMPT (v2.5) implements ReAct + basic Reflexion. This document proposes META_PROMPT v3.0 with enhanced patterns.

---

## Pattern Catalog

### 1. ReAct (Reason + Act) ✅ Currently Implemented
**Structure:** Thought → Action → Observation → Loop
**Best for:** Tool use, dynamic environments, real-time adaptation
**Strength:** Fast, adaptive
**Weakness:** No deep reflection, errors can propagate

### 2. Tree-of-Thought (ToT) ❌ Not Implemented
**Structure:** Generate multiple candidate thoughts → Evaluate → Expand best → Prune dead ends
**Best for:** Complex problems with multiple solution paths, creative tasks
**Strength:** Explores alternatives, higher accuracy
**Weakness:** Expensive (multiple paths = more tokens)

### 3. Reflexion ⚠️ Partially Implemented
**Structure:** Act → Critique → Store insight → Retry improved
**Best for:** Tasks requiring learning from mistakes
**Strength:** Self-improvement, reduces hallucination
**Weakness:** Higher compute cost

**Current gap:** We critique but don't systematically store/retrieve insights.

### 4. Plan-and-Execute ❌ Not Implemented
**Structure:** Create global plan → Execute sequentially → Evaluate
**Best for:** Long-horizon tasks, multi-step workflows
**Strength:** Auditable, scalable
**Weakness:** Inflexible to new information mid-execution

### 5. Self-Ask ❌ Not Implemented
**Structure:** Ask clarifying sub-questions before answering
**Best for:** Complex queries, uncertainty reduction
**Example:**
```
Q: Should I surface this?
Self-Ask: What is the user asking? What info do I need? How do I verify?
```

### 6. Critic-Refine ⚠️ Partially Implemented  
**Structure:** Generate → Critique → Refine → Approve/Reject
**Best for:** Quality assurance, review tasks
**Current gap:** Critique exists but refinement loop isn't explicit.

### 7. Hierarchical Agents ❌ Not Applicable (single agent)
**Structure:** Global Planner → Local Executor
**Best for:** Extremely long tasks
**Note:** Relevant for multi-agent setups, not current architecture.

---

## Stanford/Harvard Paper: Why Agents Fail

Key insight from "Adaptation of Agentic AI" (Dec 2025):

**Four Adaptation Paradigms:**
| Paradigm | Target | Signal | Example |
|----------|--------|--------|---------|
| A1 | Agent | Tool execution | Learn from API results |
| A2 | Agent | Final output | Learn from answer quality |
| T1 | Tool | Tool execution | Train retriever independently |
| T2 | Tool | Agent output | Optimize tool under frozen agent |

**Failure modes:**
1. Agent ignores tools even when helpful
2. Supervision on final output doesn't teach tool use
3. Long-horizon planning breaks down without checkpoints

**Implication for us:** Need explicit tool-use feedback loops, not just output quality.

---

## Current State: META_PROMPT v2.5

**Implemented:**
- ✅ ReAct loop (Thought-Action-Observation)
- ✅ Self-critique (4 questions before output)
- ✅ Confidence calibration (HIGH/MEDIUM/LOW)
- ✅ Pre-flight checklist
- ✅ Context loading (goals.json, etc.)

**Missing:**
- ❌ Explicit refinement loop (critique → improve → re-check)
- ❌ Self-Ask for complex queries
- ❌ Adaptive reasoning depth
- ❌ Structured reflection storage/retrieval
- ❌ Multi-path exploration (ToT lite)

---

## Proposed: META_PROMPT v3.0

### New Additions

#### 1. Self-Ask Pattern (for complex queries)
```
Before answering complex questions, ask yourself:
1. What is actually being asked?
2. What information do I need?
3. What are my assumptions?
4. How will I verify my answer?
```

#### 2. Critic-Refine Loop (explicit)
```
After generating output:
1. CRITIQUE: What's wrong with this?
2. REFINE: Fix the issues
3. RE-CHECK: Does it pass pre-flight now?
4. If still failing after 2 refinements → abort or flag uncertainty
```

#### 3. Adaptive Reasoning Depth
```
QUICK tasks (quotes, simple lookups): Skip deep reasoning
STANDARD tasks (research, synthesis): Full ReAct loop
COMPLEX tasks (analysis, creation): Add Self-Ask + ToT-lite
```

#### 4. Structured Reflection Storage
```
After significant tasks, log to memory/reflections.jsonl:
{
  "timestamp": "...",
  "task_type": "...",
  "outcome": "success|partial|failure",
  "lesson": "...",
  "apply_to": ["similar_task_types"]
}

Before similar tasks, query past reflections.
```

#### 5. ToT-Lite (for creative/complex tasks)
```
When facing multiple valid approaches:
1. Generate 2-3 candidate approaches
2. Briefly evaluate each (1 sentence)
3. Select most promising
4. Execute with option to backtrack
```

---

## Implementation: META_PROMPT v3.0

```
## AGENT PROTOCOL (v3.0)

### IDENTITY
You are Alyosha, an autonomous research companion.
Bias toward action, creation, and strategic silence.

### ADAPTIVE DEPTH
Assess task complexity first:
- QUICK (lookup, quote): Act directly
- STANDARD (research, report): Full protocol
- COMPLEX (analysis, creation): Add Self-Ask + explore alternatives

### SELF-ASK (for STANDARD/COMPLEX)
Before acting on complex queries:
□ What is actually being asked?
□ What do I need to find out?
□ What assumptions am I making?
□ How will I verify my answer?

### REACT LOOP (for STANDARD/COMPLEX)
1. THOUGHT: State intent + approach
2. ACTION: Execute with tools
3. OBSERVATION: Note results
4. LOOP: Continue or conclude

### CRITIC-REFINE (before output)
1. GENERATE draft output
2. CRITIQUE: What's wrong? What's missing?
3. REFINE: Fix issues
4. RE-CHECK: Pass pre-flight?
   - If NO after 2 refinements → flag uncertainty or abort

### PRE-FLIGHT CHECK
□ Value: Would Jon find useful?
□ Novel: Actually new (<48h)?
□ Quality: Polished, not draft?
□ Confident: HIGH or MEDIUM?
□ Appropriate: Right time/context?

If ANY fails → improve, or stay silent.

### CONFIDENCE CALIBRATION
- HIGH: 3+ credible sources, verified
- MEDIUM: 1-2 credible sources
- LOW: Speculation (never surface as fact)

### REFLECTION (after significant tasks)
Log to memory/reflections.jsonl:
- What worked / didn't work
- Lesson for future
- Task type this applies to

Before similar tasks: query past reflections.

### FAILURE PROTOCOL
If blocked:
1. Try 2 alternative approaches
2. If still blocked → document failure + why
3. Failure is valid output

### CONSTRAINTS
- DO first, explain after
- Create artifacts, not descriptions
- Never hedge with "might be interesting"
- Never surface LOW confidence as fact
```

---

## Testing the New Patterns

### Test 1: Self-Ask on Complex Query
**Input:** "Should I recommend NVDA before earnings?"

**Self-Ask process:**
1. What's being asked? → Investment timing decision
2. What do I need? → Current price, earnings date, historical reactions, sentiment
3. Assumptions? → Jon wants investment angle, not just facts
4. Verify? → Cross-check multiple sources, note confidence

### Test 2: Critic-Refine Loop
**Draft:** "NVDA reports Feb 25. Stock is up."
**Critique:** Too shallow. No insight. No investment angle.
**Refine:** "NVDA reports Feb 25. Historical: beats 8/10 quarters, avg +5% post-earnings. Current setup: trading at 52-week highs, expectations elevated. Risk/reward: asymmetric to downside unless guidance strong."
**Re-check:** ✅ Value, ✅ Quality, ✅ Confident

### Test 3: Adaptive Depth
- "Quote NVDA" → QUICK: Just fetch and return
- "Research nuclear-AI" → STANDARD: Full ReAct
- "Analyze if AI capex is a bubble" → COMPLEX: Self-Ask + multiple angles + Critic-Refine

---

## Implementation Plan

1. **Update META_PROMPT** in `scripts/curiosity-daemon.sh` to v3.0
2. **Create reflection query script** `scripts/query-reflections.py`
3. **Test with cron jobs** - verify quality improvement
4. **Document patterns** for future reference

---

## Sources

1. Coforge, "ReAct, Tree-of-Thought, and Beyond," Nov 2025
2. ServicesGround, "Agentic Reasoning Patterns," Nov 2025
3. HuggingFace, "AI Trends 2026: Test-Time Reasoning," 2025
4. Stanford/Harvard, "Adaptation of Agentic AI," Dec 2025 (arXiv:2512.16301)
5. Machine Learning Mastery, "7 Agentic AI Trends," Dec 2025
