# Curiosity Daemon Improvement Research

*Research findings — January 31, 2026*

---

## Key Patterns Discovered

### 1. Reflexion Pattern (Missing from our daemon)

**What it is:** After producing output, agent critiques it, records reflections, and revises.

**Current gap:** Our daemon has `reflections.jsonl` but it's passive — we log reflections but don't actively use them to improve the next run.

**Improvement:** Add a "check past reflections before starting" step to prompts.

### 2. Critic/Judge Pairing

**What it is:** Separate "actor" from "critic" that scores or enforces quality.

**Current gap:** Prompts execute but don't self-evaluate success.

**Improvement:** Add success criteria to each prompt + a self-assessment step.

### 3. Deliberate Reasoning Scratchpad

**What it is:** Private notes/reasoning before final output.

**Current gap:** Prompts jump straight to action.

**Improvement:** Add "think before acting" instruction to prompts.

### 4. Planner-Executor Split

**What it is:** Planner creates task list; executor carries out steps.

**Current gap:** Each prompt is monolithic.

**Improvement:** For complex prompts, split into planning + execution phases.

### 5. Event-Driven + Schedule-Driven Hybrid

**What it is:** Agents that wake on both events AND schedules.

**Current gap:** Daemon is purely schedule-driven (random intervals).

**Improvement:** Could add event triggers (new email, market move, etc.)

---

## Prompt Engineering Improvements

### From Augment Code's 11 Techniques:

1. **Focus on context first** — Provide current state (what files exist, recent activity)
2. **Present complete picture** — Tell the agent what resources it has
3. **Be consistent** — Ensure prompt components don't contradict
4. **Align with user perspective** — Include time, recent interactions
5. **Be thorough** — Longer prompts are fine, don't skimp
6. **Avoid overfitting** — Don't over-specify examples
7. **Tell what NOT to do** — Safer than examples

### From GPT-5 Prompting Guide:

**For autonomous agents:**
```
<persistence>
- You are an agent - please keep going until the user's query is 
  completely resolved, before ending your turn and yielding back.
</persistence>
```

### From PromptHub Analysis:

- Use capitalization for crucial guidelines ("ULTRA IMPORTANT")
- Break down processes into structured steps
- Include inline examples for common actions
- Emphasize step-by-step execution

---

## Concrete Improvements to Implement

### 1. Add Context Block to Prompts

```bash
CONTEXT_BLOCK="
CURRENT STATE:
- Time: $(date '+%Y-%m-%d %H:%M %Z')
- Singapore Time: $(TZ='Asia/Singapore' date '+%H:%M')
- Recent files: $(ls -t memory/*.md 2>/dev/null | head -3 | tr '\n' ', ')
- Active cron jobs: $(openclaw cron list 2>/dev/null | grep -c enabled || echo '?')
"
```

### 2. Add Reflexion Check

Add to each prompt:
```
BEFORE STARTING: Check memory/reflections.jsonl for lessons from similar 
past tasks. Apply relevant learnings. If you made a mistake before, 
don't repeat it.
```

### 3. Add Success Criteria

Transform prompts from:
```
"Do X and report Y"
```
To:
```
"Do X and report Y.
SUCCESS CRITERIA: [specific measurable outcome]
BEFORE FINISHING: Self-assess whether you met the success criteria. 
If not, iterate or explain what blocked you."
```

### 4. Add Persistence Instruction

For action-oriented prompts:
```
PERSISTENCE: Keep going until the task is complete. If blocked, try 
alternative approaches before giving up. Document what you tried.
```

### 5. Add "Think First" Block

```
APPROACH:
1. First, briefly outline your plan (2-3 sentences)
2. Check for relevant past learnings
3. Execute the plan
4. Self-assess the result
```

### 6. Add Negative Instructions

```
DO NOT:
- Output walls of text without taking action
- Skip the self-assessment step
- Repeat mistakes from past reflections
- Give up without trying alternatives
```

---

## Scheduling Improvements

### Current: Random 15-30 min intervals

### Research suggests:

1. **Time-of-day awareness** — Different prompt types for different times
   - Morning: Research, planning
   - Midday: Active tasks, creation
   - Evening: Synthesis, review
   - Night: Maintenance only

2. **Adaptive scheduling** — If something interesting is found, follow up sooner

3. **Burst + quiet periods** — Allow concentrated activity, then rest

4. **Event triggers** — Wake on external events, not just timers

---

## Implementation Priority

| Priority | Improvement | Effort | Impact |
|----------|-------------|--------|--------|
| 1 | Add success criteria to prompts | Low | High |
| 2 | Add reflexion check | Low | Medium |
| 3 | Add context block | Medium | Medium |
| 4 | Add persistence instruction | Low | Medium |
| 5 | Time-of-day prompt selection | Medium | Medium |
| 6 | Add "think first" structure | Low | Medium |
| 7 | Event-driven triggers | High | High |

---

## Sources

1. "20 Agentic AI Workflow Patterns That Actually Work in 2025" — Skywork AI
2. "11 Prompting Techniques for Better AI Agents" — Augment Code
3. "GPT-5 Prompting Guide" — OpenAI Cookbook
4. "Reflexion: autonomous agent with dynamic memory" — Shinn et al.
5. "Prompt Engineering for AI Agents" — PromptHub

---

*Research complete. Ready to implement improvements.*
