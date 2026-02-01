# Daemon Research: Making the Curiosity Daemon Smarter

*Research Date: 2026-02-02*

---

## TL;DR

Researched autonomous agent architectures, prompt engineering techniques, and proactive scheduling patterns. Key improvements: self-refinement loops, dynamic context injection, meta-prompting, and four-layer architecture (Autonomy → Reasoning → Action → Memory).

---

## 1. Advanced Prompt Engineering Techniques

### 1.1 Prompt Chaining
**What:** Decompose complex goals into smaller, linked steps. Each step feeds into the next.

**Current state:** Our curiosity-daemon.sh has standalone prompts but limited chaining.

**Improvement:**
```
Step 1: Classify task type → 
Step 2: Gather context → 
Step 3: Execute core task → 
Step 4: Self-verify → 
Step 5: Format output
```

**Implementation:** Add explicit chain markers in prompts:
```
CHAIN: [classify] → [gather] → [execute] → [verify] → [format]
```

### 1.2 Self-Refinement Loops
**What:** Agent critiques and improves own output before delivering.

**Pattern:**
1. Generate initial output
2. Apply critic prompt ("What's wrong with this?")
3. Revise based on critique
4. Repeat until quality threshold met

**Implementation idea:** Add `REFINE:` instruction to high-stakes prompts:
```
REFINE: After generating, review for: (1) accuracy, (2) investment angle, (3) novelty. Revise if any fails.
```

### 1.3 Dynamic Context Injection
**What:** Fetch relevant knowledge dynamically instead of hardcoding.

**Current state:** We have memory files but don't dynamically inject them into cron prompts.

**Improvement:** Cron prompts should read context files first:
```
CONTEXT: Read memory/daily-context.json before generating.
```

### 1.4 Meta-Prompting
**What:** Prompts that generate other prompts. Self-adapting systems.

**Use case:** When a prompt category consistently underperforms, have the agent rewrite it.

**Implementation:** Add to weekly self-review:
```
If a prompt category got <20% engagement over 4 weeks, rewrite that prompt.
```

### 1.5 Prompt Versioning
**What:** Treat prompts like code — version, test, measure.

**Current state:** We have `self-improvement-log.md` but no systematic versioning.

**Improvement:** Add version tags to prompts in curiosity-daemon.sh:
```bash
# v2.4 (2026-02-02) - Added self-refinement step
```

---

## 2. Agent Architecture Principles

### Four Core Principles (from orq.ai)

| Principle | Current State | Gap |
|-----------|---------------|-----|
| **Autonomy** | ✅ Heartbeat + crons operate independently | Good |
| **Adaptability** | ⚠️ feedback-log exists but limited use | Need more feedback → action loops |
| **Goal-Oriented** | ⚠️ Tasks are ad-hoc, not goal-layered | Need explicit goal hierarchy |
| **Continuous Learning** | ⚠️ reflections.jsonl exists, underused | Need stronger learning integration |

### Architectural Components

| Component | Our Implementation | Gap |
|-----------|-------------------|-----|
| Perception Module | web_search, web_fetch, file reads | Good |
| Decision-Making Engine | HEARTBEAT.md logic, prompt routing | Could be more sophisticated |
| Action Module | cron jobs, message tool, exec | Good |
| Memory Module | memory/*.md, *.jsonl files | Need better retrieval |

---

## 3. Proactive Agent Patterns

### The Autonomy Loop (from Medium research)

```
+-----------------------------+
| Scheduler / Event Loop      | → triggers checks periodically
+-----------------------------+
              |
              v
+-----------------------------+
| Context Collector / Sensor  | → gathers relevant data
+-----------------------------+
              |
              v
+-----------------------------+
| Reasoning Agent             | → decides what to do
+-----------------------------+
              |
              v
+-----------------------------+
| Action Layer                | → executes tasks
+-----------------------------+
```

**Our mapping:**
- Scheduler = OpenClaw cron + heartbeat system ✅
- Context Collector = heartbeat-state.json + memory reads ⚠️ (could be better)
- Reasoning Agent = HEARTBEAT.md decision logic ⚠️ (could be smarter)
- Action Layer = message tool, exec, cron jobs ✅

### Four-Layer Architecture

| Layer | Purpose | Our Implementation |
|-------|---------|-------------------|
| **Autonomy** | Scheduling, triggers, looping | Cron jobs + heartbeat |
| **Reasoning** | Intelligent logic | META_PROMPT in curiosity-daemon.sh |
| **Action** | Execute tasks via tools | Tools + scripts |
| **Memory** | State/history | memory/ folder |

---

## 4. Concrete Improvements to Implement

### 4.1 Enhanced Context Loading (HIGH PRIORITY)
Add to HEARTBEAT.md:
```markdown
Before deciding actions, load:
1. memory/daily-context.json (if exists) - what's happening today
2. memory/heartbeat-state.json - last actions
3. memory/active-projects.json - what needs attention
```

### 4.2 Self-Refinement in High-Stakes Prompts (MEDIUM)
Add to cron prompts that surface to Jon:
```
Before delivering, verify:
- [ ] Contains non-obvious insight
- [ ] Investment angle included (if relevant)
- [ ] Not duplicate of recent content
If any fails, improve or skip.
```

### 4.3 Goal Hierarchy (MEDIUM)
Create `memory/goals.json`:
```json
{
  "longTerm": ["Be genuinely useful", "Build trust through competence"],
  "weekly": ["Ship NVDA dashboard", "Write Substack #2"],
  "daily": ["Check research topics", "Maintain memory"]
}
```
Reference in decision-making.

### 4.4 Smarter Feedback Integration (HIGH)
Weekly self-review should:
1. Calculate engagement rate per prompt category
2. Identify lowest performers
3. Either improve prompt OR disable if consistently low
4. Log changes with reasoning

### 4.5 Dynamic Prompt Adaptation (EXPERIMENTAL)
If a prompt type gets 3 consecutive no-engagement runs:
- Flag for review
- Optionally auto-generate improved version via meta-prompting

---

## 5. Implementation Plan

### Immediate (This Session)
- [x] Create this research report
- [ ] Update HEARTBEAT.md with context loading
- [ ] Add self-refinement to 3 key cron prompts
- [ ] Create memory/goals.json

### This Week
- [ ] Add version tags to curiosity-daemon.sh prompts
- [ ] Enhance weekly-self-review with engagement metrics
- [ ] Create memory/daily-context.json pattern

### Future
- [ ] Implement meta-prompting for prompt improvement
- [ ] Build prompt A/B testing capability
- [ ] Add LLM-as-judge for output scoring

---

## Sources

1. GoInsight.AI - "5 Advanced Prompt Engineering Techniques" (Nov 2025)
2. Orq.ai - "AI Agent Architecture: Core Principles & Tools" (2025)
3. Medium/@manuedavakandam - "From Reactive to Proactive" (Nov 2025)
4. PromptingGuide.ai - Chain-of-Thought Prompting
5. MachineLearningMastery - "7 Agentic AI Trends to Watch in 2026"

---

*Confidence: ⭐⭐⭐ — Multiple credible sources, practical patterns*

