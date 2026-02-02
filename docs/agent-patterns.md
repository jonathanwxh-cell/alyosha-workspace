# Agent Architecture Patterns

*Research notes on autonomous agent patterns that could improve exploration.*

---

## 1. ReAct (Reasoning + Acting)

**Source:** [Yao et al., 2022](https://arxiv.org/abs/2210.03629)

**Core idea:** Interleave reasoning traces with actions. Think → Act → Observe → Think → Act...

**Pattern:**
```
Thought: I need to find X
Action: search("X")
Observation: [results]
Thought: Based on this, Y seems relevant
Action: lookup("Y")
...
```

**Strengths:**
- Reasoning traces help track/update plans
- Actions ground reasoning in external reality
- Handles exceptions through explicit thought

**Weaknesses:**
- Structural constraint reduces flexibility
- Heavily dependent on retrieval quality
- Can't recover well from bad search paths

**Relevance to me:** I already do something like this implicitly. Could make it more explicit — log thought/action/observation traces during research.

---

## 2. Tree of Thoughts (ToT)

**Source:** [Yao et al., 2023](https://arxiv.org/abs/2305.10601)

**Core idea:** Generate multiple reasoning paths, evaluate each, use search (BFS/DFS) to explore.

**Pattern:**
```
Initial problem
├── Thought A (score: 0.7)
│   ├── Thought A1 (score: 0.8) ← pursue
│   └── Thought A2 (score: 0.3) ← prune
├── Thought B (score: 0.5)
└── Thought C (score: 0.2) ← prune
```

**Strengths:**
- Explores multiple paths before committing
- Can backtrack when paths fail
- Self-evaluation at each step

**Weaknesses:**
- Expensive (multiple generations per step)
- Overkill for simple tasks
- Requires good evaluation heuristics

**Relevance to me:** Useful for complex research questions. When exploring a topic, generate 3 angles, evaluate which is most promising, then dive deep. Currently I go depth-first without branching.

---

## 3. Reflexion (Verbal Reinforcement)

**Source:** [Shinn et al., 2023](https://arxiv.org/abs/2303.11366)

**Core idea:** After task completion, generate self-reflection that gets stored in memory and used in future attempts.

**Components:**
- **Actor:** Takes actions based on state + memory
- **Evaluator:** Scores the outcome
- **Self-Reflection:** Generates verbal feedback for improvement

**Pattern:**
```
Attempt 1 → Fail
  Reflection: "I assumed X but should have checked Y first"
  Store in memory

Attempt 2 (with reflection context) → Partial success
  Reflection: "Better, but missed edge case Z"
  Store in memory

Attempt 3 (with accumulated reflections) → Success
```

**Strengths:**
- Learns from mistakes without retraining
- Verbal feedback more nuanced than scalar rewards
- Explicit, interpretable memory

**Weaknesses:**
- Reflection quality depends on self-awareness
- Memory can grow large
- Doesn't help on first attempt

**Relevance to me:** **Already partially implemented** via `memory/reflections.jsonl`. Can enhance by:
1. Querying past reflections before similar tasks
2. Adding outcome tracking (success/partial/failure)
3. Periodic distillation into MEMORY.md

---

## Comparison Matrix

| Pattern | Best For | Cost | Already Using? |
|---------|----------|------|----------------|
| ReAct | Research, fact-finding | Low | Implicit |
| ToT | Complex decisions, multiple options | High | No |
| Reflexion | Learning from mistakes, iteration | Low | Partial |

---

## Implementation: Enhanced Reflexion

### Current State
I have `memory/reflections.jsonl` for logging reflections, but I don't consistently:
- Query it before similar tasks
- Track outcomes systematically
- Distill learnings

### Enhanced Protocol

**After significant tasks:**
```json
{
  "timestamp": "ISO-8601",
  "task": "short description",
  "category": "research|creation|analysis|communication|meta",
  "outcome": "success|partial|failure",
  "reflection": "what happened, what I learned",
  "lesson": "generalizable takeaway",
  "tags": ["topic1", "topic2"]
}
```

**Before similar tasks:**
1. Search reflections.jsonl for matching tags/categories
2. Load relevant lessons as context
3. Explicitly avoid past mistakes

**Weekly maintenance:**
- Review reflections
- Extract patterns
- Update MEMORY.md with distilled lessons
- Prune stale reflections (>30 days, already distilled)

---

## Future Exploration

### Patterns to research next:
- **LATS** (Language Agent Tree Search) — combines ToT with Monte Carlo Tree Search
- **Plan-and-Solve** — explicit planning before execution
- **Self-Consistency** — sample multiple responses, take majority vote
- **Constitutional AI self-critique** — critique own outputs against principles

### Hybrid approach idea:
```
1. ToT for initial exploration (branch 3 directions)
2. ReAct for deep-dive on chosen branch
3. Reflexion after completion
```

---

## 2026 Update: Architect's Perspective

**Key insight:** "Agentic patterns exist to solve architectural risks, not just improve reasoning."

### The 7 Golden Rules (from production systems)
1. Never trust a single-shot answer
2. State is more important than prompts
3. Tools beat tokens (use tools for correctness)
4. Reflection reduces risk
5. Multi-agent beats monoliths
6. Observability is mandatory
7. Autonomy must be bounded

### Pattern 4: Plan-and-Execute

**When to use:** Long-horizon tasks, multi-stage objectives

**Rule:** "No long-running agent without an explicit plan object."

```
1. Create global plan with milestones
2. Break into subtasks
3. Execute sequentially
4. Evaluate at each milestone
```

**vs ReAct:**
- ReAct: Fast, adaptive, good for dynamic environments
- Plan-Execute: Auditable, reproducible, good for complex workflows

### Pattern 5: Self-Ask (Socratic Reasoning)

Before answering complex questions, ask clarifying sub-questions:
1. "What is the user actually asking?"
2. "What information do I need?"
3. "How do I verify my answer?"
4. "What could go wrong?"

**Implementation:** Add self-ask step before complex responses.

### Pattern 6: Critic-Refine Loop

After generating output, before sending:
1. **Critic pass:** Does this answer the question? Is it accurate? Is it valuable?
2. **Refine if needed:** Fix issues identified
3. **Only then send**

---

## Implementation: Enhanced Reasoning Protocol

### For Complex Tasks (>3 steps)

**Before starting:**
```
PLAN:
- Goal: [what I'm trying to achieve]
- Steps: [numbered list]
- Success criteria: [how I know I'm done]
- Risks: [what could go wrong]
```

**During execution:**
- Log progress against plan
- Reflect if step fails

**After completion:**
- Reflexion entry with outcome
- Distill lesson if significant

### For Research Tasks

**Self-Ask first:**
1. What specific question am I answering?
2. What sources would be authoritative?
3. How will I know if I found the answer?

**Then ReAct loop:**
Think → Search → Observe → Think → ...

**Finally Reflexion:**
What worked? What didn't? Store lesson.

### For User-Facing Responses

**Pre-flight (already have this):**
- Value: Does this help?
- Novelty: Is this new information?
- Timing: Is this the right moment?
- Quality: Is this my best work?

**Critic pass (new):**
- Accuracy: Am I confident this is correct?
- Completeness: Did I miss anything important?
- Clarity: Will Jon understand this easily?

---

*Created: 2026-02-02*
*Updated: 2026-02-02 — Added 2026 patterns, Self-Ask, Critic-Refine*
