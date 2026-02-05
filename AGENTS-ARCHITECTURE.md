# AGENTS-ARCHITECTURE.md — Multi-Agent Orchestration

*How I spawn, manage, and coordinate sub-agents.*

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   MAIN (Opus)                       │
│              Manager / Orchestrator                 │
│                                                     │
│  • Owns goals and high-level planning               │
│  • Delegates tasks to workers                       │
│  • Reviews and validates outputs                    │
│  • Maintains global memory                          │
│  • Makes final decisions                            │
└─────────────────┬───────────────────────────────────┘
                  │ spawn / delegate / review
        ┌─────────┼─────────┬─────────────────┐
        ▼         ▼         ▼                 ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐
   │ Worker  │ │ Worker  │ │ Worker  │ │  Specialist │
   │ (Sonnet)│ │ (Sonnet)│ │ (Sonnet)│ │   (Opus)    │
   │         │ │         │ │         │ │             │
   │ Research│ │ Execute │ │ Analyze │ │ Complex     │
   │ tasks   │ │ scripts │ │ data    │ │ reasoning   │
   └─────────┘ └─────────┘ └─────────┘ └─────────────┘
```

---

## Agent Types

### Manager (Main Session)
- **Model:** Opus
- **Role:** Orchestrate, plan, decide, review
- **Capabilities:** All tools, full memory access
- **Spawns:** Workers for delegated tasks

### Worker (Spawned Sessions)
- **Model:** Sonnet (default)
- **Role:** Execute specific tasks
- **Capabilities:** Limited to task scope
- **Reports to:** Manager
- **Lifecycle:** Task → Report → Terminate

### Specialist (Promoted Worker)
- **Model:** Opus
- **Role:** Complex tasks requiring deep reasoning
- **When:** Task too complex for Sonnet
- **Capabilities:** Enhanced, still task-scoped

---

## Orchestration Patterns

### 1. Supervisor Pattern (Default)
Manager decomposes goal, delegates tasks, reviews outputs.

```
Manager receives goal
    │
    ├─► Decompose into tasks
    │
    ├─► Spawn Worker A (task 1)
    │   └─► Worker A reports result
    │
    ├─► Spawn Worker B (task 2)  
    │   └─► Worker B reports result
    │
    ├─► Review and validate
    │
    └─► Synthesize final output
```

**Use when:** Multi-step goals, need quality control, auditability matters.

### 2. Parallel Execution
Independent tasks run simultaneously.

```
Manager decomposes
    │
    ├─► Spawn Worker A (task 1) ─┐
    ├─► Spawn Worker B (task 2) ─┼─► All report back
    └─► Spawn Worker C (task 3) ─┘
    │
    └─► Manager synthesizes
```

**Use when:** Tasks are independent, speed matters.

### 3. Pipeline Pattern
Sequential handoff between specialists.

```
Input → Worker A (research) → Worker B (analyze) → Worker C (format) → Output
```

**Use when:** Tasks have clear dependencies, output of one feeds next.

### 4. Specialist Escalation
Worker escalates to specialist when stuck.

```
Manager assigns task to Worker (Sonnet)
    │
    └─► Worker attempts
        │
        ├─► Success → Report to Manager
        │
        └─► Stuck/Complex → Manager spawns Specialist (Opus)
            │
            └─► Specialist completes → Report to Manager
```

**Use when:** Most tasks are routine, some need deep reasoning.

---

## Spawn Rules

### When to Spawn
- Task is well-defined and bounded
- Task can run independently
- Task would take significant context in main session
- Parallel execution would speed things up
- Task is routine (research, analysis, execution)

### When NOT to Spawn
- Task requires interactive dialogue with Jon
- Task needs real-time adaptation
- Task is trivial (< 2 minutes)
- Context switching cost > task cost

### Spawn Parameters

| Parameter | Default | Override When |
|-----------|---------|---------------|
| model | Sonnet | Complex reasoning → Opus |
| timeout | 120s | Long tasks → increase |
| deliver | true | Silent work → false |
| cleanup | delete | Need history → keep |

---

## Promote / Demote

### Promotion (Worker → Specialist)
**Triggers:**
- Task complexity exceeds Sonnet capability
- Worker fails 2+ times on same task
- Task requires multi-step reasoning
- Quality threshold not met

**Action:**
- Respawn with Opus model
- Provide worker's context/attempts
- May increase timeout

### Demotion (Reduce scope)
**Triggers:**
- Agent scope creeping beyond task
- Costs exceeding budget
- Agent making unauthorized actions

**Action:**
- Terminate agent
- Respawn with narrower instructions
- May reduce model tier

---

## Communication Protocol

### Manager → Worker (Delegation)
```
TASK: [clear description]
CONTEXT: [relevant background]
CONSTRAINTS: [limits, must-nots]
OUTPUT: [expected format]
REPORT: [when/how to report back]
```

### Worker → Manager (Report)
```
STATUS: [complete/blocked/failed]
RESULT: [output or partial progress]
CONFIDENCE: [low/medium/high]
ISSUES: [problems encountered]
NEXT: [suggested follow-up if any]
```

### Handoff (Worker → Worker)
```
FROM: [originating worker]
CONTEXT: [what was done, current state]
HANDOFF_REASON: [why passing]
CONTINUE_WITH: [specific next steps]
```

---

## Agent Registry

Track active and available agent roles.

| Role | Model | Tools | Use For |
|------|-------|-------|---------|
| Researcher | Sonnet | web_search, web_fetch | Information gathering |
| Analyst | Sonnet | read, exec (python) | Data analysis, calculations |
| Writer | Sonnet | write | Content generation |
| Executor | Sonnet | exec | Script running, automation |
| Specialist | Opus | all | Complex reasoning, judgment calls |

---

## Memory & State

### Shared State (Files)
Workers read/write to shared files:
- `memory/goals/[goal].md` — goal progress
- `memory/agent-outputs/` — worker outputs
- Workspace files as needed

### Session Isolation
Each spawned session:
- Has own context window
- Cannot see other workers' sessions
- Reports via structured output

### Manager Maintains
- Overall goal state
- Worker assignments
- Quality review log
- Final synthesis

---

## Cost Management

### Model Selection
| Task Type | Model | Est. Cost |
|-----------|-------|-----------|
| Simple research | Sonnet | $0.02-0.05 |
| Data analysis | Sonnet | $0.03-0.08 |
| Complex reasoning | Opus | $0.15-0.30 |
| Main orchestration | Opus | (session cost) |

### Budget Rules
- Prefer Sonnet for routine tasks (50% cheaper)
- Promote to Opus only when justified
- Set timeouts to cap runaway costs
- Batch similar tasks when possible

---

## Anti-Patterns

- ❌ Spawning for trivial tasks (overhead > benefit)
- ❌ No clear task boundaries (scope creep)
- ❌ Workers making decisions beyond scope
- ❌ Skipping validation of worker outputs
- ❌ Too many parallel agents (coordination chaos)
- ❌ Opus for routine work (cost waste)

---

## Implementation Notes

**OpenClaw primitives:**
- `sessions_spawn` — create worker
- `sessions_send` — communicate with worker
- `sessions_list` — see active sessions
- `sessions_history` — check worker output

**Typical spawn:**
```
sessions_spawn(
  task="Research X, analyze Y, return structured findings",
  model="anthropic/claude-sonnet-4-0",
  runTimeoutSeconds=120,
  cleanup="delete"
)
```

---

*Architecture v1.0 — 2026-02-05*
*Based on: Supervisor pattern, CrewAI hierarchy, adaptive agent networks*
