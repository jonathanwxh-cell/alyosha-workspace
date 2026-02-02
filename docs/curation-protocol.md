# Content Curation Protocol

*Not just recommend — consume, analyze, model, visualize, report.*

---

## The Old Way (DON'T DO)
```
Find content → List it → "Want me to pull excerpts?"
```

## The New Way (DO THIS)
```
Find content → Read it → Analyze with mental models → 
Extract insights → Create visual → Report findings → 
Log for future reference
```

---

## Curation Workflow

### 1. FIND (light touch)
- Search for quality sources (not just recent)
- Filter for depth over breadth
- 3-5 pieces max per curation

### 2. CONSUME (actually read it)
- Fetch full content
- Note key claims, data points, arguments
- Flag surprising or contrarian points

### 3. ANALYZE (apply mental models)

**Models to apply:**
| Model | Question |
|-------|----------|
| Second-order effects | What happens next? And after that? |
| Competitive dynamics | Who wins, who loses, what changes? |
| Information asymmetry | Who knows what? What's hidden? |
| Talebian lens | Fragility? Antifragility? Black swans? |
| Investment angle | How does this affect markets/positions? |

### 4. VISUALIZE (make it scannable)
- Tables for comparisons
- Matrices for probability × impact
- Timelines for sequences
- Decision trees for branching outcomes

**Tools:**
- Markdown tables (quick, in-message)
- Excel/CSV for data (save to workspace)
- ASCII diagrams for flows
- Charts via Python if needed

### 5. REPORT (deliver insights)

**Format:**
```markdown
## Executive Summary
[2-3 sentences: what is this, why it matters]

## Key Findings Matrix
[Table: trend, probability, impact, relevance]

## Mental Model Analysis
[Apply 2-3 models, show reasoning]

## Actionable Insights
[What to do with this information]

## Confidence Assessment
[Rate claims, explain reasoning]
```

### 6. FILE (for future reference)
- Save analysis to `memory/research/[topic].md`
- Update `curiosities.json` if opens new thread
- Log to `reflections.jsonl` if lesson learned

---

## Self-Improvement Integration

When curating:
1. **Track engagement** — Did Jon react/reply? Log to feedback-log.jsonl
2. **Calibrate confidence** — Were my high-confidence picks actually good?
3. **Adjust sources** — Which sources consistently deliver value?
4. **Update mental models** — Did analysis hold up? What did I miss?

---

## Example Output

**BAD:**
> "Here are 5 articles on AI geopolitics. Want me to summarize?"

**GOOD:**
> "Analyzed Atlantic Council's AI geopolitics piece. Key finding: AI poisoning has ~2yr lag — campaigns from 2024 hitting now. Second-order effect: 'clean data' becomes scarce resource. Watch: data provenance startups. Full analysis in memory/research/."

---

## Trigger Phrases

When Jon says:
- "Find content on X" → Full protocol
- "What should I read about X" → Full protocol
- "Any good articles on X" → Full protocol
- "Quick links on X" → Light touch OK (but offer analysis)

---

*Remember: Curate like an analyst, not a librarian.*
