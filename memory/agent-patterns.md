# Agent Patterns Reference

*Researched 2026-02-05. Patterns that improve autonomous exploration.*

## Implemented

### Reflexion (Shinn et al., 2023)
**Core Loop:** Generate → Critique → Improve → Store

**How I use it:**
1. **RECALL** — Query `scripts/reflexion.py query <topic>` before similar tasks
2. **HYPOTHESIZE** — State belief before searching
3. **ACT** — Do the research/task
4. **REFLECT** — What worked? What failed?
5. **STORE** — Log to `memory/reflections.jsonl`

**Key insight:** Learning through verbal feedback stored in memory, not weight updates. The lesson history IS the learning.

**Script:** `scripts/reflexion.py`
- `add` — Log new reflection
- `query <topic>` — Find relevant past reflections
- `mars` — MARS self-assessment
- `stats` — Reflection statistics

### ReAct (Yao et al., 2022)
**Core Loop:** Thought → Action → Observation

**How I use it:**
- Already embedded in tool-using behavior
- Explicit reasoning before tool calls
- Observation informs next thought

**Key insight:** Reasoning traces help maintain coherent action plans. Don't just act — think, then act, then observe.

## To Explore

### Tree of Thoughts (ToT)
**Core Loop:** Generate multiple paths → Self-evaluate → Backtrack if needed

**Best for:** Complex problems where first answer might be wrong.

**Potential use:** Multi-step analysis where I should consider alternative interpretations before committing.

**Not yet implemented** — would require explicit branching in prompts.

### LATS (Language Agent Tree Search)
**Core:** ToT + Monte Carlo Tree Search + reflection

**Key insight:** Combines exploration (trying new paths) with exploitation (using what worked).

**Status:** Too complex for current needs. Revisit for harder problems.

## Anti-patterns

1. **Acting without recalling** — Don't repeat past mistakes. Query reflections first.
2. **Hypothesis-free search** — State belief before searching. Prevents confirmation bias drift.
3. **Reflection without structure** — Use consistent fields: hypothesis, outcome, worked, failed, lesson, confidence.
4. **Never applying lessons** — Track which lessons are applied. High-confidence lessons should change behavior.

---
*Update when implementing new patterns or learning new insights.*
