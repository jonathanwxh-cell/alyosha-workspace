# Prompt Engineering Research — 2026-02-02

## Research Sources
- Lakera AI Guide to Prompt Engineering 2026
- Medium: Complete Prompt Engineering Guide for 2025
- Mirascope: 11 Prompt Engineering Best Practices

## Key Findings

### 1. Most Impactful Practice: Few-Shot Examples (3-5)
> "Provide Examples (Few-Shot): This is the single most impactful practice. Aim for 3–5+ diverse, high-quality examples."

**Current gap:** Our prompts have NO examples. This is the biggest improvement opportunity.

### 2. Strong Action Verbs First
> "Clear, concise prompts with strong action verbs (act, analyze, generate) consistently outperform verbose ones."

**Current status:** ✅ Good — we use GOAL/STEPS/OUTPUT structure with action verbs.

### 3. Be Specific About "Done"
> "Detail exactly what 'done' looks like — length, format, content structure."

**Current status:** ✅ Good — VERIFY/OUTPUT sections do this.

### 4. Advanced Techniques Missing

#### Recursive Self-Improvement Prompting (RSIP)
```
1. Generate initial output
2. Self-critique using specific criteria
3. Generate improved version
```
**Gap:** Our prompts don't ask for self-critique before output.

#### Calibrated Confidence Prompting (CCP)
```
Assign confidence levels (95%, 80-95%, <80%, unknown)
Justify high-confidence claims
Note what would increase confidence
```
**Gap:** We don't ask for confidence levels on claims.

#### Multi-Perspective Simulation (MPS)
```
1. Identify distinct perspectives
2. Articulate assumptions/arguments for each
3. Simulate dialogue between perspectives
4. Integrated analysis
```
**Gap:** Useful for RESEARCH prompts — not currently used.

### 5. Structure Comparison

**Current Pattern:**
```
GOAL → CONTEXT → STEPS → OUTPUT → VERIFY → RECOVER → NEVER
```

**Recommended Enhanced Pattern:**
```
GOAL → CONTEXT → THINK (perspective/criteria) → STEPS → SELF-CRITIQUE → OUTPUT → VERIFY → CONFIDENCE → RECOVER → NEVER
```

## Test Variations

### Original SCOUT:AI (v4)
```
SCOUT:AI (v4) | GOAL: Surface ONE AI development <24h that shifts mental models. 
STEPS: 1) Search 'AI news today' 'AI breakthrough' 2) Filter: genuinely new + Jon-relevant 3) Verify primary source 4) Share OR stay silent. 
OUTPUT: '[Source]: [What] — [Why it matters]' OR silence. 
VERIFY: □ <24h □ Primary source □ Non-obvious □ Not incremental. 
RECOVER: Search fail → try HN, ArXiv, X/AI. Nothing notable → silence (no 'nothing found'). 
NEVER: Hedge, surface follow-up coverage, editorialize without insight.
```

### Variation A: Add Self-Critique
```
SCOUT:AI (v5) | GOAL: Surface ONE AI development <24h that shifts mental models.
STEPS: 1) Search 'AI news today' 'AI breakthrough' 2) Filter: genuinely new + Jon-relevant 3) Verify primary source.
SELF-CRITIQUE: Before sharing, ask: "Would I click this? Is this actually new? Does it change how I think?"
OUTPUT: '[Source]: [What] — [Why it matters] — Confidence: [HIGH/MEDIUM]' OR silence.
VERIFY: □ <24h □ Primary source □ Non-obvious □ Passed self-critique.
RECOVER: Search fail → try HN, ArXiv. Nothing notable → silence.
NEVER: Hedge, share without self-critique, surface incremental progress.
```

### Variation B: Add Few-Shot Example
```
SCOUT:AI (v5) | GOAL: Surface ONE AI development <24h that shifts mental models.

GOOD EXAMPLE: "Anthropic blog: Claude gains tool use. — First major model to reliably chain tool calls. Shifts interaction from Q&A to agent workflows."

BAD EXAMPLE (don't do this): "AI news roundup: Several companies announced AI features today."

STEPS: 1) Search 'AI news today' 2) Filter for Jon-relevance 3) Match quality to good example.
OUTPUT: Single insight matching good example format, OR silence.
VERIFY: □ <24h □ Matches good example quality □ Non-obvious.
```

### Variation C: Calibrated Confidence
```
SCOUT:AI (v5) | GOAL: Surface ONE AI development <24h that shifts mental models.
STEPS: 1) Search 2) Filter 3) Verify source 4) Assess confidence.
OUTPUT FORMAT:
'[Source]: [What] — [Why it matters]
Confidence: [HIGH: verified primary source | MEDIUM: secondary source | LOW: rumor/speculation]'
RULE: Only share HIGH or MEDIUM confidence. LOW → silence.
VERIFY: □ <24h □ Confidence assessed □ Source cited.
```

## Recommendations for PROMPTS Array

### Priority 1: Add Examples to High-Frequency Prompts
- SCOUT:AI, SCOUT:MARKET, ACTION:DISCOVERY
- Include 1 GOOD and 1 BAD example in each

### Priority 2: Add Self-Critique Step
- Insert "SELF-CRITIQUE: Before output, ask: [criteria]" 
- Most useful for RESEARCH and CREATE prompts

### Priority 3: Add Confidence Calibration
- For RESEARCH prompts: require confidence levels
- For SCOUT prompts: threshold (only share HIGH/MEDIUM)

### Priority 4: Shorten Verbose Prompts
- Current prompts are ~150-250 words each
- Target: 80-120 words with same information density
- Use structured shorthand (already doing well)

## Metrics to Track
1. Surface rate (% of prompts that produce output)
2. Engagement rate (% of surfaces that get response)
3. Quality score (subjective, from feedback-log)
4. False positive rate (surfaces that shouldn't have been)

## Implementation Plan
1. Test Variation B (few-shot) on 3 prompts for 1 week
2. Measure engagement vs. current prompts
3. If improved: roll out to all SCOUT prompts
4. Then test self-critique on RESEARCH prompts
