# Daemon Improvement Research - 2026-02-04

## Key Findings

### 1. Seven Principles of Ambient Agents (Snowplow)
From industry consensus on what makes agents "ambient" vs reactive:

1. **Goal-oriented** — Clear primary objective driving behavior
2. **Autonomous operation** — Act independently without human prompting
3. **Continuous perception** — Monitor environment in real-time
4. **Semantic reasoning** — Understand context deeply, not just pattern match
5. **Persistence across interactions** — Remember prior experiences for long-term goals
6. **Multi-agent collaboration** — Specialized agents working together
7. **Asynchronous communication** — Event streams, loose coupling

**Gap in our daemon:** We have 1-5 partially. Missing: true multi-agent collaboration (sub-agents exist but don't collaborate), event-driven architecture (we poll, not subscribe).

### 2. MARS Framework (NTU Singapore, Jan 2026)
Metacognitive Agent Reflective Self-improvement — key insight:

**Two types of learning (from education psychology):**
- **Principle-based:** Abstract rules to AVOID errors ("don't do X because Y")
- **Procedural:** Step-by-step strategies for SUCCESS replication ("do A then B then C")

**Current gap:** Our `reflections.jsonl` captures lessons but doesn't separate these two types. We should split reflections into:
- "What to avoid" (principle-based)
- "What works" (procedural)

**Key innovation:** Single-cycle improvement is more efficient than multi-turn recursion. We can apply this.

### 3. Self-Evolving Agents (OpenAI Cookbook)
Pattern for autonomous prompt improvement:

```
Loop:
1. Run baseline agent
2. Evaluate outputs (human or LLM-as-judge)
3. Aggregate scores
4. If score < threshold: generate improved prompt
5. Replace baseline with improved version
6. Repeat until score > threshold OR max_retries
```

**Applicable to us:** We have `prompt-evolver.py` but it's basic. Could add:
- Aggregated scoring from feedback-log.jsonl
- Threshold-based automatic prompt updates
- Meta-prompt for prompt improvement

### 4. Judge Agent Pattern (Temporal)
From crypto trading agent architecture:

- **Execution Agent:** Does the work
- **Judge Agent:** Evaluates performance, updates execution agent's system prompt

This is exactly what we need for self-improvement. The daemon should have a "judge" process that:
1. Reviews recent outputs
2. Scores them
3. Updates HEARTBEAT.md or cron prompts based on what worked

### 5. MemGPT Patterns
- **Heartbeats for multi-step reasoning** — Already implemented!
- **Memory hierarchy** — We have this in `memory/blocks/`
- **Request_heartbeat pattern** — Agent can request another turn

## Concrete Improvements to Implement

### A. Split Reflection Types
Update `scripts/reflexion.py` to categorize:
- `type: "avoid"` — Principle-based (what NOT to do)
- `type: "procedure"` — Procedural (what TO do)

### B. Add Judge Pattern
New cron: "Daemon Judge" that:
1. Reviews last 24h of feedback-log.jsonl
2. Scores daemon outputs
3. Identifies what's working vs not
4. Proposes prompt improvements

### C. Event-Driven Triggers
Instead of pure time-based crons, add delta detection:
- Market moves > X% → trigger analysis
- New email from important sender → trigger review
- Already have `scripts/delta-detector.py`, expand it

### D. Meta-Cognitive Checkpoint
Before major outputs, add self-check:
```
THOUGHT: What am I trying to do?
PRINCIPLE CHECK: Am I avoiding known failure modes?
PROCEDURE CHECK: Am I following what's worked before?
CONFIDENCE: [1-10]
```

### E. Aggregate Scoring Dashboard
Track daemon health metrics:
- Engagement rate (replies/reactions per surface)
- Topic balance adherence
- Autonomy score (corrections per day)
- Quality score (from feedback-log)

## Implementation Priority

1. **HIGH:** Split reflection types (simple, high value)
2. **HIGH:** Judge pattern cron (self-improvement automation)
3. **MEDIUM:** Meta-cognitive checkpoint in HEARTBEAT.md
4. **LOW:** Event-driven expansion (already have basics)
5. **LOW:** Scoring dashboard (nice to have)

## Sources
- Snowplow: https://snowplow.io/blog/seven-principles-of-ambient-agents
- MARS: https://arxiv.org/html/2601.11974v1
- OpenAI Cookbook: Self-Evolving Agents
- Temporal: Orchestrating Ambient Agents
- PromptingGuide: Reflexion framework
