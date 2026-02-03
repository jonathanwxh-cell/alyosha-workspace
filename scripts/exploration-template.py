#!/usr/bin/env python3
"""
Exploration Template Generator

Generates structured exploration prompts using ReAct + Reflexion patterns.
Designed to improve autonomous curiosity daemon effectiveness.

Usage:
    python3 scripts/exploration-template.py                    # Generate template
    python3 scripts/exploration-template.py --topic "AI news"  # With specific topic
    python3 scripts/exploration-template.py --pattern react    # Specific pattern
    python3 scripts/exploration-template.py --pattern tot      # Tree of Thoughts
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# =============================================================================
# PATTERN TEMPLATES
# =============================================================================

REACT_TEMPLATE = """
## ReAct Exploration Protocol

**Task:** {task}
**Time budget:** {time_budget}
**Success criteria:** {success_criteria}

---

### Phase 1: Initial Reasoning
**Thought 1:** What do I already know about this? What's my hypothesis?
[Write your initial reasoning here]

**Action 1:** [Search/Read/Query] — What's my first information-gathering step?
[Execute the action]

**Observation 1:** What did I find? Does it confirm or challenge my hypothesis?
[Record what you learned]

---

### Phase 2: Deepen or Pivot
**Thought 2:** Based on observation, should I go deeper or change direction?
[Reason about next step]

**Action 2:** [Specific action based on thought]
[Execute]

**Observation 2:** [Record findings]

---

### Phase 3: Synthesize
**Thought 3:** What's the key insight? Is it worth sharing?
[Synthesize findings]

**Action 3:** Create artifact — [brief/tool/cron/file]
[Build something tangible]

**Final Observation:** Does artifact meet success criteria?

---

### Self-Evaluation
- [ ] Success criteria met? [YES/PARTIAL/NO]
- [ ] Created tangible artifact?
- [ ] Insight is non-obvious?
- [ ] Worth Jon's attention?

**Reflection (if PARTIAL/NO):**
What went wrong? What would I do differently?
[Log to memory/reflections.jsonl]
"""

TOT_TEMPLATE = """
## Tree of Thoughts Exploration

**Problem:** {task}
**Time budget:** {time_budget}

---

### Step 1: Generate Multiple Approaches

**Approach A:** {approach_a_hint}
- Initial thought: [How would this approach work?]
- Feasibility: [sure/maybe/impossible]

**Approach B:** {approach_b_hint}
- Initial thought: [How would this approach work?]
- Feasibility: [sure/maybe/impossible]

**Approach C:** {approach_c_hint}
- Initial thought: [How would this approach work?]
- Feasibility: [sure/maybe/impossible]

---

### Step 2: Evaluate & Select

Which approach is most promising? Why?
[Select the "sure" or most promising "maybe"]

**Selected approach:** [A/B/C]
**Rationale:** [Why this one?]

---

### Step 3: Execute Selected Approach

[Follow ReAct pattern for selected approach]

**Thought:** [Reasoning]
**Action:** [Execution]
**Observation:** [Result]

---

### Step 4: Backtrack if Needed

If stuck or approach fails:
1. Note what went wrong
2. Return to Step 2
3. Try next most promising approach

**Backtrack log:** [If applicable]

---

### Step 5: Synthesize

**Final output:** [Artifact or insight]
**Confidence:** [HIGH/MEDIUM/LOW]
**Alternative approaches not tried:** [For future reference]
"""

REFLEXION_TEMPLATE = """
## Reflexion Loop: Learn from Experience

**Task:** {task}
**Episode:** {episode_num}
**Prior reflections:** {prior_reflections}

---

### Actor Phase

**Plan:** Based on task and prior reflections, what's my approach?
[State your plan in 1-2 sentences]

**Execution:**
[Execute the plan using ReAct or direct action]

**Trajectory summary:**
- Actions taken: [list]
- Observations: [key findings]
- Output produced: [artifact]

---

### Evaluator Phase

**Score:** [1-10]
**Criteria check:**
- [ ] Task completed?
- [ ] Output quality acceptable?
- [ ] Time budget respected?
- [ ] No repeated mistakes from prior reflections?

---

### Self-Reflection Phase (if score < 8)

**What went wrong?**
[Specific failure mode]

**Root cause:**
[Why did this happen?]

**What would I do differently?**
[Concrete change for next attempt]

**Reflection to store:**
```json
{{
  "timestamp": "{timestamp}",
  "task": "{task_short}",
  "outcome": "[success/partial/failure]",
  "reflection": "[what happened]",
  "lesson": "[key takeaway for future]"
}}
```

---

### Memory Update

Append reflection to: `memory/reflections.jsonl`
Update relevant files if insight is durable.
"""

HYBRID_TEMPLATE = """
## Hybrid Exploration: ReAct + Reflexion

**Task:** {task}
**Time:** {time_budget}
**Success:** {success_criteria}

---

### Pre-Flight Check (Reflexion Memory)

```bash
python3 scripts/query-reflections.py "{query_term}"
```

**Relevant past lessons:**
[List any applicable lessons from reflections]

**Adjusted approach based on lessons:**
[How will past experience change your approach?]

---

### Exploration (ReAct Loop)

**Cycle 1:**
- Thought: [Initial reasoning]
- Action: [First step]
- Observation: [What you found]

**Cycle 2:**
- Thought: [Adjusted reasoning]
- Action: [Next step]
- Observation: [Findings]

**Cycle 3 (if needed):**
- Thought: [Synthesis reasoning]
- Action: [Create artifact]
- Observation: [Verify artifact]

---

### Post-Flight Reflection

**Self-Assessment:**
- Success criteria met? [YES/PARTIAL/NO]
- Artifact created? [YES/NO]
- Time budget respected? [YES/NO]

**If not fully successful:**
```bash
echo '{{"timestamp":"{timestamp}","task":"{task_short}","outcome":"[result]","reflection":"[what happened]","lesson":"[takeaway]"}}' >> memory/reflections.jsonl
```

**If successful:**
- Note what worked for future reference
- Update relevant memory files if insight is durable

---

### Output

[Your final artifact or insight here]
"""

# =============================================================================
# Generator Functions
# =============================================================================

def generate_react(task, time_budget="15 min", success_criteria="tangible artifact created"):
    return REACT_TEMPLATE.format(
        task=task,
        time_budget=time_budget,
        success_criteria=success_criteria
    )

def generate_tot(task, time_budget="20 min"):
    return TOT_TEMPLATE.format(
        task=task,
        time_budget=time_budget,
        approach_a_hint="Direct search approach",
        approach_b_hint="Lateral/creative approach",
        approach_c_hint="Build something approach"
    )

def generate_reflexion(task, episode_num=1, prior_reflections="None"):
    return REFLEXION_TEMPLATE.format(
        task=task,
        episode_num=episode_num,
        prior_reflections=prior_reflections,
        timestamp=datetime.now().isoformat(),
        task_short=task[:50]
    )

def generate_hybrid(task, time_budget="15 min", success_criteria="artifact + insight"):
    return HYBRID_TEMPLATE.format(
        task=task,
        time_budget=time_budget,
        success_criteria=success_criteria,
        query_term=task.split()[0].lower(),
        timestamp=datetime.now().isoformat(),
        task_short=task[:50]
    )

def main():
    args = sys.argv[1:]
    
    # Defaults
    pattern = "hybrid"
    topic = "Find something interesting and create an artifact"
    
    # Parse args
    if "--pattern" in args:
        idx = args.index("--pattern")
        if idx + 1 < len(args):
            pattern = args[idx + 1]
    
    if "--topic" in args:
        idx = args.index("--topic")
        if idx + 1 < len(args):
            topic = args[idx + 1]
    
    if "--help" in args:
        print(__doc__)
        return
    
    # Generate
    if pattern == "react":
        output = generate_react(topic)
    elif pattern == "tot":
        output = generate_tot(topic)
    elif pattern == "reflexion":
        output = generate_reflexion(topic)
    else:
        output = generate_hybrid(topic)
    
    print(output)

if __name__ == "__main__":
    main()
