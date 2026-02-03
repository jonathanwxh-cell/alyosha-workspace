# Agent Reasoning Patterns
*Research compilation for autonomous exploration improvement*

---

## 1. ReAct (Reasoning + Acting)

**Paper:** Yao et al., 2022 — "Synergizing Reasoning and Acting in Language Models"

### Core Loop
```
Thought: [Reason about current state, plan next step]
Action: [Execute action, call tool, search]
Observation: [Result from environment]
... repeat until task complete ...
Answer: [Final output]
```

### Why It Works
- **Interpretability:** Explicit reasoning makes decisions transparent
- **Dynamic planning:** Can adjust strategy based on observations
- **Reduces hallucination:** Grounds reasoning in actual observations
- **Error recovery:** Can detect and correct mistakes mid-task

### When to Use
- Information retrieval tasks
- Multi-step problem solving
- Tasks requiring external tool use
- When you need audit trail of reasoning

### Implementation
```python
def react_loop(task, tools, max_iterations=5):
    context = []
    for i in range(max_iterations):
        # 1. Reasoning step
        thought = llm(f"Task: {task}\nContext: {context}\nThought:")
        
        # 2. Action step  
        action = llm(f"Based on thought: {thought}\nAction:")
        
        # 3. Execute and observe
        observation = execute(action, tools)
        
        context.append({"thought": thought, "action": action, "obs": observation})
        
        if is_complete(observation):
            return synthesize_answer(context)
    
    return "Max iterations reached"
```

---

## 2. Tree of Thoughts (ToT)

**Paper:** Yao et al., 2023 — "Deliberate Problem Solving with Large Language Models"

### Core Idea
Maintain a **tree** of intermediate thoughts. Explore multiple reasoning paths, evaluate each, and use search algorithms (BFS/DFS) to find the best solution.

### Structure
```
         [Problem]
        /    |    \
    [T1]   [T2]   [T3]     ← Generate multiple thoughts
     |      |      |
   [eval] [eval] [eval]    ← Self-evaluate each (sure/maybe/impossible)
     |      |
   [T1a]  [T2a]            ← Expand promising branches
    ...
```

### Key Operations
1. **Thought Generation:** Propose multiple next steps
2. **Thought Evaluation:** Rate each as sure/maybe/impossible
3. **Search:** BFS or DFS to explore the tree
4. **Backtracking:** Abandon dead ends, try alternatives

### When to Use
- Complex reasoning with multiple valid paths
- Problems requiring strategic lookahead
- When initial approach might be wrong
- Puzzles, planning, creative tasks

### Simplified Prompt Version
```
Imagine three different experts answering this question.
All experts will write down 1 step of their thinking, then share with group.
Then all experts go on to the next step, etc.
If any expert realizes they're wrong at any point, they leave.
The question is: [TASK]
```

---

## 3. Reflexion

**Paper:** Shinn et al., 2023 — "Language Agents with Verbal Reinforcement Learning"

### Core Loop
```
Episode 1:
  Actor: Generate trajectory (attempt task)
  Evaluator: Score the output
  Self-Reflection: "What went wrong? What would I do differently?"
  Memory: Store reflection

Episode 2:
  Actor: Generate trajectory WITH reflection memory as context
  ... repeat until success or max episodes ...
```

### Three Components
1. **Actor:** Generates actions (can use CoT or ReAct)
2. **Evaluator:** Scores outputs (LLM or heuristic)
3. **Self-Reflection Model:** Generates verbal feedback for improvement

### Why It Works
- Converts scalar feedback into rich linguistic feedback
- Builds explicit episodic memory
- Enables rapid learning from mistakes
- No model fine-tuning required

### When to Use
- Tasks requiring trial and error
- When traditional RL is impractical
- When nuanced feedback helps
- Programming, decision-making, reasoning

### Implementation
```python
def reflexion_loop(task, max_episodes=3):
    memory = []
    
    for episode in range(max_episodes):
        # Actor generates trajectory
        trajectory = actor(task, memory)
        
        # Evaluator scores
        score, feedback = evaluator(trajectory)
        
        if score >= threshold:
            return trajectory  # Success!
        
        # Self-reflection
        reflection = reflect(trajectory, feedback)
        memory.append(reflection)
    
    return best_trajectory
```

---

## 4. LATS (Language Agent Tree Search)

**Paper:** Zhou et al., 2023 — "Unifies Reasoning, Acting, and Planning"

### Core Idea
Combines Monte Carlo Tree Search with LLMs. Uses the LLM as:
- **Agent:** Generates actions
- **Value function:** Evaluates states
- **Optimizer:** Guides search

### Key Innovation
- Search with lookahead and backtracking
- Learn from both success and failure trajectories
- Can improve over multiple attempts

### When to Use
- Complex decision-making with uncertainty
- When you need planning + acting + reasoning
- Tasks with clear success/failure signals

---

## 5. Pattern Comparison

| Pattern | Strength | Weakness | Best For |
|---------|----------|----------|----------|
| **ReAct** | Interpretable, grounds in observation | Rigid structure | Tool use, retrieval |
| **ToT** | Explores alternatives, backtracks | Expensive (many calls) | Complex reasoning |
| **Reflexion** | Learns from mistakes, builds memory | Needs multiple attempts | Trial-and-error tasks |
| **LATS** | Full planning capability | Most complex | Strategic decisions |

---

## 6. Application to Curiosity Daemon

### Current State
- We have `reflections.jsonl` (episodic memory)
- We have ReAct-style prompts in crons
- Missing: explicit self-evaluation, thought branching

### Recommended Enhancement: ReAct + Reflexion Hybrid

**Before task:**
1. Query reflections for relevant past lessons
2. Load relevant context from memory/

**During task (ReAct):**
```
Thought: [What am I trying to do? What do I know?]
Action: [Search/Read/Execute]
Observation: [What did I find?]
... repeat ...
```

**After task (Reflexion):**
```
Self-Evaluate: Did I meet the success criteria? [YES/PARTIAL/NO]
If PARTIAL or NO:
  - What went wrong?
  - What would I do differently?
  - Log reflection to memory
```

### Implementation
See `scripts/curiosity-engine.py` META_PROMPT for integrated version.

---

## 7. Sources

- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Tree of Thoughts Paper](https://arxiv.org/abs/2305.10601)
- [Reflexion Paper](https://arxiv.org/abs/2303.11366)
- [LATS Paper](https://arxiv.org/abs/2310.04406)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

*Compiled by Alyosha, 2026-02-03*
