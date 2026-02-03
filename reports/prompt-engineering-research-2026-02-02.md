# Prompt Engineering Research

*2026-02-02 — Improving the curiosity-daemon PROMPTS array*

## Key Research Findings

### 1. Few-Shot Examples (Most Impactful)
**Source:** Lakera 2026, Min et al. 2022

- Examples are more important than perfect labels
- Format consistency matters even more than correctness
- GOOD/BAD contrast is highly effective
- **Current prompts: ✅ Already using GOOD/BAD examples in v5**

### 2. Chain-of-Thought (CoT)
**Source:** Wei et al. 2022, Kojima et al. 2022

- "Let's think step by step" significantly improves reasoning
- Works even zero-shot
- Best combined with few-shot examples
- **Current prompts: ⚠️ STEPS section exists but no explicit reasoning prompt**

### 3. ReAct (Reason + Act)
**Source:** Yao et al. 2022

- Interleave reasoning traces with actions
- Thought → Action → Observation cycle
- Allows dynamic plan adjustment
- **Current prompts: ⚠️ Implicit in structure but not explicit**

### 4. Self-Consistency
**Source:** Wang et al. 2022

- Generate multiple reasoning paths
- Select most consistent answer
- **Current prompts: ❌ Not implemented**

### 5. Reflexion
**Source:** Shinn et al. 2023

- Self-reflect on failures
- Learn from mistakes in-context
- **Current prompts: ✅ RECOVER section addresses this**

---

## Current Prompt Structure Analysis

```
GOAL → EXAMPLES (GOOD/BAD) → STEPS → SELF-CRITIQUE → OUTPUT → RECOVER
```

### Strengths
- Clear goal statement
- Contrastive examples (highly effective)
- Step-by-step actions
- Self-critique checkpoint
- Recovery instructions

### Weaknesses
1. **No explicit reasoning prompt** — Missing "Think:" or "Reason:" prefix
2. **Steps are instructions, not reasoning** — Could benefit from CoT
3. **No multi-path generation** — Single-shot execution
4. **Confidence levels underutilized** — Mentioned but not enforced
5. **Output format sometimes vague** — Could be more templated

---

## Improvement Patterns

### Pattern 1: Add Explicit Reasoning Phase
**Before:**
```
STEPS: 1) Search 2) Filter 3) Share
```

**After:**
```
THINK: What would make this genuinely valuable? What's the bar?
STEPS: 1) Search 2) Filter 3) Share
```

### Pattern 2: Add ReAct-Style Checkpoints
**Before:**
```
STEPS: 1) Search 2) Filter 3) Output
```

**After:**
```
STEPS:
1) Search → OBSERVE: Found X results
2) Filter → REASON: Of these, only Y meets bar because...
3) Output → CHECK: Does this pass quality gate?
```

### Pattern 3: Strengthen Confidence Calibration
**Before:**
```
OUTPUT: [thing] [HIGH/MED/LOW]
```

**After:**
```
CONFIDENCE RULES:
- HIGH: 3+ independent sources confirm, primary source available
- MEDIUM: 2 sources or 1 highly credible source
- LOW: Single source, speculation, or inference
RULE: Never share LOW as fact. Mark uncertainty explicitly.
```

### Pattern 4: Add "Would I Click?" Test
```
QUALITY GATE (before sending):
□ Would I click this headline?
□ Would I forward this to a smart friend?
□ Does this beat the BAD example?
□ Is this better than silence?
```

### Pattern 5: Template Forcing
**Before:**
```
OUTPUT: Brief insight.
```

**After:**
```
OUTPUT TEMPLATE:
[EMOJI] **[CATEGORY]**
[Headline]: [Detail]
→ [So what / action / implication]
[Confidence: HIGH/MED]
```

---

## Proposed V6 Prompt Structure

```
[NAME] (v6) | CONTEXT: [files to load] | GOAL: [one sentence]

THINK: [Reasoning prompt — what question to answer internally]

EXAMPLES:
✅ GOOD: [Specific high-quality example output]
❌ BAD: [Specific low-quality example to avoid]

STEPS: (ReAct-style)
1) [Action] → Check: [validation]
2) [Action] → Check: [validation]
3) [Action] → Check: [validation]

CONFIDENCE:
- HIGH: [criteria]
- MEDIUM: [criteria]  
- LOW: [criteria — don't share]

OUTPUT TEMPLATE:
[Exact format to follow]

QUALITY GATE:
□ Would I click/use/forward this?
□ Better than BAD example?
□ Confidence ≥ MEDIUM?
□ Better than silence?
If ANY NO → improve or skip.

RECOVER: [What to do if blocked]
```

---

## Test: Compare V5 vs V6 on Same Task

### Task: Find one notable AI development

**V5 Prompt (current):**
```
SCOUT:AI (v5) | GOAL: ONE AI development <24h that shifts thinking.
GOOD: 'Anthropic blog: Claude gains tool use — First model to reliably chain tools. Shifts Q&A→agents. [HIGH]'
BAD: 'AI news: Several companies announced features.' (vague)
STEPS: 1) Search AI news 2) Filter: new + meaningful 3) Verify source 4) SELF-CHECK: Would I click?
OUTPUT: '[Source]: [What] — [Why] [HIGH/MED]' OR silence.
RULE: Only HIGH (primary) or MEDIUM (credible). Never share LOW.
RECOVER: Search fail → HN, ArXiv. Nothing good → silence.
```

**V6 Prompt (improved):**
```
SCOUT:AI (v6) | CONTEXT: memory/topic-graph.json | GOAL: ONE AI development that shifts thinking.

THINK: What would make a developer/investor stop scrolling? Not incremental — paradigm.

EXAMPLES:
✅ GOOD: "Anthropic: Claude tool chaining → Q&A→agents shift. [HIGH: primary source]"
❌ BAD: "AI news: Several announcements." (no specifics, no so-what)

STEPS (ReAct):
1) Search → CHECK: Found <24h news? If no, try HN/ArXiv.
2) Filter → REASON: Does this change how someone builds/invests?
3) Verify → CHECK: Is source primary or credible secondary?
4) Draft → TEST: Would I click this? Better than BAD?

CONFIDENCE:
- HIGH: Primary source (company blog, paper, official announcement)
- MEDIUM: Credible secondary (major tech outlet, verified account)
- LOW: Rumor, single anonymous source → DON'T SHARE

OUTPUT:
"[Source]: [What] — [Why it matters] [Confidence]"

GATE: Click-worthy? Specific? Non-obvious? If no → silence.
RECOVER: Bad search → HN front page. Still nothing → silence is fine.
```

**Key V6 Improvements:**
1. Added THINK phase (reasoning prompt)
2. Made STEPS ReAct-style with checkpoints
3. Explicit confidence criteria
4. "Would I click?" test more prominent
5. Clearer template

---

## Implementation Priority

| Change | Impact | Effort | Priority |
|--------|--------|--------|----------|
| Add THINK phase | High | Low | 1 |
| ReAct-style STEPS | Medium | Medium | 2 |
| Confidence criteria | High | Low | 1 |
| Output templates | Medium | Low | 3 |
| Quality gate checklist | High | Low | 1 |

---

## Next Steps

1. Update 3-5 most-used prompts to v6 format
2. Test both versions on same tasks
3. Track which produces better outputs
4. Roll out improvements to full array
