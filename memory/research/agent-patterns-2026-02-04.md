# Agent Architecture Patterns Research

## Comparison Matrix

| Pattern | Planning | Execution | Strengths | Weaknesses |
|---------|----------|-----------|-----------|------------|
| **ReAct** | Per-step | Sequential | Simple, transparent | Slow, expensive, myopic |
| **Plan-and-Execute** | Upfront full plan | Sequential | Faster, cheaper | Can't adapt mid-execution |
| **ReWOO** | Upfront with variables | Sequential with deps | No re-planning needed | Still sequential |
| **LLMCompiler** | DAG with parallelism | Parallel | Fast execution | Complex to implement |
| **Tree of Thoughts** | Branching | BFS/DFS | Explores alternatives | Token expensive |
| **Reflexion** | Per-attempt | With memory | Learns from failure | Needs multiple attempts |

## Pattern Details

### 1. ReAct (Reasoning + Acting)
```
Thought: I need to find X
Action: Search("X")
Observation: Found Y
Thought: Now I need Z
Action: Lookup("Z")
...
```
**Best for:** Simple tasks, debugging, transparency
**Our use:** Basic heartbeat actions

### 2. Plan-and-Execute
```
Plan:
1. Research topic A
2. Find connections to B
3. Synthesize findings
4. Generate output

Execute each step → Re-plan if needed
```
**Best for:** Multi-step research, complex tasks
**Our use:** Deep dives, weekly synthesis

### 3. Tree of Thoughts (ToT)
```
Initial prompt → Generate N branches
     ├── Branch 1: Angle A → Evaluate (7/10)
     ├── Branch 2: Angle B → Evaluate (4/10) [prune]
     └── Branch 3: Angle C → Evaluate (8/10) ★
           ├── Sub-branch C1 → Evaluate
           └── Sub-branch C2 → Evaluate
```
**Best for:** Creative exploration, finding non-obvious angles
**Our use:** Curiosity engine, research expansion

### 4. Intrinsic Curiosity Module (ICM)
From RL research - agent is rewarded for:
- **Novelty**: States it hasn't seen before
- **Surprise**: Predictions that were wrong (learning opportunity)
- **Information gain**: Reducing uncertainty

**Our use:** Prioritize topics that are NEW or SURPRISING, not just relevant

## Recommended Daemon Architecture

### For Exploration Tasks
```
BRANCH: Generate 3 exploration angles
EVALUATE: Score each (novelty × relevance × depth potential)
SELECT: Pick best branch
EXECUTE: Deep dive with Plan-and-Execute
REFLECT: Log learnings, update curiosity model
```

### For Research Tasks
```
PLAN: List all steps needed
EXECUTE: Run steps (can use smaller model)
SYNTHESIZE: Combine results (larger model)
REFLECT: What worked? What would I do differently?
```

### For Daily Exploration
Current: Random prompt → Execute
Better: 
1. Generate 3 prompts (branching)
2. Self-evaluate which is most novel/promising
3. Execute winner with Plan-and-Execute
4. Reflect on outcome

## Implementation Priority

1. **Tree-of-Thoughts for exploration** - Branch before committing
2. **Plan-and-Execute for research** - Already partially doing this
3. **ICM-style novelty scoring** - Prioritize surprise over routine

## Key Insight

> "The goal isn't to complete the task efficiently (ReAct). 
> It's to discover something valuable (ToT + ICM).
> Exploration rewards surprise, not just success."
