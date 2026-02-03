# Agent Patterns Reference

*Patterns for autonomous exploration and self-improvement.*

---

## 1. ReAct (Reasoning + Acting)

**Source:** Yao et al., 2022

**Pattern:** Interleave reasoning traces with actions.
```
Thought: What do I need to find out?
Action: [tool call]
Observation: [result]
Thought: Based on this, what next?
...
```

**When to use:** Research tasks, tool-heavy exploration, information gathering.

**Already implicit in my operation.** Claude naturally does think → act → observe.

---

## 2. Tree of Thoughts (ToT)

**Source:** Yao et al., 2023

**Pattern:** Maintain tree of possible paths, evaluate each, prune bad branches.
```
Branch A: [approach 1] → evaluate: "maybe"
Branch B: [approach 2] → evaluate: "sure" ← pursue
Branch C: [approach 3] → evaluate: "impossible" ← prune
```

**When to use:** Complex decisions with multiple valid paths, strategic lookahead required.

**Trade-off:** Expensive (multiple LLM calls). Use sparingly for high-stakes decisions.

**Implementation:** For complex tasks (>3 steps), explicitly list 2-3 approaches, evaluate each briefly, then pursue best.

---

## 3. Reflexion (Verbal Reinforcement Learning)

**Source:** Shinn et al., 2023 — 91% on HumanEval vs GPT-4's 80%

**Pattern:** After task completion, verbally reflect and store lessons.
```json
{
  "task": "what I attempted",
  "outcome": "success|partial|failure",
  "reflection": "what happened, why",
  "lesson": "actionable takeaway for future"
}
```

**Key insight:** Learning without weight updates. Memory IS the improvement mechanism.

**Implementation:**
1. **Before similar tasks:** Query `memory/reflections.jsonl` for relevant lessons
2. **After significant tasks:** Append structured reflection
3. **Periodically:** Distill patterns into MEMORY.md

**Script:** `python3 scripts/log-reflection.py "task" "outcome" "reflection" "lesson"`

---

## 4. Self-Ask (Clarifying Questions)

**Pattern:** Before answering, generate and answer clarifying sub-questions.
```
Question: [original task]
Self-Ask: What exactly is being asked?
Self-Ask: What constraints apply?
Self-Ask: What would "done" look like?
Then: Proceed with clarity
```

**When to use:** Ambiguous requests, complex multi-part tasks.

---

## 5. Plan-Execute (Explicit Planning)

**Pattern:** For complex tasks, create explicit plan BEFORE acting.
```
PLAN: [goal]
STEPS:
1. [action] → [expected outcome]
2. [action] → [expected outcome]
3. [action] → [expected outcome]
SUCCESS CRITERIA: [how to verify done]
RISKS: [what could go wrong]
```

**When to use:** Multi-step tasks, anything that could take >3 tool calls.

---

## 6. Critic-Refine (Self-Review)

**Pattern:** Before sending output, review against quality criteria.
```
DRAFT: [initial output]
CRITIC:
- [ ] Answers the actual question?
- [ ] Non-obvious insight included?
- [ ] Appropriate length/format?
- [ ] Worth recipient's attention?
REFINE: [improved output]
```

**When to use:** All proactive surfaces, anything going to Jon.

---

## Hybrid: My Exploration Protocol

For significant exploration tasks:

```
1. SELF-ASK: What am I trying to achieve? What does success look like?
2. REFLECT-BEFORE: Query past reflections for relevant lessons
3. PLAN: If >3 steps, create explicit plan
4. EXECUTE: ReAct loop (think → act → observe)
5. BRANCH: If stuck, ToT — list alternatives, evaluate, pick best
6. CRITIC: Before output, quality check
7. REFLECT-AFTER: Log to reflections.jsonl
```

---

## Pattern Selection Heuristic

| Task Type | Primary Pattern |
|-----------|-----------------|
| Research/exploration | ReAct |
| Complex decisions | ToT (branching) |
| Learning from experience | Reflexion |
| Ambiguous requests | Self-Ask |
| Multi-step builds | Plan-Execute |
| Proactive outputs | Critic-Refine |

---

*Last updated: 2026-02-02*

---

## 7. Self-Evolution (Daemon-level)

**Pattern:** Periodic analysis → suggestions → behavioral adjustment

**Implementation:**
```
┌─────────────────────────────────────────────────────┐
│                 SELF-EVOLUTION LOOP                 │
├─────────────────────────────────────────────────────┤
│  1. OBSERVE: Track engagement per content category  │
│  2. ANALYZE: Calculate health scores                │
│  3. SUGGEST: Generate improvement recommendations   │
│  4. APPLY: Adjust scheduling, content mix, timing   │
│  5. REPEAT: Weekly cycle                            │
└─────────────────────────────────────────────────────┘
```

**Key insight:** Can't retrain the LLM, but CAN:
- Adjust prompt templates
- Shift cron schedules
- Change content category weights
- Learn optimal timing windows

**Script:** `scripts/cron-autotuner.py evolve`

**References:**
- OpenAI Cookbook: Self-Evolving Agents
- EvoAgentX Survey (GitHub)
- STOP: Self-Taught Optimizer (2024)

---

## 8. Pipeline Pattern (Sequential Checkpoints)

**Pattern:** Multi-stage processing with explicit quality gates

**Structure:**
```
STAGE 1: GATHER
  ↓ checkpoint: sufficient coverage?
STAGE 2: FILTER  
  ↓ checkpoint: notable items remain?
STAGE 3: ANALYZE
  ↓ checkpoint: high-confidence insights?
STAGE 4: SYNTHESIZE
  ↓ checkpoint: proud to send?
STAGE 5: OUTPUT (or abort)
```

**Benefits:**
- Prevents error cascade
- Early abort saves tokens
- Targeted debugging
- Quality gates prevent low-value outputs

**When to use:**
- Research tasks needing multi-step refinement
- High-stakes outputs (market analysis, recommendations)
- Complex synthesis from multiple sources

**Checkpoint template:**
```
✓ CHECKPOINT: [Quality question]?
If NO → [abort condition or fix action]
```

**References:**
- Microsoft Azure Sequential Orchestration Pattern
- Google Cloud Agentic AI Design Patterns
