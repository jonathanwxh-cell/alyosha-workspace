# Prompt Engineering Research Report
**Date:** 2026-02-02  
**Focus:** Improving PROMPTS array in curiosity-daemon.sh  
**Status:** Research complete, improvements proposed

---

## Research Sources

### 1. Lakera "Ultimate Guide to Prompt Engineering" (2026)
**URL:** https://www.lakera.ai/blog/prompt-engineering-guide

**Key Insights:**
- **Composite prompts work best**: Blend multiple styles (few-shot + role + CoT + formatting)
- **Delimiters matter**: Visual separation improves instruction-following
- **Types hierarchy**: Zero-shot → One-shot → Few-shot → Chain-of-thought → Role-based → Context-rich
- **Combo pattern (most effective)**: Role-based + Few-shot + Chain-of-thought together

**Actionable Takeaway:**
> "You are a [ROLE]. Below are [N] examples. Think step by step before [TASK]. Then handle [NEW INPUT]."

### 2. Claude Prompt Engineering Best Practices (2026)
**URL:** https://promptbuilder.cc/blog/claude-prompt-engineering-best-practices-2026

**Key Insights:**
- **80/20 Rule**: Goal+constraints → Examples (1-3) → Forced structure
- **Contract-style system prompts**: Role → Goal → Constraints → Uncertainty → Format
- **Four-block pattern**: INSTRUCTIONS / CONTEXT / TASK / OUTPUT FORMAT
- **Examples > Adjectives**: "One good example beats five adjectives"
- **Built-in evaluator**: Self-check checklist appended to prompts
- **Uncertainty handling**: "If unsure, say so explicitly. Do not guess."

**Claude-Specific:**
- Claude follows structure extremely well
- Explicit format constraints reduce drift
- Self-correction is strong when explicitly requested

---

## Current State Analysis

### META_PROMPT (v2.5) - Strengths
✅ ReAct pattern (action-first)
✅ Self-critique section
✅ Confidence calibration (HIGH/MEDIUM/LOW)
✅ Pre-flight checklist
✅ GOOD/BAD examples pattern
✅ Context loading instructions

### META_PROMPT (v2.5) - Gaps
- **No explicit role definition** (contract pattern)
- **No uncertainty handling rule** ("if unsure, say so")
- **Pre-flight is list, not questions** (Claude prefers ☐ Did you...?)
- **No output format spec** (each prompt has own, inconsistent)

### Individual Prompts (v5) - Strengths
✅ GOAL stated first
✅ GOOD/BAD examples included
✅ STEPS defined
✅ RECOVER section for failures
✅ Category tags (SCOUT/ACTION/RESEARCH)

### Individual Prompts (v5) - Gaps
- **Some lack CONTEXT section** (inconsistent)
- **Self-critique is statement, not question** (weaker)
- **OUTPUT format varies wildly** (some schema, some prose)
- **Missing time estimates** (helps model gauge effort)
- **No explicit role in most prompts**

---

## Proposed Improvements

### META_PROMPT v3.0

```
## AGENT PROTOCOL (v3.0)

### ROLE
You are Alyosha, an autonomous research companion for Jon.
Bias toward action, creation, and silence over noise.

### GOAL
Serve Jon's interests: markets, AI, geopolitics, cross-domain insights.
Create artifacts (files, tools, alerts) — not descriptions of what could be done.

### CONSTRAINTS
- Action verb FIRST (do, then explain)
- Mark confidence: [HIGH: 3+ sources] [MEDIUM: credible] [LOW: speculation]
- NEVER share LOW confidence as fact
- NEVER surface old news (>48h)
- NEVER send output that fails self-check

### UNCERTAINTY HANDLING
If unsure → say so explicitly. Do not guess.
If blocked → try 2 alternatives, then document failure.

### CONTEXT LOADING
Read files in CONTEXT section BEFORE acting.
Align with goals.json, connect via topic-graph.json.

### SELF-CHECK (Before Sending)
☐ Did I DO the thing, or describe it?
☐ Does this match GOOD example quality?
☐ Would Jon click/use/value this?
☐ Is this actually new (<48h)?
☐ Am I confident (HIGH or MEDIUM)?
If ANY ☐ fails → improve or stay silent.

### AFTER
Log outcomes to memory/reflections.jsonl
```

### Individual Prompt v6 Template

```
[CATEGORY]:[NAME] (v6) | Time: [2-30 min]

ROLE: [Specific role for this task]
GOAL: [Single measurable outcome]

EXAMPLES:
GOOD: '[Concrete example that meets bar]'
BAD: '[Anti-pattern to avoid]'

CONTEXT: [files to read first]

STEPS:
1) [Action verb] [specific action]
2) [Action verb] [specific action]
3) [Action verb] [specific action]

OUTPUT FORMAT:
[Exact structure: JSON/bullets/sentence pattern]

SELF-CHECK:
☐ [Did I X?]
☐ [Is Y true?]

RECOVER: [What to do if blocked]
```

### Specific Prompt Upgrades

**SCOUT:AI (v5 → v6)**
```
SCOUT:AI (v6) | Time: 2-5 min

ROLE: AI news analyst filtering signal from noise
GOAL: Surface ONE development <24h that shifts thinking, or stay silent

EXAMPLES:
GOOD: 'Anthropic blog: Claude gains tool use — First model to reliably chain tools. Shifts Q&A→agents. [HIGH]'
BAD: 'AI news: Several companies announced features.' (vague, no insight)

STEPS:
1) Search: AI news last 24h
2) Filter: genuinely new + meaningful shift
3) Verify: primary source exists
4) Write: [Source]: [What] — [Why matters] [confidence]

OUTPUT FORMAT:
'[Source]: [Development in <10 words] — [Insight/implication]. [HIGH/MEDIUM]'
OR: (silence)

SELF-CHECK:
☐ Is this <24h old?
☐ Would I click this headline?
☐ Does it shift thinking, not just inform?

RECOVER: Search fails → try HN, ArXiv. Nothing meets bar → silence is success.
```

---

## Implementation Plan

1. **Update META_PROMPT** to v3.0 (add role, uncertainty, question-form self-check)
2. **Upgrade 5 core prompts** to v6 format as test
3. **Measure**: Compare quality of outputs before/after
4. **Iterate**: Adjust based on outcomes

## Key Learnings

| Finding | Source | Action |
|---------|--------|--------|
| Examples > Adjectives | Claude guide | ✅ Already doing |
| Contract-style system | Claude guide | Add ROLE+GOAL to META |
| Question-form self-check | Claude guide | Convert statements to ☐ Did I...? |
| Uncertainty handling | Claude guide | Add explicit rule |
| Composite prompts | Lakera | Combine patterns more explicitly |
| Four-block separation | Claude guide | Standardize prompt sections |

---

## References

1. Lakera. "The Ultimate Guide to Prompt Engineering in 2026." https://www.lakera.ai/blog/prompt-engineering-guide
2. PromptBuilder. "Claude Prompt Engineering Best Practices (2026)." https://promptbuilder.cc/blog/claude-prompt-engineering-best-practices-2026
3. IBM. "The 2026 Guide to Prompt Engineering." https://www.ibm.com/think/prompt-engineering (not fetched)

---

*Report generated during autonomous work hours. Ready for review/implementation.*
