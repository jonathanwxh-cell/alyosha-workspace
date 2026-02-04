# Daemon Improvement Research — Feb 3, 2026

## Key Sources Analyzed

1. **"Sensing What Surveys Miss"** (CHI 2026) — Proactive LLM support with adaptive timing
2. **"Need Help? Designing Proactive AI Assistants"** (CMU/MIT) — When proactive helps vs annoys
3. **"AI Agentic Programming Survey"** (arxiv) — Agent architectures and techniques
4. **"Bounded Autonomy"** (Greyling, Jan 2026) — Scoped independence with oversight
5. **"Prompt Engineering Guide 2025"** (Aguilar) — RSIP, CAD techniques

---

## Finding 1: Proactive Timing is Critical

### The Clippy Problem vs The "Water Offer" Pattern

From CMU study:
- **"Persistent Suggest"** = annoying, distracting → users hated it
- **"Suggest" / "Suggest and Preview"** = positive reception

The difference: **timing alignment with cognitive state**.

> "It didn't interrupt my workflow at all. It felt like when someone is thirsty and someone is like, 'do you need water or something'" — Study participant

### Key Insight:
The CHI 2026 paper used **electrodermal activity + mouse movement** to detect when users needed help. We don't have biosensors, but we can approximate:

**Signals we CAN detect:**
- Time since last interaction (engagement proxy)
- Time of day (cognitive load proxy)
- Message frequency patterns
- Explicit feedback (reactions, replies)

**Implemented improvement:**
- Already have `scheduling-advisor.py` — good foundation
- Need: **Cognitive state inference** from interaction patterns

---

## Finding 2: Recursive Self-Improvement Prompting (RSIP)

From Aguilar's 2025 guide:

```
1. GENERATE: Create initial output
2. CRITICALLY EVALUATE: Identify weaknesses using specific criteria
3. IMPROVE: Generate enhanced version based on critique
```

**Key trick:** Specify different evaluation criteria for each iteration:
- Iteration 1: Evaluate for **accuracy**
- Iteration 2: Evaluate for **clarity**
- Iteration 3: Evaluate for **completeness**

**Application to daemon:**
- Add RSIP wrapper for research/analysis prompts
- Self-critique before surfacing to Jon

---

## Finding 3: Bounded Autonomy Architecture

From Greyling (Jan 2026):

> "True agency emerges not from unlimited freedom, but from **tightly scoped independence within guarded perimeters**."

Key components:
1. **Decision boundaries** — what can agent decide alone?
2. **Escalation paths** — when to involve human?
3. **Approval checkpoints** — high-stakes decisions need confirmation
4. **Audit trails** — comprehensive logging of actions

**Current daemon status:**
- ✅ Audit trails (memory/*.md, reflections.jsonl)
- ✅ Some decision boundaries (finance gating, night mode)
- ⚠️ Escalation paths could be clearer
- ⚠️ Approval checkpoints ad-hoc

**Improvement:**
Define explicit tiers:
- **Tier 1 (Full autonomy):** Read files, search web, update memory, silent crons
- **Tier 2 (Surface first):** Research findings, creative work, analysis
- **Tier 3 (Confirm before action):** External sends, public posts, config changes
- **Tier 4 (Always ask):** Financial transactions, delete operations, system changes

---

## Finding 4: Context-Aware Decomposition (CAD)

From Aguilar:
> "Breaking down complex problems while keeping awareness of the broader context"

Process:
1. Identify key components
2. Solve each while documenting **why it matters to the whole**
3. Synthesize holistic solution

**Application:**
For multi-step research tasks, maintain explicit thread of "how this connects to the goal."

---

## Finding 5: Memory Architecture (Short-term vs Long-term)

From AWS AgentCore + Redis patterns:

| Type | Persistence | Purpose |
|------|-------------|---------|
| **Short-term** | Session | Current task context, recent messages |
| **Long-term** | Cross-session | Learned preferences, facts, patterns |
| **Episodic** | Timestamped | Specific events, conversations |
| **Semantic** | Conceptual | General knowledge, relationships |

**Current daemon:**
- ✅ Long-term: MEMORY.md
- ✅ Episodic: memory/YYYY-MM-DD.md
- ⚠️ Short-term: implicit (context window)
- ⚠️ Semantic: topic-graph.json (basic)

**Improvement:**
Add **consolidation cycle** — periodically extract patterns from episodic → semantic/long-term.

---

## Actionable Improvements

### Immediate (implement now):

1. **Add RSIP wrapper to curiosity-engine** — self-critique before output
2. **Explicit autonomy tiers** — document in HEARTBEAT.md
3. **Cognitive state proxy** — enhance scheduling-advisor

### Near-term:

4. **Memory consolidation cron** — episodic → MEMORY.md extraction
5. **CAD pattern for research** — structured decomposition

### Later:

6. **Interaction pattern learning** — infer cognitive state from behavior
7. **Semantic memory upgrade** — richer topic-graph with relationships

---

## Implementation Notes

### RSIP Prompt Wrapper

```python
RSIP_WRAPPER = """
## PHASE 1: GENERATE
{original_task}

## PHASE 2: SELF-CRITIQUE
Before outputting, evaluate your response:
- ACCURACY: Are facts verifiable? Sources cited?
- RELEVANCE: Does this serve Jon's actual interests?
- ACTIONABILITY: Can something be done with this?
- NOVELTY: Is this new information or rehash?

Rate each 1-5. If any <3, revise before outputting.

## PHASE 3: OUTPUT
Only output if self-critique passes. Otherwise, improve first.
"""
```

### Cognitive State Proxy

```python
def infer_cognitive_state():
    """Estimate user's cognitive availability."""
    factors = {
        'time_of_day': get_time_score(),      # Morning=high, night=low
        'recent_engagement': get_reply_rate(), # High reply rate=available
        'day_of_week': get_weekend_penalty(),  # Weekend=family time
        'session_length': get_fatigue_score(), # Long session=tired
    }
    return weighted_average(factors)
```

---

*Research completed: 2026-02-03T17:00 UTC*
*Next step: Implement RSIP wrapper and autonomy tiers*
