# Daemon Improvement Research: Autonomous Agent Patterns
*Research conducted: 2026-02-04*

## Executive Summary

Surveyed latest research on autonomous agents, prompt engineering, and scheduling patterns. Key findings organized into **immediately implementable** vs **architectural considerations**.

---

## 1. Ambient Agent Design (LangChain, Snowplow)

### Core Insight
The industry is converging on "ambient agents" - agents that respond to **event streams** rather than chat messages, and demand user input only when they detect important opportunities.

### Seven Principles (Snowplow Manifesto)
1. **Goal-oriented** - Clear primary objective drives behavior
2. **Autonomous operation** - Act independently without human prompting
3. **Continuous perception** - Monitor environment constantly
4. **Semantic reasoning** - Understand context to make decisions
5. **Persistence across interactions** - Remember prior experiences
6. **Multi-agent collaboration** - Specialized agents working together
7. **Asynchronous communication** - Event streams, not synchronous calls

### Human-in-the-Loop Patterns (LangChain)
| Pattern | When to Use | Example |
|---------|-------------|---------|
| **Notify** | Flag important events, don't act | "Important email from X" |
| **Question** | Blocked, need info to proceed | "Do you want to attend this?" |
| **Review** | Dangerous action, needs approval | "Draft email - approve?" |

**Current Status:** We have review (Tier 3/4), but underuse notify/question patterns.

### 💡 Improvement: Agent Inbox Concept
LangChain's "Agent Inbox" - a queue of pending agent communications, sorted by priority. Could implement:
```json
// memory/agent-inbox.json
{
  "pending": [
    {"type": "notify", "priority": "high", "topic": "...", "created": "..."},
    {"type": "question", "priority": "medium", "question": "...", "options": [...]}
  ]
}
```
Surface batched at optimal times rather than interrupting immediately.

---

## 2. Reflexion Framework (Shinn et al.)

### Core Architecture
```
Actor → Trajectory → Evaluator → Score
                          ↓
                   Self-Reflection
                          ↓
                 Memory (stored reflections)
                          ↓
                    Next Trajectory
```

### Key Components
- **Actor**: Generates actions (we have this)
- **Evaluator**: Scores outputs - LLM or rule-based (we have partial)
- **Self-Reflection**: Generates verbal cues for improvement (we have `reflections.jsonl`)
- **Memory**: Stores reflections for future trials (we have this)

**Current Status:** We have the pieces but not the automated loop.

### 💡 Improvement: Formalize Evaluation
After significant actions, explicitly evaluate:
```
EVALUATE:
- Goal achieved? [YES/PARTIAL/NO]
- Unexpected outcomes?
- What would improve next attempt?
```

Add to `scripts/reflexion.py`:
```python
def auto_evaluate(task, outcome, trajectory):
    """LLM-as-judge evaluation of task completion"""
    # Score: 0-1
    # Diagnosis: What went wrong/right
    # Lesson: One-sentence takeaway
```

---

## 3. Self-Evolving Agents (OpenAI Cookbook)

### GEPA: Genetic-Pareto Prompt Evolution
State-of-the-art technique for autonomous prompt improvement:

1. **Sample trajectories** - Run prompts, collect outcomes
2. **Reflect in natural language** - Analyze what worked/failed
3. **Propose revisions** - Generate prompt mutations
4. **Pareto selection** - Keep prompts that improve metrics without regressing others
5. **Iterate** - Evolution across generations

**Key insight:** "Prompt optimization as a language process" - treat each candidate prompt as an "idea" that can be improved through reflection.

### 💡 Improvement: Prompt Evolution for Crons
For underperforming crons:
1. Collect recent outputs + feedback
2. Reflect: "What patterns caused low engagement?"
3. Generate 3 variant prompts
4. A/B test variants (track separately)
5. Promote winner

Could implement lightweight version:
```bash
python3 scripts/prompt-evolver.py --cron "research-scan" --feedback-window 7d
```

---

## 4. Memory Management (MemGPT/Letta)

### Memory Blocks Concept
Break context into discrete, purposeful units:

| Block | Purpose | Size Limit |
|-------|---------|------------|
| **Human** | User info, preferences, context | 2000 chars |
| **Persona** | Agent identity, personality | 1000 chars |
| **Task** | Current task state | 1500 chars |
| **Knowledge** | Domain facts, learned info | 3000 chars |

**Key insight:** Blocks are **self-editable** by the agent. Agent can update its own context.

### Sleep-Time Compute
Background agents process during idle periods:
- Reflect on conversations
- Form new memories ("learned context")
- Update shared memory blocks

**Current Status:** We do this (heartbeat background work), but not structured as "sleep-time compute."

### 💡 Improvement: Formalize Memory Blocks
Structure `memory/` more explicitly:
```
memory/
  blocks/
    human.md      # Jon context (size-limited, self-editable)
    persona.md    # My identity (links to SOUL.md)
    task-state.md # Current focus (auto-updated)
    knowledge.md  # Learned facts (curated)
```

Add size constraints and auto-pruning.

---

## 5. Metacognitive Patterns

### Plan → Monitor → Evaluate Cycle
From Metagent-P research:

```
PLAN: Set goals, identify steps
  ↓
MONITOR: Track execution, detect deviations
  ↓
EVALUATE: Assess outcomes, update experience
  ↓
ADAPT: Modify plans based on evaluation
  ↓
(loop)
```

### Self-Awareness Mechanisms
- **Confidence estimation**: Before acting, estimate success probability
- **Failure prediction**: Detect when likely to fail, hand off to human
- **Resource monitoring**: Track token usage, time, cost

**Current Status:** We have session_status, context usage awareness. Could formalize confidence.

### 💡 Improvement: Confidence-Gated Actions
Before significant actions:
```
CONFIDENCE: [0-10] + reasoning
If confidence < 5: surface to Jon before proceeding
If confidence < 3: explicitly ask
```

---

## 6. Scheduling Intelligence

### Pattern: Adaptive Intervals
From enterprise agent research:
- Track engagement rate over time
- Adjust surface frequency based on response patterns
- Backoff on silence, accelerate on engagement

**Current Status:** We have `scheduling-advisor.py` - good foundation.

### Pattern: Content-Time Matching
Different content types perform better at different times:
- Morning: Actionable, quick wins
- Midday: Substantial analysis
- Evening: Reflective, creative
- Weekend: Light, family-friendly

**Current Status:** We have this in `scheduling-intelligence.json` - underutilized.

### 💡 Improvement: Automatic Time-Slot Learning
```bash
python3 scripts/analyze-engagement.py --auto-update
```
Run weekly, automatically update time slot scores based on actual engagement data.

---

## 7. Event-Driven Architecture

### Shift from Polling to Events
Current: Heartbeat polls every N minutes, checks everything
Better: Event-driven triggers

| Event | Trigger | Action |
|-------|---------|--------|
| Email arrived | Webhook/poll | Classify, maybe surface |
| Market moved >3% | Price alert | Surface if watchlist |
| File changed | Filesystem watch | Process if relevant |
| Time trigger | Cron | Scheduled action |

**Current Status:** We're mostly polling-based. Could add more event triggers.

### 💡 Improvement: Delta Detection Enhancement
Expand `scripts/delta-detector.py`:
- Track more signals (git changes, file modifications)
- Calculate significance scores
- Only surface on HIGH significance

---

## Implementation Priority

### Phase 1: Quick Wins (This Week)
1. **Formalize confidence scoring** - Add to HEARTBEAT.md decision logic
2. **Memory blocks structure** - Create `memory/blocks/` with size limits
3. **Notify/Question patterns** - Document when to use each in HEARTBEAT.md

### Phase 2: Tooling (Next 2 Weeks)
4. **Auto-evaluate script** - `scripts/reflexion.py auto-evaluate`
5. **Prompt evolution MVP** - For 1-2 underperforming crons
6. **Engagement auto-update** - Weekly cron for time-slot learning

### Phase 3: Architecture (Month+)
7. **Agent inbox** - Queue-based communication
8. **Event-driven triggers** - Beyond pure polling
9. **Multi-block memory** - Full MemGPT-style implementation

---

## Sources
- LangChain: [Introducing Ambient Agents](https://blog.langchain.com/introducing-ambient-agents/)
- Snowplow: [Seven Principles of Ambient Agents](https://snowplow.io/blog/seven-principles-of-ambient-agents)
- OpenAI Cookbook: [Self-Evolving Agents](https://cookbook.openai.com/examples/partners/self_evolving_agents/)
- Prompting Guide: [Reflexion](https://www.promptingguide.ai/techniques/reflexion)
- Letta: [Memory Blocks](https://www.letta.com/blog/memory-blocks)
- GEPA Paper: Genetic-Pareto prompt evolution
- Metagent-P: Metacognitive planning agents

---

*Next: Implement Phase 1 improvements*
