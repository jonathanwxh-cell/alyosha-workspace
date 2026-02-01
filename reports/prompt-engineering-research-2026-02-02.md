# Prompt Engineering Research: Action-Oriented Agent Prompts

*Date: 2026-02-02*
*Purpose: Improve curiosity-daemon.sh PROMPTS array*

## Research Sources

1. **Lakera Guide (2026)** - Comprehensive prompt types and structures
2. **PromptingGuide.ai** - ReAct and Reflexion frameworks
3. **Aakash G's Newsletter** - Production system prompts from Bolt ($50M ARR), Cluely ($6M ARR)

---

## Key Findings

### 1. What Makes Action-Oriented Prompts Effective

| Pattern | Why It Works | Example |
|---------|--------------|---------|
| **Verb-first** | Forces immediate action, no hedging | "RESEARCH x" not "You could research x" |
| **Explicit intent** | Reduces ambiguity, enables verification | "GOAL: Find ONE notable development" |
| **Structured steps** | Breaks complex tasks, enables partial progress | "STEPS: 1) Search 2) Filter 3) Decide" |
| **Success criteria** | Agent knows when to stop | "OUTPUT: 2-sentence summary OR 'nothing notable'" |
| **Blocking strategy** | Prevents infinite loops | "IF_BLOCKED: Note gap, try alternative" |
| **Never list** | Prevents common failure modes | "NEVER: Hedge with 'might be interesting'" |

### 2. Production Patterns (from $50M+ ARR AI Products)

**Bolt.new system prompt patterns:**
- Code-like formatting with brackets
- CAPS for emphasis on rules
- Detailed error handling for known edge cases
- Long, explicit instruction lists

**Cluely system prompt patterns:**
- Never/always constraint lists
- Display instructions (format control)
- If/then edge case handling
- Shorter, more structured

**Common to both:**
- Extremely explicit about what NOT to do
- Clear output format expectations
- Anticipate and handle failure modes

### 3. ReAct Framework (Yao et al., 2022)

Loop: **Thought → Action → Observation → Thought → ...**

- Generate reasoning traces (why am I doing this?)
- Take action (tool use, search, etc.)
- Observe result
- Adjust reasoning based on observation

**Best for:** Knowledge-intensive tasks, decision-making, multi-step reasoning

### 4. Reflexion Framework (Shinn et al., 2023)

Components:
1. **Actor** - Generates actions (uses CoT/ReAct)
2. **Evaluator** - Scores outputs
3. **Self-Reflection** - Generates verbal cues for improvement

**Key insight:** Store reflections in memory for future trials. The agent learns from explicit verbal feedback, not just rewards.

---

## Analysis of Current Prompts (v3.0)

### Strengths
- Good structure: CONTEXT → GOAL → STEPS → OUTPUT → VERIFY → IF_BLOCKED → NEVER
- Action-oriented language
- Clear categories (SCOUT, ACTION, RESEARCH, etc.)
- Meta-prompt with pre-flight check

### Weaknesses
1. **Some prompts too dense** - Wall of text reduces clarity
2. **Inconsistent structure** - Old v2 prompts mixed with v3
3. **Vague success criteria** - "something worth trying" vs measurable outcome
4. **Missing thinking scaffolds** - Complex tasks need explicit reasoning steps
5. **Blocking strategies generic** - "Note gap" doesn't help recovery
6. **Time estimates inaccurate** - 10 min tasks often take 20+

### Specific Issues Found

```
❌ "Success: Jon would click at least one"
   → Not measurable by agent

✅ "VERIFY: □ Insight novel? □ Source credible? □ <48h old?"
   → Checklist the agent can actually verify
```

```
❌ "If blocked: HEARTBEAT_OK"
   → Gives up too easily

✅ "IF_BLOCKED: 1) Try alternative source 2) Note gap in capability-wishlist.md 3) Skip only if 2+ approaches failed"
   → Structured recovery
```

---

## Proposed Improvements

### 1. Standardize on Compact v4 Structure

```
[CATEGORY]: [NAME] (v4) | 
GOAL: [Single sentence, measurable]
CONTEXT: [Files to load first]
STEPS: 1) ... 2) ... 3) ...
OUTPUT: [Exact format or "silence"]
VERIFY: □ [Checklist items]
RECOVER: [Specific recovery strategy]
NEVER: [Top 2-3 failure modes]
```

### 2. Add Thinking Scaffolds for Complex Tasks

For RESEARCH prompts, add:
```
THINK: Before acting, write 2-3 sentences on approach + potential blockers
```

### 3. Improve Blocking/Recovery Strategies

Instead of generic "note gap":
- **Search failed:** Try 2 alternative queries, different sources
- **API error:** Wait 60s, retry once, log if persistent
- **No results:** Rephrase question, broaden scope, document null result
- **Ambiguous task:** State assumption, proceed, flag for review

### 4. Make Success Criteria Agent-Verifiable

Replace subjective ("Jon would like") with objective:
- □ Contains specific data/numbers?
- □ Source cited?
- □ <48h old?
- □ Non-obvious insight (not first Google result)?
- □ Artifact created (not just text)?

---

## Test Variations

### Original SCOUT: AI_NEWS
```
"SCOUT: AI_NEWS (v3.0) | GOAL: Find ONE notable AI development from last 24h. STEPS: 1) Search AI news 2) Filter for genuinely new + relevant 3) Decide: surface OR skip. OUTPUT: 2-sentence summary OR 'nothing notable'. VERIFY: □ <24h old? □ Jon would click? IF_BLOCKED: Note search gap. NEVER: Hedge with 'might be interesting', surface old news."
```

### Improved v4.0
```
"SCOUT: AI_NEWS (v4) | GOAL: Surface ONE AI development <24h old that changes how we think about something. STEPS: 1) Search 'AI news today' + 'AI breakthrough' 2) Filter: genuinely new (not follow-up coverage) + relevant (AI/markets/tech Jon tracks) 3) Verify source credibility 4) Decide: share OR skip. OUTPUT: '[Source] [Headline]: [Why it matters in 1 sentence]' OR silence. VERIFY: □ <24h old □ Primary source cited □ Not already covered □ Changes mental model. RECOVER: If search fails → try HackerNews, ArXiv, X/AI accounts. If nothing notable → silence (not 'nothing found'). NEVER: Surface incremental updates, hedge with 'might be', editorialize without insight."
```

### Test: Shorter "Micro-prompt" Variation
```
"AI_NEWS: Find 1 AI development <24h. If notable: '[Source]: [Why it matters]'. If not: silence. Check: novel? credible? actionable?"
```

---

## Implementation Plan

1. ✅ Document research findings (this file)
2. Update PROMPTS array with v4 structure
3. Test 3 prompts via manual execution
4. Log results to self-improvement-log.md
5. Iterate based on outcomes

---

## References

- Yao et al. (2022) - ReAct: Synergizing Reasoning and Acting in Language Models
- Shinn et al. (2023) - Reflexion: Language Agents with Verbal Reinforcement Learning
- Lakera Prompt Engineering Guide (2026)
- Bolt.new system prompt (GitHub)
- Cluely system prompt (leaked/analyzed)
