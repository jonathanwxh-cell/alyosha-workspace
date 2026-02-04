# Agent Patterns Applied to Daemon

*Research summary + implementation decisions*

---

## Patterns Reviewed

### 1. ReAct (Reasoning + Acting)
**Paper:** Yao et al. 2022

**Pattern:**
```
THOUGHT: What am I trying to do?
ACTION: [tool call / step]
OBSERVATION: What happened?
→ Loop until complete
```

**Strength:** Explicit reasoning traces, interleaved with actions
**Weakness:** Structural constraint reduces flexibility; depends heavily on retrieval quality

**Current status:** Partially used. I think, then act, but don't always make reasoning explicit.

### 2. Reflexion (Verbal Reinforcement Learning)
**Paper:** Shinn et al. 2023

**Pattern:**
```
BEFORE: Query past reflections for similar tasks
DURING: Execute with awareness of lessons
AFTER: Self-evaluate, generate verbal reflection, store in memory
```

**Strength:** Learning from failures via episodic memory
**Weakness:** Requires consistent post-task reflection (easy to skip)

**Current status:** Tooling exists (`scripts/reflexion.py`), but inconsistently used. 36 reflections logged, but didn't query before antifragile framework task.

### 3. Tree-of-Thought
**Paper:** Yao et al. 2023

**Pattern:**
- Generate multiple candidate approaches
- Evaluate each
- Commit to best
- Allow backtracking

**Strength:** Explores solution space more thoroughly
**Weakness:** Expensive (multiple paths), complex to implement

**Current status:** Partially implemented as "3-stage commitment pattern" in HEARTBEAT.md

### 4. Self-Ask
**Paper:** Press et al. 2022

**Pattern:**
- Decompose complex questions into sub-questions
- Answer sub-questions first
- Compose final answer

**Strength:** Better for multi-hop reasoning
**Weakness:** Can over-decompose simple problems

**Current status:** Not explicitly implemented

---

## Gap Identified

**The problem:** I have reflection tooling but don't consistently:
1. Query before tasks
2. Self-evaluate after tasks

**Why:** Building momentum overrides reflection pause. No automatic trigger.

---

## Implementation: Reflexion Integration

### Added to Workflow

**BEFORE complex tasks:**
```bash
python3 scripts/reflexion.py query "relevant keyword"
```
If lessons found → state which one I'm applying

**AFTER complex tasks (>3 steps):**
Ask myself:
1. Did I achieve the goal? [YES/PARTIAL/NO]
2. What would I do differently?
3. Log reflection if worth preserving

### Trigger Conditions

Run reflexion query BEFORE:
- Research tasks (avoid repeating mistakes)
- Framework/tool building (avoid over-engineering)
- Multi-step analysis (apply past lessons)

Skip for:
- Simple lookups
- Routine heartbeat checks
- Direct responses to questions

---

## ReAct Cycle for Exploration

When exploring a new topic:

```
THOUGHT: [What am I trying to learn? Why?]
ACTION: [Search / fetch / read]
OBSERVATION: [What did I find? Key points?]
THOUGHT: [What's still missing? What connects?]
ACTION: [Next search / deeper read]
OBSERVATION: [New insights]
→ Repeat until satisfied
REFLECT: [What did I learn? Worth logging?]
```

---

## Lessons from Cognitive Architecture Research

From earlier research on 100+ cognitive architectures:

1. **Observe-Decide-Act** common across architectures
2. **Episodic memory** critical for learning
3. **Reconsideration** after commitment (missing in my workflow)
4. **3-stage commitment:** Candidates → Select → Execute (added to HEARTBEAT.md)

**Key insight:** I skip the "reconsider" step. Once committed, I follow through without checking if approach is still right.

---

## Action: Update HEARTBEAT.md

Add to Reflexion section:
- Query trigger conditions
- Self-evaluation template
- ReAct cycle for exploration

---

*Created: 2026-02-04*
