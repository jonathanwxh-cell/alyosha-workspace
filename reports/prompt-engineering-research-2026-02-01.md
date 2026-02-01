# Prompt Engineering Research: Action-Oriented Prompts
*2026-02-01*

## Research Sources
- OpenAI Prompt Engineering Guide
- Lakera Prompt Engineering Guide 2026
- Prompting Guide (DAIR.AI)
- ReAct Framework (Yao et al., 2022)
- Mercity ReAct Implementation Guide

---

## Key Findings: What Makes Action-Oriented Prompts Effective

### 1. ReAct Framework (Highest Impact)

**Core insight:** Interleaving reasoning and action produces better outcomes than either alone.

Structure:
```
Thought: [Reasoning about current state and next step]
Action: [Specific action to take]
Observation: [Result of action]
... repeat until done ...
Final Answer: [Outcome]
```

**Why it works:**
- Forces decomposition of complex tasks
- Creates audit trail for debugging
- Prevents "hallucinated" actions (must reason first)
- Enables course-correction between steps

### 2. Explicit Success Criteria

**Bad:** "Research AI news"
**Good:** "Find ONE notable AI development. Success = concrete finding saved to file OR confident 'nothing notable' response."

Success criteria should be:
- Binary (pass/fail)
- Observable (can verify completion)
- Scoped (what "done" looks like)

### 3. Anti-Patterns (Negative Instructions)

Research shows explicitly stating what NOT to do is effective:
- "Do NOT output walls of text without taking action"
- "Do NOT just describe what could be done — DO it"
- "Do NOT give up without trying alternatives"

### 4. Time Budgets

Implicit scope through time hints:
- "Spend 3 minutes..." → lightweight scout
- "15-minute deep dive..." → thorough research
- "Quick scan..." → surface-level check

### 5. Output Format Specification

Clarity on deliverable format:
- "Save to reports/[topic]-[date].md"
- "2-3 sentence summary"
- "Bullets, not paragraphs"
- "JSON with fields: X, Y, Z"

### 6. Tangible Artifacts > Exploration

**Less effective:** "Explore interesting topics"
**More effective:** "Create a 200-word brief on [topic]"

Prompts that require a concrete deliverable consistently produce better outcomes.

---

## Analysis of Current PROMPTS Array

### Strengths
- Already uses domain prefixes (AI/TECH, MARKET, etc.)
- Has some success criteria and anti-patterns
- Good variety of task types
- META_PROMPT adds reflexion and persistence

### Gaps
1. **Inconsistent structure** — some prompts have clear criteria, others don't
2. **Variable verbosity** — some are tight, others ramble
3. **Missing time budgets** — unclear scope
4. **Soft language** — "could be", "consider" instead of direct action verbs
5. **Some prompts too open-ended** — "Agent's choice" gives no guidance

---

## Improved Prompt Design Principles

### Template
```
[DOMAIN] [TIME-BUDGET]: [VERB] [SPECIFIC OBJECT]. 
Output: [FORMAT]. 
Success: [BINARY CRITERIA]. 
Anti-pattern: [WHAT NOT TO DO].
```

### Verb Priority (Action > Description)
- ✅ Create, Build, Find, Generate, Fix, Update, Send
- ❌ Explore, Consider, Think about, Look into

### Tightness
- Max 50 words per prompt (excluding META_PROMPT)
- One primary objective per prompt
- Remove hedging language

---

## Recommended META_PROMPT Updates

Current META_PROMPT is good. Minor refinements:

```
## AGENT PROTOCOL

BEFORE: Check memory/reflections.jsonl. Note time (SGT). State plan in 1 sentence.

DURING: 
- Persist until done or blocked
- If blocked, try alternative THEN give up
- Take action — don't just describe

AFTER:
- Self-assess: Did output meet success criteria?
- If learning, append to memory/reflections.jsonl
- Be honest about partial success

DO NOT:
- Output text without action
- Skip self-assessment
- Repeat past mistakes (check reflections)
- Describe what could be done (DO it)
```

---

## Test Variations

### Original
"CURIOSITY ACTION: Find something genuinely interesting in AI/tech. Don't summarize — TRANSFORM it. Output options: create a brief (reports/), set up a cron monitor, build a quick tool, or draft something Jon could use. Success = tangible artifact created. Anti-pattern: walls of text with no action."

### Improved (Tighter)
"AI DISCOVERY [10 min]: Find ONE notable AI development. Transform into artifact: brief (reports/), cron alert, or tool. Output: File created + 2-sentence summary to Jon. Success: tangible deliverable exists. Don't: describe without creating."

### Analysis
- Improved is 40% shorter
- Clearer time scope
- Single objective
- Explicit deliverable
- Same anti-pattern, tighter wording

---

## Recommendations

1. **Standardize structure** across all prompts
2. **Add time budgets** to every prompt
3. **Remove hedge words** (consider, might, could)
4. **Single objective** per prompt
5. **Binary success criteria** for every prompt
6. **Test and iterate** — log which prompts produce good outcomes

---

*Research compiled by Alyosha, 2026-02-01*
