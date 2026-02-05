# GOALS.md — Goal Framework v3.1

*Research-informed. Self-improving. One active goal at a time.*

---

## Current Goal

**Status:** None active

---

## Core Principles

1. **Test-First**: Define what success looks like BEFORE acting
2. **Reflect Always**: Every action generates learning (dual-loop: inside + outside view)
3. **Fail Forward**: Failures improve the system
4. **Confidence-Gated**: Low confidence = don't proceed
5. **Memory-Backed**: Everything logged, nothing lost
6. **Verify Inputs**: Don't trust observations blindly — cross-check
7. **Know When Done**: 80% with certainty beats 100% with diminishing returns
8. **Checkpoint Progress**: Save state at milestones, enable rollback

---

## Goal Lifecycle

### Phase 1: DEFINE
**Purpose:** Establish clear, measurable goal with boundaries.

**Required:**
- Goal statement (specific, measurable)
- Constraints (time, capital, resources, risk limits)
- Success criteria (how will we KNOW it worked?)
- Failure criteria (when do we stop/pivot?)
- Autonomy tier (see below)

**Success Tests (TDD for Goals):**
Before proceeding, define 3-5 "tests" that would prove success:
```
□ Test 1: [specific measurable outcome]
□ Test 2: [specific measurable outcome]
□ Test 3: [specific measurable outcome]
```
These tests guide all subsequent work.

**Output:** Goal definition with success tests
**Checkpoint:** Jon approves ✓
**Confidence required:** HIGH (>80%)

---

### Phase 2: UNDERSTAND
**Purpose:** Research problem space before solutions.

**Questions to Answer:**
- What domain knowledge is required?
- What don't I know that I need to know?
- What has been tried before? (by me, by others)
- What are the key variables and uncertainties?
- What mistakes do people commonly make?

**Process:**
1. Generate questions (minimum 5)
2. Research each with sources
3. Synthesize findings
4. Map knowledge gaps
5. Self-critique: What am I missing?

**Dual-Loop Reflection:**
*Introspection (inside view):*
- What would a skeptic say about my understanding?
- What sources disagree with my synthesis?
- What's the strongest argument against my conclusions?

*Extrospection (outside view — step outside yourself):*
- If I showed this to an expert, what would they immediately question?
- What am I too close to see?
- What would a fresh observer notice that I've missed?

**Output:** Domain understanding summary with confidence
**Checkpoint:** Jon confirms sufficient ✓
**Confidence required:** MEDIUM (>60%)

---

### Phase 3: APPROACH
**Purpose:** Evaluate methods and select strategy.

**Process:**
1. List candidate approaches (minimum 3, ideally 5+)
2. Research each with primary sources
3. Score against constraints:
   - Fit to goal (/10)
   - Risk level (/10)
   - Effort required (/10)
   - Track record (/10)
4. Recommend top 1-2 with reasoning

**Dual-Loop Reflection:**
*Introspection:*
- Am I biased toward a particular approach? Why?
- What's the anti-consensus view?
- What would make me change my recommendation?

*Extrospection:*
- What would an expert in this field recommend?
- If someone else proposed my recommendation, would I poke holes in it?
- What's the obvious thing I'm overlooking?

**Output:** Approach comparison + recommendation
**Checkpoint:** Jon picks approach ✓
**Confidence required:** MEDIUM (>60%)

---

### Phase 4: DECOMPOSE
**Purpose:** Break goal into executable structure.

**Hierarchy:**
```
Goal
├── Subgoal 1 (milestone)
│   ├── Task 1.1 (specific action)
│   │   └── Success test: [how to verify]
│   └── Task 1.2
│       └── Success test: [how to verify]
├── Subgoal 2
│   └── ...
└── Subgoal 3
```

**For each task:**
- Clear action statement
- Success test (how to know it's done)
- Dependencies (what must happen first)
- Approval needed? (yes/no)
- Estimated effort
- Risk level

**Dual-Loop Reflection:**
*Introspection:*
- Are tasks small enough to execute cleanly?
- Did I miss any dependencies?
- What could go wrong at each step?

*Extrospection:*
- Would a project manager approve this breakdown?
- What would someone unfamiliar with the goal find confusing?
- If this plan fails, what will the post-mortem say was obvious?

**Output:** Task tree with success tests
**Checkpoint:** Jon approves structure ✓
**Confidence required:** HIGH (>80%)

---

### Phase 5: EXECUTE
**Purpose:** Do the work. Learn continuously.

**OODA+ Loop (per task):**
```
VERIFY → OBSERVE → ORIENT → DECIDE → ACT → [repeat]
```

1. **Verify:** Are my inputs trustworthy?
   - Is data current? (check timestamps, freshness)
   - Is source reliable? (cross-reference if uncertain)
   - Am I hallucinating? (ground in concrete evidence)
   - *If verification fails → pause, get better data*

2. **Observe:** What's the current state? What data do I have?

3. **Orient:** How does this relate to the goal? What's changed?

4. **Decide:** What's the best next action? (with confidence)

5. **Act:** Execute. Log outcome immediately.

**After Each Task:**
```
□ Task completed? [yes/no]
□ Success test passed? [yes/no]
□ Unexpected outcomes? [describe]
□ What did I learn? [insight]
□ Confidence in result: [LOW/MEDIUM/HIGH]
```

**Completion Threshold (Good Enough Detection):**
Before iterating further, ask:
- Have I hit diminishing returns? (effort ↑, value ↓)
- Is 80% with high confidence better than 100% with low confidence?
- Am I polishing or actually improving?
- *If diminishing returns → declare done, move on*

**Failure Protocol:**
- 1 failure → Reflect, adjust, retry
- 2 failures → Deeper analysis, consider pivot
- 3 failures → Escalate to Jon with analysis

**Guardrails:**
- Tier 4 actions → per-action approval + rollback plan
- Low confidence → pause and report
- Scope creep → checkpoint before expanding

**Output:** Completed tasks with outcomes logged
**Checkpoints:** Per subgoal (milestone) ✓

---

### Phase 6: REVIEW
**Purpose:** Extract maximum learning from the goal.

**Evaluation:**
- Goal met? [fully / partially / failed]
- Success tests passed? [X/Y]
- Time vs estimate? [under / on / over]
- Unexpected challenges?

**Reflection Questions:**
- What worked better than expected?
- What worked worse than expected?
- What would I do differently?
- What surprised me?
- What should I never do again?

**Learning Extraction:**
1. Add key lessons → MEMORY.md
2. Add anti-patterns → ANTI-PATTERNS.md (if failures)
3. Update GOALS.md if framework needs improvement
4. Archive goal journal to `memory/goals/archive/`

**Meta-Learning:**
- Did this goal make me better at goals generally?
- What framework improvement does this suggest?

**Output:** Post-mortem with extracted lessons
**Action:** Apply lessons to system

---

## Autonomy Tiers

| Tier | Name | My Autonomy | Approval Needed | Use When |
|------|------|-------------|-----------------|----------|
| 1 | Rule-based | Execute predefined steps | None | Simple, low-risk |
| 2 | Workflow | Draft/research, you decide | All outputs | Learning new domain |
| 3 | Semi-auto | Act within guardrails | Milestones + Tier 4 | **Default** |
| 4 | Full-auto | Decide and act | Start + End only | High trust, bounded |

---

## Checkpoint Protocol

**Purpose:** Enable recovery from failures without losing progress.

**When to Checkpoint:**
- After each subgoal completion (automatic)
- Before any Tier 4 action
- Before any irreversible action
- When switching contexts or pausing work

**Checkpoint Contents:**
```
## Checkpoint: [Goal] / [Subgoal] — [timestamp]
- Progress: [X/Y tasks complete]
- Current state: [summary]
- Next action: [what comes next]
- Blockers: [if any]
- Key decisions made: [list]
- Rollback point: [last safe state]
```

**Storage:** `memory/goals/checkpoints/[goal-slug]-[timestamp].md`

**Recovery:**
- On failure → load last checkpoint
- On context loss → resume from checkpoint
- On pivot → archive checkpoint, start fresh

---

## Rollback Mechanism

**For Tier 4 actions (irreversible/high-risk):**

Before executing, document:
```
## Rollback Plan: [Action]
- **Action:** [what will be done]
- **Can it be undone?** [yes/no/partial]
- **If yes, how:** [specific steps]
- **If no, mitigation:** [damage control plan]
- **Worst case:** [what happens if this goes wrong]
- **Acceptable?** [yes/no — if no, don't proceed]
```

**Examples:**
- Trade executed → Rollback: Close position (may have loss)
- Email sent → Rollback: Send correction/apology
- File deleted → Rollback: Restore from trash/backup
- Config changed → Rollback: Revert to previous config

**Rule:** No Tier 4 action without documented rollback plan.

---

## Confidence Scoring

Every output gets a confidence score:

| Score | Meaning | Action |
|-------|---------|--------|
| HIGH (>80%) | Strong evidence, multiple sources | Proceed |
| MEDIUM (60-80%) | Reasonable evidence, some gaps | Proceed with caution |
| LOW (<60%) | Weak evidence, significant uncertainty | **STOP. Surface to Jon.** |

**Never proceed with LOW confidence without explicit approval.**

---

## Failure Memory

Failures are valuable. Log them explicitly:

```markdown
## Failure Log: [Goal Name]

### Failure 1
- **What happened:** [description]
- **Why it failed:** [root cause]
- **What I tried:** [approaches attempted]
- **Lesson:** [what to do differently]
- **Added to anti-patterns?** [yes/no]
```

**Failure → Learning → System Improvement**

---

## Self-Improvement Mechanism

After EVERY goal (success or failure):

1. **Extract Patterns:**
   - What worked that should be repeated?
   - What failed that should be avoided?

2. **Update System:**
   - MEMORY.md ← key insights
   - ANTI-PATTERNS.md ← failure modes
   - GOALS.md ← framework improvements
   - Scripts ← automation opportunities

3. **Track Improvement:**
   - Log changes to `memory/self-improvement-log.md`
   - Include: what changed, why, evidence, expected impact

**Goal of Goals:** Each goal makes the system better at future goals.

---

## Cross-Goal Learning

Maintain `memory/goals/patterns.md`:

| Pattern | Occurrences | Confidence | Action |
|---------|-------------|------------|--------|
| [what works] | [count] | [H/M/L] | [keep doing] |
| [what fails] | [count] | [H/M/L] | [stop doing] |

Update after each goal review.

---

## Anti-Patterns

- ❌ Skipping UNDERSTAND (jumping to solutions)
- ❌ Single approach without alternatives
- ❌ No success tests defined upfront
- ❌ Proceeding with LOW confidence
- ❌ Ignoring failures (no learning extraction)
- ❌ Plan fixation (refusing to adapt)
- ❌ Scope creep without checkpoint
- ❌ Acting beyond autonomy tier
- ❌ No self-improvement after goal ends
- ❌ **Trusting inputs blindly** (no verification)
- ❌ **Endless iteration** (not recognizing "good enough")
- ❌ **Tier 4 without rollback plan** (irreversible action without escape hatch)
- ❌ **Single-loop reflection only** (missing external perspective)

---

## Goal Log

| Goal | Started | Ended | Tests Passed | Outcome | Key Lesson |
|------|---------|-------|--------------|---------|------------|
| — | — | — | — | — | — |

---

## Sources

- Reflexion (Shinn et al.): Self-reflection, verbal reinforcement
- Self-Refine: Generate → Critique → Improve loop
- OODA Loop (Boyd): Observe → Orient → Decide → Act
- Test-Driven Development: Define tests before code
- BabyAGI: Task generation from outcomes
- Hierarchical Task Networks: Decomposition patterns
- Andrew Ng: Reflection as core agentic pattern
- Dual-Loop Reflection (Nature 2025): Extrospection + Introspection
- Schneier OODA Critique (2025): Input verification, trust assumptions
- LangGraph/Dapr: Checkpoint-based state persistence
- MAR (Multi-Agent Reflexion): Diminishing returns detection

---

*Framework v3.1 — 2026-02-05*
*v3.1 Changes: Added dual-loop reflection (extrospection), input verification (VERIFY step), completion threshold (good enough detection), checkpoint protocol, rollback mechanism for Tier 4 actions*

*v3.0 Changes: Added success tests (TDD), self-critique questions, confidence gating, failure memory, self-improvement mechanism, cross-goal learning, OODA execution loop*
