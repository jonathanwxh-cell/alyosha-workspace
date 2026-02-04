# Prompt Engineering Research — 2026-02-04

## Sources

1. **Comet "Meta Prompting"** (2026)
   - Structure over content: Teach HOW to think, not just WHAT to do
   - APE (Automatic Prompt Engineer): Generate candidates, evaluate, iterate
   - LCP (Learning from Contrastive Prompts): Compare SUCCESS vs FAILURE explicitly

2. **Comet "Prompt Engineering for Agentic AI"** (2026)
   - Game of 24 example: 4% → 74% success with structured reasoning (18x improvement!)
   - Key insight: "How you structure reasoning matters more than which model"
   - Agent anatomy: Planning + Memory + Tool Use
   - Few-shot = in-context learning, not just format demonstration

3. **2026 Guide to Prompt Engineering** (AI Corner)
   - 6 elements: Role, Goal, Context, Format, Examples, Constraints
   - Context windows now 1M-10M tokens
   - Most people "prompt like it's 2024" - leaving 90% capability on table

4. **IBM 2026 Guide**
   - Chain of Thought, Tree of Thoughts, ReAct, Self-Consistency
   - Reasoning architectures > clever wording

## Key Patterns

### 1. Meta-Prompts (Structure Over Content)

**Traditional prompt:**
> "Categorize this article as Technology, Business, or Health."

**Meta-prompt:**
> "To categorize ANY article: 1) Identify primary subject, 2) Apply criteria [X], 3) If spans multiple, select majority, 4) Output with justification."

The meta-prompt creates a reusable reasoning template.

### 2. Contrastive Learning (LCP)

Instead of just optimizing for higher scores, explicitly compare:
- What did SUCCESS prompts have that FAILURE prompts lacked?
- Extract pattern: "For [task], ALWAYS [success pattern], NEVER [failure pattern]"

### 3. Cognitive Architectures

| Architecture | Best For | Pattern |
|-------------|----------|---------|
| Chain of Thought | Linear problems | Step 1 → Step 2 → ... → Answer |
| Tree of Thoughts | Exploration | Branch → Evaluate → Backtrack if needed |
| ReAct | Tool use | Thought → Action → Observation loop |
| Self-Consistency | High-stakes | Multiple paths → Majority vote |

### 4. APE (Automatic Prompt Engineer)

1. Generate multiple candidate prompts
2. Evaluate each against test cases
3. Use best performers to create variations
4. Iterate until convergence

## Implementation

Added new `meta_prompting` category to curiosity-engine.py with 4 prompts:

1. **REASONING FRAMEWORK BUILDER** [w=1.5]
   - Create reusable thinking templates for task categories
   - Includes contrastive SUCCESS vs FAILURE examples

2. **CONTRASTIVE PROMPT LEARNING** [w=1.4]
   - Learn from past successes vs failures
   - Extract actionable rules

3. **COGNITIVE ARCHITECTURE PRACTICE** [w=1.3]
   - Deliberately practice CoT, ToT, ReAct, Self-Consistency
   - Compare architectures for fit

4. **PROMPT EVOLUTION SESSION** [w=1.2]
   - Improve underperforming prompts systematically
   - Apply APE principles

## Action Items

- [x] Add meta_prompting category to curiosity-engine.py
- [ ] Run CONTRASTIVE PROMPT LEARNING on reflection history
- [ ] Build reasoning-frameworks/ library for common task types
- [ ] Track which cognitive architecture works best for which task

---

*Research completed: 2026-02-04 06:20 SGT*
