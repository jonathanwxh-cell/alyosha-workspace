# Prompt Engineering Research — 2026-02-01 v2

## Source Analysis

### High-Revenue AI Products ($50M+ ARR)

**Bolt.new ($50M ARR in 5 months)**
- System prompt is "one of the keys to success"
- Extremely detailed error handling from real testing
- Long lists with ALL CAPS for emphasis
- Code-like formatting

**Cluely ($6M ARR in 2 months)**
- Uses brackets like code `[instruction]`
- Explicit NEVER and ALWAYS lists
- Display/format instructions
- If/then edge cases

### Key Patterns from Research

1. **Longer > Shorter** (for complex tasks)
   - Production prompts are much longer than "tips" suggest
   - Every instruction is a product decision

2. **Code-like Structure**
   - `[brackets]` for variables/categories
   - `###` section dividers
   - Explicit formatting

3. **Edge Case Handling**
   - "If X happens, do Y"
   - Specific error recovery paths
   - Learned from real failures

4. **Explicit Constraints**
   - ALWAYS: [list]
   - NEVER: [list]
   - Not just "don't do X" but "instead do Y"

5. **Verification Built-In**
   - Self-check before output
   - Explicit success criteria
   - Binary outcomes when possible

---

## Current Prompt Pattern (v2.1)

```
[DOMAIN] [TIME]: [VERB] [OBJECT]. 
MUST: [CONSTRAINT]. 
Output: [FORMAT]. 
Verify: [CHECK]. 
Success: [BINARY]. 
If blocked: [FALLBACK]. 
Don't: [ANTI].
```

**Strengths:**
- Action-oriented verbs
- Time budgets
- Binary success criteria
- Fallback paths

**Gaps:**
- Could use more specific edge cases
- ALWAYS/NEVER lists not explicit
- Could benefit from code-like formatting
- Error handling is generic ("if blocked")

---

## Proposed Improvements (v2.2)

### 1. Add ALWAYS/NEVER blocks to meta-prompt

```
### ALWAYS
- Start with the action verb
- Include time estimate in first 5 words
- Declare intent before acting
- Log outcome to appropriate file

### NEVER
- Describe what could be done (DO it)
- Send output that fails pre-flight
- Hedge with "might be interesting"
- Report issues without attempting fix
```

### 2. More specific edge cases

Before:
```
If blocked: note search gap.
```

After:
```
If blocked:
  - API rate limit → wait 60s, retry once
  - No results → try alternative search terms
  - Tool error → log to capability-wishlist.md
  - Ambiguous task → make reasonable choice + note assumption
```

### 3. Code-like variables for dynamic content

```
[TASK: AI Discovery]
[TIME_BUDGET: 10 min]
[OUTPUT_PATH: reports/ai-discovery-{date}.md]
[DELIVERY: telegram if notable, silent if not]
```

---

## Test: Improved AI Discovery Prompt

### Before (v2.1)
```
AI DISCOVERY [10 min]: Find ONE notable AI development from last 48h. 
MUST: Transform into artifact (reports/ brief, cron alert, OR tool). 
Output: file path + 2-sentence summary. 
Verify: Artifact exists AND is useful. 
Success: deliverable created AND shared. 
If blocked: log to capability-wishlist.md. 
Don't: describe without creating OR share unfinished work.
```

### After (v2.2)
```
[TASK: AI DISCOVERY] [TIME: 10 min]

OBJECTIVE: Find ONE notable AI development from last 48h and CREATE an artifact.

ALWAYS:
- Search 2+ sources before concluding "nothing notable"
- Transform finding into deliverable (report, alert, or tool)
- Verify artifact exists before claiming success

NEVER:
- Describe what you could create (create it)
- Surface news older than 48h
- Share half-finished work

EDGE CASES:
- If search rate-limited → use cached/alternate source
- If finding is minor → save to memory/interesting-but-minor.md, don't surface
- If finding connects to existing topic → update topic-graph.json

OUTPUT: {reports/ai-discovery-{date}.md} + 2-sentence summary to Jon
SUCCESS: File exists AND contains insight AND shared
FAILURE: Log gap to capability-wishlist.md with specific barrier
```

---

## Implementation

Will update ONE prompt in curiosity-daemon.sh to test v2.2 pattern.
Track engagement on outputs from improved vs standard prompts over next week.
