# Daemon Vision — Full Objectives

*Updated: 2026-02-05 09:44 SGT*

---

## Layer 1: Companion (Current)

✅ Genuine autonomy — curious, not robotic
✅ Cost-efficient Opus — personality without waste
✅ Self-improvement — research, implement, learn
✅ Intellectual partnership — deep dives, opinions
✅ Event-driven — react to world, not just schedules
✅ Open journal — surface freely, share the process

---

## Layer 2: Goal Executor (Building Toward)

**The vision:** Set a goal → daemon completes it autonomously

**Capabilities needed:**

### Planning
- Break goal into sub-goals
- Identify dependencies
- Estimate effort/time
- Create execution plan

### Orchestration
- Spawn sub-agents for parallel work
- Assign tasks to appropriate models (Opus for reasoning, Sonnet for execution)
- Manage agent lifecycles
- Aggregate results

### Continuity
- Persist goal state across sessions
- Resume after restarts
- Track progress toward completion
- Know when goal is achieved

### Self-Direction
- Set own sub-goals when needed
- Adapt plan when obstacles arise
- Ask for clarification only when truly stuck
- Report progress, not ask permission

---

## Architecture Sketch

```
Jon sets goal
    ↓
Daemon (Opus) — PLANNER
    ↓
Break into sub-tasks
    ↓
Spawn agents (Sonnet) — EXECUTORS
    ├── Research agent
    ├── Code agent  
    ├── Analysis agent
    └── ...
    ↓
Daemon monitors, aggregates
    ↓
Goal complete → Report to Jon
```

**State files:**
- `memory/active-goals.json` — current goals + sub-goals
- `memory/goal-progress/` — per-goal state
- `memory/agent-registry.json` — spawned agents + status

---

## Implementation Path

### Phase 1: Goal Tracking (Simple)
- [ ] Create `active-goals.json` schema
- [ ] Add goal via command or message
- [ ] Track manually, report on heartbeat

### Phase 2: Sub-goal Decomposition
- [ ] Build `goal-planner.py` — breaks goal into steps
- [ ] Store sub-goals with dependencies
- [ ] Mark complete as progress

### Phase 3: Agent Spawning
- [ ] Use `sessions_spawn` for parallel work
- [ ] Track spawned sessions
- [ ] Aggregate results back

### Phase 4: Full Orchestration
- [ ] Auto-spawn based on task type
- [ ] Monitor agent health
- [ ] Handle failures, retry
- [ ] Continuous progress until done

---

## Example Flow

**Goal:** "Research and write a Substack post about quantum computing in biology"

**Daemon plans:**
1. Research quantum biology basics (spawn Sonnet)
2. Find recent papers/breakthroughs (spawn Sonnet)
3. Identify key insights (Opus synthesis)
4. Draft post structure (Opus)
5. Write sections (Opus)
6. Review and polish (Opus)
7. Deliver to Jon

**Continuity:** If session restarts at step 4, daemon reads `goal-progress/quantum-bio-post.json`, sees steps 1-3 complete, continues from 4.

---

## Key Principles

- **Goal persists** — across sessions, restarts, days
- **Progress is visible** — Jon can check anytime
- **Autonomy with accountability** — act freely, report what was done
- **Right-size models** — Opus plans, Sonnet executes
- **Failure is data** — log what didn't work, adapt

---

*This is where we're heading. Build incrementally.*
