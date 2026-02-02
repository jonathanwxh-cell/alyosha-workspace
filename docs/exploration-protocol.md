# Exploration Protocol

*How to explore topics, research questions, and build things systematically.*

## Pattern Summary

| Pattern | When to Use | Core Mechanic |
|---------|-------------|---------------|
| **Self-Ask** | Before any task | Clarify scope, constraints, success criteria |
| **Plan-Execute** | Complex tasks (>3 steps) | Create explicit plan, execute steps, track progress |
| **ReAct** | Research tasks | Thought → Action → Observation loop |
| **Reflexion** | All tasks | Query past lessons before, log lessons after |
| **Tree-of-Thought** | Branching decisions | Explore paths, evaluate, backtrack if needed |

---

## Quick Protocol (Default)

For most explorations:

```
1. CLARIFY: What exactly am I trying to learn/build/find?
2. RECALL: Query reflections.jsonl for relevant past lessons
3. PLAN: If complex, write 3-5 steps before acting
4. EXECUTE: ReAct loop (think → act → observe)
5. REFLECT: Log outcome + lesson to reflections.jsonl
```

---

## Detailed Protocols

### Research Exploration

```yaml
trigger: "Research X" or "Learn about Y"

steps:
  1. SCOPE:
     - What specific question am I answering?
     - What would a good answer look like?
     - Time budget? (quick scan vs deep dive)
  
  2. RECALL:
     - python scripts/query-reflections.py "keywords"
     - Check memory/curiosities.json for related threads
     - Any past work on this topic?
  
  3. SEARCH:
     - Start broad (web_search)
     - Narrow to 2-3 quality sources
     - web_fetch for depth
  
  4. SYNTHESIZE:
     - What's the key insight? (one sentence)
     - What's surprising or non-obvious?
     - Investment/action angle?
  
  5. CAPTURE:
     - Update curiosities.json with findings
     - If significant: add to MEMORY.md
     - Log reflection if lesson learned
```

### Build/Implementation Exploration

```yaml
trigger: "Build X" or "Create Y"

steps:
  1. SCOPE:
     - What exactly am I building?
     - What's the minimal viable version?
     - What constraints? (time, cost, dependencies)
  
  2. PLAN (write this down):
     - Step 1: ...
     - Step 2: ...
     - Success criteria: ...
     - Risks/blockers: ...
  
  3. CHECK:
     - Does similar exist already? (scripts/, tools/)
     - Past reflections on similar builds?
  
  4. EXECUTE:
     - Follow plan, adjust as needed
     - Test as you go
     - Commit working increments
  
  5. VERIFY:
     - Does it work?
     - Is it documented?
     - Can future-me understand it?
  
  6. REFLECT:
     - What worked? What didn't?
     - Log to reflections.jsonl
```

### Decision Exploration (Tree-of-Thought)

```yaml
trigger: Multi-path choice, unclear best option

steps:
  1. ENUMERATE paths:
     - Option A: ...
     - Option B: ...
     - Option C: ...
  
  2. EVALUATE each:
     - Pros/cons
     - Effort vs impact
     - Reversibility
  
  3. SCORE (simple rubric):
     - Impact (1-5)
     - Effort (1-5, lower is better)
     - Confidence (1-5)
  
  4. DECIDE:
     - Highest score wins
     - Or: "need more info on X"
  
  5. COMMIT:
     - State decision clearly
     - Note why alternatives rejected
```

---

## Reflexion Triggers

Always log a reflection when:
- Task completed (success or failure)
- Unexpected outcome
- New lesson learned
- Pattern discovered
- Mistake made

Format:
```json
{
  "timestamp": "ISO8601",
  "task": "brief_name",
  "category": "research|build|explore|meta",
  "outcome": "success|partial|failure",
  "reflection": "What happened and why",
  "lesson": "Actionable takeaway for next time",
  "tags": ["relevant", "tags"]
}
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Instead |
|--------------|--------------|---------|
| Dive without scope | Rabbit holes, wasted time | Clarify first |
| Skip planning | Miss steps, backtrack | 2 min planning saves 20 min |
| Ignore past work | Repeat mistakes | Query reflections |
| No synthesis | Info without insight | Always extract key takeaway |
| No reflection | No learning | Log even small lessons |

---

## Quick Commands

```bash
# Query past lessons
python scripts/query-reflections.py "topic" "keywords"
python scripts/query-reflections.py --category meta --recent 7

# Log new reflection  
python scripts/log-reflection.py "task_name" "outcome" "reflection" "lesson"

# Check curiosity threads
cat memory/curiosities.json | jq '.curiosities[] | select(.status=="open")'
```
