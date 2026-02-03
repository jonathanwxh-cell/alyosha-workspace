# Prompt Engineering Research — 2026-02-03

## Key Findings from Literature

### 1. Reflexion Pattern (Shinn et al., 2023)
- Generate → Critique → Revise loop
- **91% pass rate** on HumanEval (vs baseline)
- Key insight: Store reflections for reuse, not just discard

### 2. Self-Challenging Agents (Zhou et al., NeurIPS 2025)
- **Challenger + Executor** dual roles
- "Code-as-Task" format: instruction + verifiable test code
- Tests provide scalar reward (not fuzzy LLM judgment)
- **2x performance** on tool-use benchmarks

### 3. Self-Generated In-Context Examples (Sarukkai et al., 2025)
- Store successful trajectories → reuse as prompts
- **73% → 93%** on ALFWorld
- "Experience replay for prompting"
- Key: Curation matters (don't replay suboptimal patterns)

### 4. RISE, STaR, SELF Patterns
- Train on mistake→fix traces
- Self-correction as built-in capability
- "Learning to improve" as training objective

## Design Principles for Action-Oriented Prompts

### MUST HAVE (Research-Backed)
1. **Verifiable success** — Test command, file existence check, measurable output
2. **Failure recovery** — Explicit fallback paths (if X fails → try Y)
3. **Experience capture** — Log successful patterns for reuse
4. **Time-bounded** — Prevents infinite loops, forces prioritization
5. **Single objective** — One clear goal (not "explore and maybe also...")

### SHOULD HAVE (Best Practice)
6. **Difficulty gradient** — Easy/Medium/Hard variants
7. **Self-challenge mode** — Generate harder version after success
8. **Role clarity** — Am I exploring, building, or validating?
9. **Anti-patterns** — Explicit "don't do X" prevents common failures

### NICE TO HAVE
10. **Curriculum hooks** — Connect to prior work, build on it
11. **Meta-reflection** — "What would make this prompt better?"

## Prompt Template (Improved)

```
[CATEGORY] [DIFFICULTY] [TIME]: [VERB] [OBJECT]

[CONTEXT] Why this matters / connection to prior work

[STEPS]
1. First action
2. Second action  
3. Verification step

[SUCCESS TEST]
- Command: `[test command]`
- Expected: [specific output]

[FAILURE RECOVERY]
- If [X] fails → Try [Y]
- If still blocked → Log blocker, try [Z]

[EXPERIENCE CAPTURE]
- If successful: `echo '{"pattern":"..."}' >> memory/successful-patterns.jsonl`

[SELF-CHALLENGE]
- After success: Generate harder variant for tomorrow

[ANTI-PATTERNS]
- ❌ [Common mistake 1]
- ❌ [Common mistake 2]
```

## Key Insight

The difference between vague prompts and effective prompts:

| Vague | Effective |
|-------|-----------|
| "Find something interesting" | "Find ONE paper with >5% benchmark gain, extract key number" |
| "Build a tool" | "Build script <100 lines, test with `--help`, exit 0 required" |
| "Think about X" | "Write 100 words, save to file, verify file exists" |

**The secret: Verifiable success + failure recovery + experience capture**
