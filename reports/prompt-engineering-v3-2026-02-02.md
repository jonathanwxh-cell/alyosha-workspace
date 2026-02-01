# Prompt Engineering Research: v3.0 Improvements

*Research Date: 2026-02-02*

---

## Research Sources

1. **Lakera** - "Clear structure and context > clever wording"
2. **PromptingGuide.ai** - ReAct, planning with feedback, memory integration
3. **Mercity.ai** - ReAct deconstructs problems into well-structured format

---

## Current Pattern (v2.1)

```
[DOMAIN] [TIME]: [VERB] [OBJECT]. MUST: [CONSTRAINT]. Output: [FORMAT]. 
Verify: [CHECK]. Success: [BINARY]. If blocked: [FALLBACK]. Don't: [ANTI].
```

**Issues identified:**
- No explicit context loading
- Steps not decomposed
- Verification is single-line (should be checklist)
- Success criteria often vague
- Dense, hard to parse quickly

---

## New Pattern (v3.0)

```
[CATEGORY] [NAME] (v3.0)

CONTEXT: [files to read before starting]
GOAL: [one action-verb sentence]
STEPS:
  1. [specific action]
  2. [specific action]
  ...
OUTPUT: [exact format with example]
VERIFY: 
  □ [check 1]
  □ [check 2]
IF_BLOCKED: [fallback action]
NEVER: [anti-pattern]
```

**Key improvements:**
1. **CONTEXT** - Explicit file reads (aligns with daemon research)
2. **STEPS** - Decomposed actions (ReAct-inspired)
3. **VERIFY** - Checklist format (easier to self-check)
4. **Cleaner structure** - Easier to parse at runtime

---

## Example Transformation

### Before (v2.1):
```
"DEEP DIVE [20 min]: Pick topic from Jon's domains (markets, AI, geopolitics). 
MUST: Research 3+ sources AND synthesize (not aggregate). Output: reports/[topic]-deep-dive-[date].md 
with TL;DR (2 sent), findings (5-7 bullets), sources, next actions. Verify: Insights are non-obvious. 
Success: report created + 100-word summary sent. If blocked: save partial + note gaps. 
Don't: regurgitate—illuminate."
```

### After (v3.0):
```
RESEARCH: DEEP_DIVE (v3.0)

CONTEXT: memory/goals.json, memory/topic-graph.json
GOAL: Research and synthesize one topic from Jon's domains into actionable insight.
STEPS:
  1. Pick topic (markets/AI/geopolitics) based on goals or gaps
  2. Search 3+ sources, cross-reference claims
  3. Synthesize (don't aggregate) — find the non-obvious thread
  4. Write report with: TL;DR (2 sent), findings (5-7 bullets), sources
  5. Draft 100-word Telegram summary
OUTPUT: reports/[topic]-deep-dive-[date].md + message to Jon
VERIFY:
  □ Contains insight not obvious from headlines?
  □ Investment angle included?
  □ Summary standalone (doesn't require reading report)?
IF_BLOCKED: Save partial draft, note research gaps
NEVER: Regurgitate without synthesis, surface without actionable angle
```

---

## Prompt Categories to Update

| Category | Count | Priority | Notes |
|----------|-------|----------|-------|
| Quick Scouts | 3 | Medium | Already lean, minor tweaks |
| Action Tasks | 5 | High | Need context loading |
| Deep Dives | 3 | High | Need step decomposition |
| Creative | 5 | Low | Intentionally loose |
| Maintenance | 6 | Medium | Add verification checklists |
| Curation | 3 | Medium | Need personalization hooks |
| Experimental | 6 | High | Need clearer success criteria |
| Video | 3 | Low | Rarely used |

---

## Implementation: Top 5 Prompts to Upgrade

### 1. DEEP_DIVE → v3.0 ✓
(See example above)

### 2. AI_DISCOVERY → v3.0
```
RESEARCH: AI_DISCOVERY (v3.0)

CONTEXT: memory/topics-tracking.json
GOAL: Find and transform one notable AI development into a useful artifact.
STEPS:
  1. Search for AI news from last 48h
  2. Filter for: genuinely new, relevant to Jon's interests
  3. Choose ONE worth surfacing
  4. Create artifact: report, alert, or tool
  5. Share with context
OUTPUT: File path + 2-sentence summary to Jon
VERIFY:
  □ Development is <48h old?
  □ Artifact exists and is complete?
  □ Jon would find this useful?
IF_BLOCKED: Log to capability-wishlist.md
NEVER: Describe without creating, share half-finished work
```

### 3. THESIS → v3.0
```
RESEARCH: THESIS (v3.0)

CONTEXT: memory/mental-models.md, recent deep-dives
GOAL: Build a testable mini investment thesis on an emerging trend.
STEPS:
  1. Identify trend from recent research or gaps
  2. Formulate claim (specific, falsifiable)
  3. Gather 3+ data points as evidence
  4. Steel-man counter-arguments
  5. Define "I'm wrong if..." criteria
OUTPUT: reports/thesis-[topic].md
VERIFY:
  □ Claim is specific enough to be proven wrong?
  □ Counter-arguments addressed honestly?
  □ Evidence from multiple sources?
IF_BLOCKED: Note research gap, save partial
NEVER: State opinion without evidence, ignore counter-arguments
```

### 4. FEEDBACK_REVIEW → v3.0
```
MAINTENANCE: FEEDBACK_REVIEW (v3.0)

CONTEXT: memory/feedback-log.jsonl, memory/what-works.md
GOAL: Extract one actionable insight from feedback data and implement it.
STEPS:
  1. Load last 20 feedback entries
  2. Calculate engagement by category
  3. Identify one pattern (positive or negative)
  4. Implement one small change to HEARTBEAT.md or prompts
  5. Log change with reasoning
OUTPUT: Updated file + entry in self-improvement-log.md
VERIFY:
  □ Change is evidence-based (not intuition)?
  □ Change is small and reversible?
  □ Logged with clear reasoning?
IF_BLOCKED: Note data gap
NEVER: Guess without data, make large changes
```

### 5. CAPABILITY_PROBE → v3.0
```
EXPERIMENTAL: CAPABILITY_PROBE (v3.0)

CONTEXT: memory/capability-wishlist.md
GOAL: Test one untried capability and document the result.
STEPS:
  1. Pick something from wishlist OR identify new gap
  2. Attempt the capability (embrace failure)
  3. Document: what worked, what didn't, why
  4. If successful, add to TOOLS.md
  5. If failed, add to wishlist with notes
OUTPUT: "Tried: [X]. Result: [Y]. Learned: [Z]"
VERIFY:
  □ Actually attempted (not just researched)?
  □ Learned something new?
  □ Documented regardless of outcome?
IF_BLOCKED: Document the block itself
NEVER: Avoid risk, hide failures, claim success without proof
```

---

## META_PROMPT Updates

Add to META_PROMPT v2.4:

```
### CONTEXT LOADING (New)
Before executing, check if prompt has CONTEXT section.
If yes, read those files first and incorporate relevant info.

### STEP EXECUTION (Enhanced)
Execute steps in order. After each step:
- Confirm step completed
- Note any blockers
- Adjust subsequent steps if needed
```

---

## Testing Plan

1. Run 3 prompts with v2.1 pattern, log results
2. Run same 3 prompts with v3.0 pattern, log results
3. Compare: output quality, completion rate, time taken
4. Iterate based on findings

---

## Next Steps

1. Update curiosity-daemon.sh with v3.0 prompts (top 5 first)
2. Update META_PROMPT to v2.4
3. Test in next daemon run
4. Review results in weekly self-review

