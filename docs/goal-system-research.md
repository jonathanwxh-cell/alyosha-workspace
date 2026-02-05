# Goal System Research

*Researched: 2026-02-05 09:45 SGT*

---

## Key Findings

### Two Orchestration Patterns (OpenAI Agents SDK)

**1. LLM-Driven (Flexible)**
- Agent plans and decides autonomously
- Uses tools + handoffs to sub-agents
- Good for open-ended tasks
- Risk: Unpredictable, can spiral

**2. Code-Driven (Deterministic)**
- Flow controlled by code
- Structured outputs → next step
- Chaining agents (output → input)
- Good for predictable workflows

**Best approach: Hybrid** — Code controls flow, LLM handles reasoning within steps.

---

### Goal Decomposition (HTN Pattern)

From Kore.ai and academic research:

```
Goal (High-level)
  ↓
Sub-goals (Decomposed by LLM)
  ↓
Tasks (Atomic, assignable)
  ↓
Actions (Tool calls)
```

**Key principles:**
- Analyze goal structure + dependencies
- Create task hierarchies
- Identify constraints that affect scheduling
- Track state across steps

---

### Lessons from AutoGPT/BabyAGI

**What worked:**
- Task queue with prioritization
- Persistent memory across steps
- Specialized agents per task type

**What failed:**
- Expensive API spirals (no step limits)
- Over-complex vector DB memory (unnecessary)
- General-purpose agents (too unfocused)

**Fixes in 2025 versions:**
- Step limits
- Human-in-the-loop checkpoints
- Cost tracking per goal

---

### Best Practices (Synthesis)

1. **Specialized agents** > general purpose
2. **Good prompts** matter more than complex architecture
3. **Let agent self-critique** in loops
4. **Chain outputs** between steps
5. **Persist state** for continuity
6. **Step limits** to prevent spirals
7. **Evals** to improve over time

---

## Implementation Design

### State Files
- `memory/active-goals.json` — goal registry
- `memory/goal-progress/<id>.json` — per-goal events

### Goal Schema
```json
{
  "id": "abc123",
  "description": "Write Substack post",
  "status": "active|complete|paused",
  "sub_goals": [
    {"id": "x1", "description": "Research", "status": "complete"},
    {"id": "x2", "description": "Draft", "status": "in_progress"}
  ],
  "progress_pct": 50,
  "created": "2026-02-05 09:45 SGT"
}
```

### Flow
1. Jon sets goal → added to registry
2. Daemon decomposes into sub-goals (LLM)
3. Sub-goals assigned to agents (Sonnet via spawn)
4. Progress tracked, state persisted
5. On restart, daemon reads state, continues
6. Goal complete → report to Jon

---

## Next Steps

- [x] Build `goal-tracker.py` — basic CRUD
- [ ] Add decomposition prompt (LLM breaks goal into sub-goals)
- [ ] Integrate with `sessions_spawn` for parallel execution
- [ ] Add heartbeat check for goal progress
- [ ] Build evaluation loop (is sub-goal done well?)

---

*Tool: `scripts/goal-tracker.py`*
