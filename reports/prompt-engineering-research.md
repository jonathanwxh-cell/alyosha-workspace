# Prompt Engineering Research: Action-Oriented Prompts

*2026-01-31 | Research for improving curiosity-daemon.sh*

---

## Key Findings

### From Anthropic (Context Engineering)

> "Good context engineering means finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."

**Key principles:**
1. **Right altitude** — Not too vague, not too brittle. Specific enough to guide, flexible enough to adapt.
2. **Clear structure** — Use delimiters (XML tags, markdown headers) to separate sections
3. **Minimal but complete** — Start minimal, add based on failure modes
4. **Token efficiency** — Every token has cost; make each one count

### From OpenAI Best Practices

1. **Put instructions first** — Before context
2. **Be specific** about outcome, length, format, style
3. **Show, don't just tell** — Examples of desired output
4. **Say what TO do, not just what NOT to do**
5. **Use leading patterns** — Start the response structure

### From $50M ARR AI Companies (Bolt, Cluely)

Their system prompts include:
- **Never/always lists** — Clear boundaries
- **If/then edge cases** — Handle known failure modes
- **Display instructions** — Exact output format
- **Code-like formatting** — Brackets, structured sections

---

## What Makes Action-Oriented Prompts Effective

### 1. Strong Action Verbs (Imperative)
❌ "Find something interesting about AI"
✅ "**Search** for AI news. **Create** a brief. **Save** it to reports/. **Send** summary to Jon."

### 2. Explicit Success Criteria
❌ "Check markets and report if notable"
✅ "Check markets. If any index moves >1% or major earnings surprise, **create a 200-word brief** with: headline, what happened, why it matters, what to watch."

### 3. Anti-Pattern Callouts
❌ Generic task description
✅ "Don't just summarize — **transform** the information into something actionable."

### 4. Output Specification
❌ "Save your findings"
✅ "Save to `reports/[topic]-[date].md` with sections: TL;DR, Key Points, Sources, Action Items"

### 5. Constraint Framing
❌ "Research this topic"
✅ "Research using max 3 searches. Produce output in under 5 minutes. Focus on actionable insights."

### 6. Progressive Depth Hints
- Quick: "Spend 2-3 minutes on a quick scan"
- Deep: "Do a thorough 15-minute deep dive"
- Creative: "Take an unexpected angle"

---

## Current PROMPTS Array Analysis

### What's Working
- ✅ "Don't just summarize - DO something"
- ✅ Specific action verbs (Create, Build, Save)
- ✅ Anti-pattern callouts
- ✅ Domain variety

### What's Missing
- ❌ Specific output formats
- ❌ Time/depth expectations
- ❌ Success criteria
- ❌ Constraint framing
- ❌ Progressive complexity levels

---

## Improved Prompt Patterns

### Pattern A: Quick Scout (2-5 min)
```
[DOMAIN] QUICK SCOUT: Spend 3 minutes scanning [source]. 
Find ONE thing worth knowing. 
If nothing notable, reply "Nothing notable in [domain]."
If something found: Send 2-3 sentence summary + why it matters.
No file creation needed.
```

### Pattern B: Action Task (5-15 min)
```
[DOMAIN] ACTION: [specific task].
Output: [exact deliverable with format].
Save to: [path/filename pattern].
Success = [concrete criteria].
Anti-pattern: Don't just [common failure mode].
```

### Pattern C: Deep Dive (15-30 min)
```
[DOMAIN] DEEP DIVE: Thoroughly research [topic].
Use multiple sources (min 3).
Create: `reports/[topic]-[date].md` with:
  - TL;DR (2 sentences)
  - Key findings (bullets)
  - Sources used
  - Open questions
  - Action items for Jon
Send summary (100 words max) to Telegram.
```

### Pattern D: Creative (open-ended)
```
CREATIVE MOMENT: Make something unexpected.
Options: image, micro-fiction, concept visualization, tool prototype, absurdist artifact.
Constraint: Must be shareable/usable, not just described.
Save output. Surprise Jon.
```

### Pattern E: Self-Improvement
```
SELF-IMPROVE: Review [specific file/system].
Find ONE thing to improve.
Implement the improvement.
Log change to memory/self-improvement-log.md with: what, why, expected impact.
Report: "Improved [X] by [doing Y]."
```

---

## Testing Framework

To evaluate prompt effectiveness:

1. **Completion rate** — Did the task get done?
2. **Output quality** — Was the deliverable useful?
3. **Efficiency** — Time/tokens spent vs value
4. **Action ratio** — Actions taken vs just talking
5. **Jon engagement** — Did he respond/react?

---

## Recommendations

1. **Restructure prompts** using Pattern A-E templates
2. **Add time expectations** (quick/medium/deep)
3. **Specify output formats** explicitly
4. **Include success criteria** in each prompt
5. **Balance variety** — mix of quick, action, deep, creative
6. **Test and iterate** — log which prompts produce best outcomes
