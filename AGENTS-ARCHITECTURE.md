# AGENTS-ARCHITECTURE.md — Multi-Agent Orchestration v1.1

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

## Structured Handoff Protocol

**Treat handoffs as versioned APIs, not free-form prose.**

### Handoff Payload Schema
```json
{
  "schemaVersion": "1.0.0",
  "traceId": "uuid-for-entire-goal",
  "taskId": "specific-task-identifier",
  "from": "worker-role",
  "to": "next-worker-role",
  "status": "complete|partial|failed",
  "summary": "What was accomplished",
  "output": {
    "data": {},
    "format": "json|markdown|file"
  },
  "citations": [
    {"title": "", "url": "", "accessed": "ISO-date"}
  ],
  "toolState": {
    "lastQuery": "",
    "resultsCount": 0
  },
  "confidence": "LOW|MEDIUM|HIGH",
  "openQuestions": [],
  "nextRequired": ["field1", "field2"],
  "error": null
}
```

### Validation Rules
- Validate payload against schema before accepting
- On validation failure: retry with error feedback (max 2 attempts)
- On persistent failure: escalate to manager
- Log all handoffs with trace_id for debugging

---

## Failure Recovery

### Failure Types
| Type | Detection | Response |
|------|-----------|----------|
| Timeout | No response in timeout window | Retry with extended timeout |
| Error | Explicit error in output | Analyze, adjust, retry |
| Stuck | Worker loops without progress | Terminate, escalate to specialist |
| Low Confidence | Worker reports LOW confidence | Manager reviews, may promote |
| Scope Creep | Worker acting outside boundaries | Terminate, respawn narrower |

### Retry Protocol
```
Attempt 1: Original task
    ↓ failure
Attempt 2: Task + error feedback + "try different approach"
    ↓ failure
Attempt 3: Promote to Opus OR escalate to manager
    ↓ failure
STOP: Log failure, surface to Jon
```

### Circuit Breaker (for repeated spawns)
If same task type fails 3+ times in a session:
- **Open circuit**: Stop spawning for that task type
- **Log pattern**: Record failure mode
- **Escalate**: Surface to manager/Jon
- **Reset**: After manual review or context change

### Isolation on Failure
When a worker fails:
- Capture partial output (if any)
- Save tool state for recovery
- Don't let failure cascade to parallel workers
- Manager decides: retry, reassign, or abort

---

## Quality Assurance Loop

### Producer → Reviewer → Publisher Pattern

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Producer │ ──► │ Reviewer │ ──► │ Publisher│
│ (Worker) │     │ (Worker) │     │ (Manager)│
└──────────┘     └──────────┘     └──────────┘
                      │
                      ▼ feedback
                ┌──────────┐
                │ Producer │ (revision)
                └──────────┘
```

**When to use QA loop:**
- High-stakes outputs (external sends, financial decisions)
- Complex analysis requiring verification
- Content that will be shown to Jon

**Reviewer responsibilities:**
- Check against success criteria
- Verify sources/citations
- Flag inconsistencies
- Provide specific feedback if rejecting

**Skip QA loop when:**
- Internal/draft work
- Simple data retrieval
- Time-critical tasks where speed > perfection

---

## Observability & Tracing

### Trace ID
Every goal gets a unique `traceId` that propagates through:
- All spawned workers
- All handoffs
- All file outputs
- All checkpoints

Format: `goal-{slug}-{timestamp}-{random4}`
Example: `goal-trading-setup-20260205-a3f2`

### Logging Requirements
Each agent interaction logs:
```
[traceId] [timestamp] [agent] [action] [outcome] [cost]
```

### SLOs (Service Level Objectives)
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Worker success rate | >90% | <80% |
| Handoff validation rate | >95% | <90% |
| Avg task completion | <60s | >120s |
| Retry rate | <20% | >30% |

### Cost Tracking
Track per-goal:
- Total tokens (input + output)
- Number of spawns
- Model breakdown (Opus vs Sonnet)
- Compare to estimate

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

### Memory Types

**Short-term (Task Context)**
- Current task state
- Recent tool outputs
- Conversation within task
- Cleared after task completion

**Long-term (Reusable Knowledge)**
- Goal progress and checkpoints
- Learned patterns and anti-patterns
- Domain knowledge acquired
- Persists across tasks

### Shared State (Files)
Workers read/write to shared files:
- `memory/goals/[goal].md` — goal progress
- `memory/goals/checkpoints/` — state snapshots
- `memory/agent-outputs/` — worker outputs
- Workspace files as needed

### Session Isolation
Each spawned session:
- Has own context window (short-term)
- Cannot see other workers' sessions
- Reports via structured output
- Accesses long-term via files only

### Manager Maintains
- Overall goal state
- Worker assignments and status
- Quality review log
- Trace ID → output mapping
- Final synthesis

### Memory Compaction
When context grows large:
- Summarize completed task outputs
- Archive detailed logs to files
- Keep only active task context
- Preserve trace IDs for recovery

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
- ❌ **Free-form handoffs** (no schema validation)
- ❌ **No retry logic** (single failure = abort)
- ❌ **No trace IDs** (can't debug failures)
- ❌ **Ignoring partial outputs** (lose work on failure)
- ❌ **Parallel workers duplicating work** (no coordination)

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

## Sources

- Anthropic Multi-Agent Research System: Orchestrator-worker, parallel subagents
- OpenAI Agents SDK: LLM vs code orchestration, handoffs
- Skywork Best Practices: Structured handoffs as APIs, QA loops
- Galileo Failure Recovery: Circuit breakers, isolation boundaries
- LangGraph: Checkpointing, typed state, human-in-loop
- CrewAI: Role-based collaboration, built-in evaluators

---

*Architecture v1.1 — 2026-02-05*
*v1.1 Changes: Added structured handoff protocol (versioned schema), failure recovery (retry/circuit breaker), QA loop (producer→reviewer→publisher), observability/tracing (trace IDs, SLOs), memory types (short-term/long-term)*

*v1.0: Initial architecture — supervisor pattern, spawn rules, promote/demote*
