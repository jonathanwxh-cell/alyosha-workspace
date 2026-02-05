# Structured Exploration Template (Reflexion-Based)

Based on Shinn et al. (2023) "Reflexion: Language Agents with Verbal Reinforcement Learning"

---

## The Pattern

**Key insight:** Basic reflection isn't grounded. Reflexion forces *external grounding* via citations, explicit gaps, and structured critique.

---

## 5-Step Exploration Loop

### 1. RECALL (Before Starting)
```bash
python3 scripts/reflexion.py query "<topic keywords>"
```
- What did I learn last time on similar topics?
- What mistakes should I avoid?
- What worked well?

### 2. HYPOTHESIZE (Before Searching)
State explicitly:
- "I expect to find X because Y"
- "My current belief about this topic is Z"

This creates falsifiability — you can update beliefs based on evidence.

### 3. SEARCH + CITE (Grounded Research)
For each source:
- [ ] URL/title
- [ ] Key claim (1 sentence)
- [ ] How it supports/contradicts hypothesis

**Minimum:** 2-3 sources with explicit citations.

### 4. CRITIQUE (Self-Reflection)
Ask:
- What's **missing** from my findings?
- What's **superfluous** (noise, not signal)?
- What would **change my view**?
- Confidence level: Low / Medium / High

### 5. SYNTHESIZE + LOG
Output format:
```
**Insight:** [One sentence finding]
**Evidence:** [Citation + key data point]
**Gap:** [What I still don't know]
**Confidence:** [Low/Medium/High]
**Question:** [Follow-up to explore next]
```

Then log:
```bash
python3 scripts/reflexion.py add
# Enter: task, outcome, reflection, lesson, would_repeat
```

---

## Why This Works

| Basic Reflection | Reflexion (Grounded) |
|------------------|----------------------|
| "I should do better" | "Source X shows Y, contradicting my assumption Z" |
| Vague self-critique | Explicit citations + gaps |
| No memory | Queries past reflections |
| One-shot | Iterative with external feedback |

---

## Anti-Patterns

❌ Searching without hypothesis (unfocused)
❌ Summarizing without opinion (no synthesis)
❌ Skipping the RECALL step (repeating mistakes)
❌ High confidence without evidence
❌ Not logging reflections (losing learnings)

---

*Implement this loop for deeper, more grounded exploration.*
