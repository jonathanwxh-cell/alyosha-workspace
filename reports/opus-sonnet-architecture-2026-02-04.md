# Opus-Sonnet Architecture: Objective-Aligned Model Routing

*Draft: 2026-02-04*
*Principle: Never compromise on objectives. Optimize everything else.*

---

## The Core Insight

From research: **"GPT-5 for planning, GPT-3.5 for execution"** — the pattern that works.

Applied to us:
- **Opus** = Strategic thinking, planning, deep reasoning
- **Sonnet** = Execution, day-to-day, information gathering

---

## Jon's Objectives (What Must Not Be Compromised)

From USER.md — these require Opus-level reasoning:

| Category | Examples |
|----------|----------|
| **Investment thesis** | Forming/revising long-term views, position sizing logic |
| **Risk analysis** | Tail risks, fragility mapping, second-order effects |
| **Deep reasoning** | Multi-step logic, Talebian analysis, contrarian thinking |
| **Cross-domain synthesis** | Connecting unrelated fields, original insights |
| **Strategic planning** | Life/work decisions, long-term direction |
| **Self-improvement** | Daemon architecture, learning from failures |

---

## Proposed Architecture

### Layer 1: Opus (Strategic Brain)

**When to use:**
- Investment thesis formation or revision
- Risk/fragility deep dives
- Multi-step reasoning chains
- "What should I do?" type decisions
- Cross-domain synthesis
- Planning sessions (weekly proposals, strategic reviews)
- Debugging complex problems
- Architecture/design decisions

**Trigger words/patterns:**
- "analyze", "thesis", "strategy", "risk", "fragility"
- "what do you think about", "should I"
- "plan", "design", "architect"
- Any explicit `/opus` command

### Layer 2: Sonnet (Execution Engine)

**When to use:**
- Information gathering and research
- Summaries and briefings
- Status updates and monitoring
- Script execution and reporting
- Routine questions with clear answers
- Following established playbooks
- All crons (already configured)

**Default for:**
- Quick questions
- News/market updates
- Email triage
- Kids dinner ideas
- Most daemon heartbeat work

### Layer 3: Haiku (Mechanical Tasks)

**When to use:**
- Script + status report
- Format conversion
- Simple threshold checks
- Deduplication checks

---

## Implementation Options

### Option A: Manual Switching (Simplest)

**How it works:**
- Default session = Sonnet
- Jon types `/opus` when strategic thinking needed
- Types `/sonnet` to return to default

**Pros:**
- Full control
- Zero false routing
- Simple to implement

**Cons:**
- Friction
- Might forget to switch for important stuff

**Implementation:** Use `session_status model=X` commands

---

### Option B: Keyword-Triggered (Semi-Automatic)

**How it works:**
- Sonnet by default
- Certain keywords/phrases auto-escalate to Opus:
  - "thesis", "risk analysis", "fragility", "strategy"
  - "what should I", "deep dive", "analyze"
  - "plan", "design", "architecture"

**Pros:**
- Less friction
- Catches important topics automatically

**Cons:**
- False positives (keyword in casual context)
- Requires keyword detection logic

**Implementation:** Would need OpenClaw config change or wrapper

---

### Option C: Session-Type Based (Recommended)

**How it works:**
- **Main interactive session** = Sonnet default, with easy `/opus` escalation
- **Strategic crons** = Opus (Weekly Ambitious Proposal, Self-Review)
- **Execution crons** = Sonnet (news, research, monitoring)
- **Mechanical crons** = Haiku (scripts, status)

**Pros:**
- Predictable costs
- Strategic work always gets Opus
- Day-to-day efficient on Sonnet
- No routing logic needed

**Cons:**
- Need to remember `/opus` for ad-hoc strategic thinking

**Implementation:** 
1. Main session default → Sonnet
2. Move 2-3 strategic crons → Opus
3. Move mechanical crons → Haiku

---

### Option D: Objective-Aligned Routing (Most Sophisticated)

**How it works:**
- Define "objective categories" in config
- Any conversation touching those categories → Opus
- Everything else → Sonnet

**Objective categories:**
1. Investment decisions (buy/sell/hold, thesis)
2. Risk assessment (fragility, tail risks)
3. Life planning (career, family, priorities)
4. Self-improvement (daemon design, learning)
5. Deep analysis (cross-domain, multi-step)

**Pros:**
- Truly aligned with what matters
- Automatic escalation for important topics

**Cons:**
- Requires classification (adds latency/cost)
- Edge cases

**Implementation:** Would need classifier (Haiku?) or rule-based detection

---

## Recommended Path

### Phase 1: Simple Start (This Week)

1. **Switch main session default to Sonnet**
   - `session_status model=sonnet`
   
2. **Add easy escalation**
   - When strategic topic comes up, I prompt: "This seems strategic — want me to switch to Opus?"
   - Or Jon types `/opus` explicitly

3. **Keep strategic crons on... wait, they're already Sonnet**
   - Consider: Move "Weekly Ambitious Proposal" to Opus (strategy)
   - Consider: Move "Weekly Self-Review" to Opus (meta-improvement)

### Phase 2: Evaluate (Week 2)

- Track: Did Sonnet quality feel insufficient anywhere?
- Track: How often did we escalate to Opus?
- Adjust routing based on evidence

### Phase 3: Refine (Week 3+)

- If working well: Expand Haiku for mechanical
- If Sonnet gaps found: Define clearer Opus triggers

---

## Cost Projection

| Component | Current | Proposed |
|-----------|---------|----------|
| Main session | Opus always | Sonnet default, Opus ~20% |
| Strategic crons | Sonnet | Opus (2-3 crons) |
| Execution crons | Sonnet | Sonnet |
| Mechanical crons | Sonnet | Haiku |

**Net effect:** ~30-40% cost reduction, Opus preserved for what matters.

---

## Quality Safeguards

### Never Compromise On:
- Investment thesis discussions → Always offer Opus
- Risk/fragility analysis → Always offer Opus  
- "What should I do?" questions → Always offer Opus
- Multi-step reasoning requests → Always offer Opus

### Automatic Escalation Triggers (I implement):
When I detect these topics in Sonnet mode, I'll prompt:
- "This touches investment thesis — switch to Opus?"
- "This needs deep reasoning — Opus recommended"

### Easy Override:
- `/opus` — switch to Opus
- `/sonnet` — switch to Sonnet
- `/haiku` — switch to Haiku (if needed)

---

## Decision Needed

**Which option to start with?**

| Option | Effort | Risk | Savings |
|--------|--------|------|---------|
| A: Manual | Low | Low | Medium |
| B: Keyword | Medium | Medium | Medium |
| **C: Session-type** | Low | Low | High |
| D: Objective-aligned | High | Medium | High |

**My recommendation:** Option C (Session-type based)
- Start simple
- Sonnet default for main session
- I prompt for Opus when strategic topics detected
- Measure and adjust

---

## Summary

**Philosophy:** Opus is for thinking. Sonnet is for doing.

**Rule:** If it affects Jon's objectives → Opus. If it's information/execution → Sonnet.

**Implementation:** Start with Sonnet default + easy escalation. Measure. Refine.

---

*Awaiting feedback before any changes.*
