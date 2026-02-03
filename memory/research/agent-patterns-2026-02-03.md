# Agent Patterns Research — 2026-02-03

## Key Patterns Surveyed

### 1. ReAct (Reasoning + Acting)
**Source:** Yao et al. 2022
**Core idea:** Alternate between reasoning traces and actions
```
THOUGHT → ACTION → OBSERVATION → THOUGHT → ...
```
**Best for:** Tool-using tasks, research, exploration
**Already implemented:** Partially in HEARTBEAT.md

### 2. Reflexion (Verbal Reinforcement Learning)
**Source:** Shinn et al. 2023, NeurIPS
**Core idea:** Self-reflect on task outcomes, store lessons in episodic memory
**Components:**
- Actor: Generates actions (ReAct)
- Evaluator: Scores outcomes
- Self-Reflection: Generates verbal feedback
- Memory: Stores reflections for future trials

**Key insight:** "Reflexion agents verbally reflect on task feedback signals, then maintain their own reflective text in an episodic memory buffer to induce better decision-making in subsequent trials."

**Results:** 90%+ success on AlfWorld, significant gains on HotPotQA reasoning

**Implemented:** `scripts/reflexion.py`

### 3. LATS (Language Agent Tree Search)
**Source:** Zhou et al. 2023
**Core idea:** Combine reasoning, acting, planning with tree search
- Explores multiple action paths
- Uses self-reflection for node scoring
- Backpropagates values like MCTS

**Best for:** Complex multi-step planning
**Status:** Not implemented (overkill for current use cases)

### 4. Tree of Thought (ToT)
**Core idea:** Explore multiple reasoning paths, evaluate and select
**Best for:** Branching decisions, creative exploration
**Status:** Can be applied manually for complex choices

## Implementation: Reflexion System

Created `scripts/reflexion.py` with:
- `query <topic>` — Find relevant past reflections before tasks
- `add` — Log new reflection after task
- `stats` — View success rates and categories
- `lessons` — Extract top lessons by category

**Integration points:**
1. HEARTBEAT.md — Reflexion Protocol section
2. Daily Free Exploration cron — 5-step Reflexion loop
3. Weekly Self-Review — stats + lessons extraction

## Hybrid Approach (Recommended)

| Pattern | When to Use |
|---------|-------------|
| **ReAct** | Research, tool use, exploration |
| **Reflexion** | After any significant task, before similar tasks |
| **ToT** | Complex decisions with multiple valid paths |
| **LATS** | Only if systematic search needed (rare) |

## Key Lessons from Research

1. **Query before acting** — Always check past reflections before starting similar tasks
2. **Explicit self-evaluation** — Ask "Did I achieve the goal? What would I do differently?"
3. **One-sentence lessons** — Force crystallization of insight
4. **Anti-patterns as guardrails** — Store what NOT to do, not just what works

## References

- [Reflexion Paper](https://arxiv.org/abs/2303.11366)
- [LATS Paper](https://arxiv.org/abs/2310.04406)
- [Agent Architectures Survey](https://arxiv.org/html/2404.11584v1)
- [Prompt Engineering Guide - Reflexion](https://www.promptingguide.ai/techniques/reflexion)
