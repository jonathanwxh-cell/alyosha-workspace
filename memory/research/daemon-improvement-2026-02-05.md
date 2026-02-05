# Daemon Improvement Research — 2026-02-05

## Sources Reviewed
- Prompt Engineering Guide: LLM Agents, Reflexion
- Simon Willison: Designing Agentic Loops
- Microsoft Azure: AI Agent Orchestration Patterns
- arXiv: Self-Reflection in LLM Agents

---

## Key Insights

### 1. Agentic Loop Design (Simon Willison)
**Core principle:** "An LLM agent is something that runs tools in a loop to achieve a goal."

**What we're missing:**
- Our crons are isolated tasks, not loops toward goals
- No iteration within tasks - run once, done
- No clear "goal achieved?" check

**Improvement:** Each cron should be a mini-loop:
```
while not goal_achieved:
    observe → plan → act → evaluate
```

### 2. Reflexion Pattern (Shinn et al.)
**Core components:**
- Actor: Takes actions
- Evaluator: Scores outputs  
- Self-Reflection: Generates improvement cues

**What we have:**
- ✅ Actor (cron agents do tasks)
- ⚠️ Evaluator (partial - daemon-judge exists but disconnected)
- ❌ Self-Reflection loop (we reflect weekly, not per-task)

**Improvement:** Add reflection to EVERY task that can fail:
```
1. Execute task
2. Evaluate: Did it achieve the goal?
3. If no: Reflect on why, try again with insight
4. Store reflection in memory
```

### 3. Agent Memory Architecture
**Short-term:** Context window (what we have)
**Long-term:** External store for retrieval (what we have - memory files)

**What we're missing:**
- **Episodic memory:** Specific task outcomes linked to contexts
- **Procedural memory:** "How I solved X last time"

**Improvement:** When a task succeeds, log HOW it succeeded:
```json
{"task": "research position sizing", "approach": "searched Kelly criterion + Taleb", "outcome": "found 3 frameworks", "timestamp": "..."}
```

### 4. Orchestration Patterns (Microsoft)
**Patterns identified:**
- Sequential: A → B → C (our current approach)
- Concurrent: A + B + C simultaneously
- Handoff: A decides to pass to B or C based on context

**What we're missing:**
- Dynamic routing based on results
- Parallel execution for independent tasks
- Explicit handoff protocols between agents

**Improvement:** Foundation research could run multiple competency investigations in parallel, then synthesize.

### 5. Goal-Directed Planning
**Key insight:** Planning should happen BEFORE action, not during.

**Current flow:** Cron fires → Agent figures out what to do → Does it
**Better flow:** Cron fires → Check goal state → Plan specific actions → Execute plan → Verify

---

## Concrete Improvements to Implement

### A. Add Reflection to Daily Daemon Assessment
Instead of just reporting stats, evaluate:
- What worked today? Why?
- What failed? Why?
- What would I do differently?

### B. Create Procedural Memory
New file: `memory/procedures.jsonl`
Log successful approaches so future tasks can reference them.

### C. Goal-State Checking
Every goal-related cron should:
1. Read current state
2. Check if already achieved
3. Plan next micro-step
4. Execute
5. Update state

### D. Event-Driven Triggers (Future)
Instead of time-based crons for everything:
- "When competency file updated, check gate"
- "When position.md changes, alert if threshold hit"

---

## Implementation Priority
1. **Now:** Update Foundation Research cron with reflection loop
2. **Now:** Add procedural memory logging
3. **This week:** Add reflection to Daemon Assessment
4. **Future:** Event-driven triggers (needs OpenClaw feature)

---

*Research complete. Implementing priority items.*
