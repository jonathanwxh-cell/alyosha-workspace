# Daemon Improvement Research
## How to Make This Curiosity Daemon Better

*Research Date: 2026-02-03*
*Sources: LangMem, Letta, Yohei Nakajima (BabyAGI creator), ByteByteGo, ArXiv, PromptingGuide*

---

## 1. Memory Architecture Improvements

### Current State
| Memory Type | Current Implementation | Gap |
|-------------|----------------------|-----|
| **Semantic** (facts) | MEMORY.md, USER.md | Manual curation only |
| **Episodic** (experiences) | memory/YYYY-MM-DD.md, reflections.jsonl | No automated extraction |
| **Procedural** (behavior) | AGENTS.md, HEARTBEAT.md, protocols/ | Good |
| **Working** (current context) | Session state | Lost on compaction |

### Research Findings

**From LangMem (LangChain):**
> "The best memory systems are often application-specific. Memory relevance is more than just semantic similarity. Recall should combine similarity with 'importance' of the memory, as well as the memory's 'strength', which is a function of how recently/frequently it was used."

**From Letta:**
> "Stateful agents" maintain persistent memory and actually learn during deployment, not just during training. Memory blocks provide structured, editable storage — agents can update their own memory blocks using tools.

### Improvements to Implement

#### A. Automated Memory Extraction
Create a "subconscious" memory formation process that runs after conversations:

```python
# scripts/memory-extract.py
# Run after significant sessions to extract:
# - New facts about Jon (→ USER.md)
# - Lessons learned (→ MEMORY.md)  
# - Decisions made (→ daily log)
# - Patterns noticed (→ insights file)
```

**Implementation:** Add to nightly cron — analyze day's conversations, extract memories.

#### B. Memory Importance Scoring
Not all memories are equal. Add importance + recency weighting:

```json
{
  "memory": "Jon prefers text over audio",
  "importance": 0.9,
  "lastAccessed": "2026-02-03",
  "accessCount": 5,
  "source": "explicit feedback"
}
```

#### C. Memory Consolidation ("Sleep-Time" Processing)
From Letta: "Sleep-time agents" can modify memory blocks. Implement:
- Weekly: Review daily logs → distill into MEMORY.md
- Monthly: Archive old entries, update importance scores
- **Already have:** Monthly Memory Compaction cron — enhance it

---

## 2. Self-Improvement Patterns

### Research Findings

**From Yohei Nakajima (BabyAGI creator), NeurIPS 2025 synthesis:**

Six mechanisms for self-improving agents:

| Mechanism | Description | Our Status |
|-----------|-------------|------------|
| **Self-reflection** | Prompt-level improvement via reflection | ✅ Have (Reflexion in curiosity-engine) |
| **Self-generated data** | Agents create data they learn from | ❌ Missing |
| **Self-adapting** | Agents fine-tune themselves | N/A (no fine-tuning) |
| **Self-improving code** | Agents modify own code/policies | ⚠️ Partial (can edit files) |
| **Embodied** | Learn by acting in environments | ⚠️ Partial (cron feedback) |
| **Verification** | Keep improvement safe | ⚠️ Partial (need guardrails) |

**Key insight from Reflexion paper:**
> "Reflexion is best suited when an agent needs to learn from trial and error... It utilizes verbal feedback, which can be more nuanced and specific than scalar rewards."

**Key insight from Self-Challenging Agents (NeurIPS 2025):**
> "The challenger creates new tasks... The executor tries them. This auto-curriculum lets the agent practice exactly what it's weak at."

### Improvements to Implement

#### A. Enhanced Reflexion Loop
Current: Query reflections before tasks
Enhanced: Score confidence, log outcome, update reflection quality

```
BEFORE TASK:
1. Query: scripts/query-reflections.py "topic"
2. State plan with confidence: "PLAN: X → Y → Z (confidence: 70%)"

AFTER TASK:
3. Self-score: "OUTCOME: [YES/PARTIAL/NO] because..."
4. If PARTIAL/NO: "LESSON: ..."
5. Log to reflections.jsonl with structured fields
```

#### B. Self-Challenging Curriculum
Add a cron that generates practice tasks based on weak areas:

```
SELF-CHALLENGE:
1. Review recent failures from reflections.jsonl
2. Generate a practice task targeting that weakness
3. Attempt it
4. Log result
```

**Example:** If I repeatedly fail at "reading content before recommending," generate a practice task: "Find and deeply analyze one paper on X, produce 500-word synthesis."

#### C. Output Self-Scoring
For every significant output, self-score before sending:

```
SELF-SCORE:
- Relevance (1-10): [X]
- Depth (1-10): [X]
- Actionability (1-10): [X]
- Would Jon find this valuable? [Y/N]

If avg < 7 or N → revise before sending
```

---

## 3. Scheduling Patterns

### Research Findings

**From ArXiv "Agent.xpu" paper:**
> "Reactive tasks, initiated by users, demand immediate, low-latency responses, while proactive tasks operate invisibly and prioritize throughput. Proactive agents are ambient, digesting event streams in the background without hard deadlines."

**Two workload types:**
| Type | Trigger | Priority | Our Examples |
|------|---------|----------|--------------|
| **Reactive** | User message | Immediate | Direct chats |
| **Proactive** | Time/event | Background | Crons, heartbeats |

**Key insight:**
> "Proactive workload, where daemon-like agents listen to predetermined event signals and act on them accordingly without human intervention."

### Current State
- 30+ crons (time-based)
- Heartbeat polling (time-based)
- No true event-driven triggers

### Improvements to Implement

#### A. Event-Driven Triggers
Move from "check every N hours" to "react when something happens":

| Current (Time-Based) | Better (Event-Driven) |
|---------------------|----------------------|
| "Check email every 8:45am" | "Alert when urgent email arrives" |
| "Check GitHub every 6 hours" | "Alert on new release" |
| "Check market every morning" | "Alert on >3% move" |

**Implementation:** Use webhooks where available. For polling, check more frequently but only surface on state change.

#### B. Workload Classification
Tag each cron as REACTIVE-SUPPORT or PROACTIVE:

```json
{
  "name": "Daily World State",
  "type": "proactive",
  "priority": "background",
  "canDefer": true,
  "maxLatency": "4h"
}
```

This allows intelligent scheduling: defer proactive work when reactive work is active.

#### C. Adaptive Scheduling
Already have `scheduling-advisor.py`. Enhance with:
- Burst mode (high engagement → more surfaces)
- Backoff mode (low engagement → fewer surfaces)
- Time-slot learning (which hours get responses?)

---

## 4. Agentic Workflow Patterns

### Research Findings

**From ByteByteGo "Top AI Agentic Workflow Patterns":**

Five essential patterns:

| Pattern | Description | Our Implementation |
|---------|-------------|-------------------|
| **Reflection** | Generate → critique → revise | ⚠️ Partial (manual) |
| **Tool Use** | Use external tools | ✅ Good (many tools) |
| **Planning** | Break down complex tasks | ⚠️ Inconsistent |
| **Multi-Agent** | Specialized agents collaborate | ✅ Have (sub-agents) |
| **ReAct** | Reason + Act interleaved | ✅ Natural behavior |

**Key insight on Reflection:**
> "Instead of generating output in a single pass, agentic workflows involve cycles where the agent takes an action, observes the result, and uses that observation to inform the next action."

### Improvements to Implement

#### A. Mandatory Reflection for Complex Tasks
For tasks >3 steps, require explicit planning and reflection:

```
COMPLEX TASK PROTOCOL:
1. PLAN: State steps with success criteria
2. EXECUTE: Do each step
3. CHECKPOINT: After each step, assess
4. REFLECT: What worked? What didn't?
5. LOG: Update reflections.jsonl
```

#### B. Specialized Sub-Agents
Current: Generic sub-agents
Better: Role-specialized agents

| Role | Specialization |
|------|---------------|
| Researcher | Deep dives, source reading |
| Curator | Content selection + analysis |
| Builder | Code, tools, infrastructure |
| Monitor | Event watching, alerting |

#### C. Self-Ask Pattern
Before complex tasks, decompose into sub-questions:

```
TASK: "Research AI infrastructure fragility"

SELF-ASK:
Q1: What are the main infrastructure components?
Q2: Where are the concentration risks?
Q3: What would break the system?
Q4: What's the investment implication?

Then answer each, synthesize.
```

---

## 5. Concrete Implementation Plan

### Immediate (This Week)

| Improvement | File to Create/Edit | Priority |
|-------------|-------------------|----------|
| Enhanced Reflexion logging | Edit: scripts/query-reflections.py | HIGH |
| Output self-scoring | Add to: protocols/quality-check.md | HIGH |
| Event-driven state change | Create: scripts/state-watcher.py | MEDIUM |

### Short-Term (This Month)

| Improvement | File to Create/Edit | Priority |
|-------------|-------------------|----------|
| Memory extraction script | Create: scripts/memory-extract.py | MEDIUM |
| Self-challenging curriculum | Create: scripts/self-challenge.py | MEDIUM |
| Workload classification | Update: cron job metadata | LOW |

### Structural (Ongoing)

| Improvement | Approach |
|-------------|----------|
| Memory importance scoring | Add metadata to memory files |
| Adaptive scheduling | Enhance scheduling-advisor.py |
| Specialized sub-agents | Define role prompts |

---

## 6. Key Takeaways

### What the Research Says

1. **Memory is context engineering** — what's in context determines what the agent "knows"
2. **Self-improvement requires feedback loops** — generate → evaluate → reflect → improve
3. **Proactive agents should be event-driven** — not just time-based polling
4. **Reflection patterns dramatically improve output** — up to 91% on coding benchmarks

### What This Daemon Needs Most

1. **Automated memory extraction** — stop relying on manual MEMORY.md updates
2. **Mandatory self-scoring** — catch low-quality outputs before sending
3. **Event-driven triggers** — alert on state changes, not just schedules
4. **Self-challenging practice** — target weak areas intentionally

### The North Star

From Yohei Nakajima:
> "Agents shouldn't be static models with fixed prompts. They should practice, reflect, generate their own curricula, and rewrite parts of themselves."

The goal isn't a better cron scheduler — it's a system that **gets smarter over time** through its own operation.

---

## Sources

1. LangMem Conceptual Guide - langchain-ai.github.io/langmem
2. "Better Ways to Build Self-Improving AI Agents" - Yohei Nakajima (NeurIPS 2025 synthesis)
3. "Agent Memory" - Letta Blog
4. "Top AI Agentic Workflow Patterns" - ByteByteGo
5. "Agent.xpu: Efficient Scheduling of Agentic LLM Workloads" - ArXiv 2506.24045
6. "Reflexion" - PromptingGuide.ai
7. Reflexion Paper - Shinn et al., 2023

---

*Research complete. Implementing high-priority items now.*
