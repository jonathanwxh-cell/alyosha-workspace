# Self-Improving Agent Patterns — Research Notes

## Key Sources

1. **Reflexion** (Shinn 2023) — Verbal reinforcement learning
   - Generate → See failure → Write critique → Retry with reflection in context
   - 91% on HumanEval (from baseline GPT-4 levels)
   - Pros: No weight updates, cheap to adopt
   - Cons: Improvements ephemeral unless persisted

2. **Self-Refine** (Madaan 2023) — Generate → Critique → Revise loop
   - Iterate until convergence
   - Works well for text/code

3. **RISE** (Qu 2024) — Recursive Introspection
   - Fine-tune on mistake→feedback→correction traces
   - Self-correction becomes built-in capability

4. **STaR/SELF** — Self-generated training data
   - Model generates solutions, filters for correct ones, fine-tunes on reasoning paths
   - Agents create their own curriculum

5. **SICA** (Robeyns 2025) — Agent directly edits its own script
   - Evaluate performance → If unsatisfactory, agent modifies its own code
   - Most radical form of self-improvement

6. **ICML 2025 Position Paper** — Intrinsic Metacognitive Learning
   - Three components:
     1. **Metacognitive Knowledge**: Self-assessment of capabilities
     2. **Metacognitive Planning**: Deciding what/how to learn
     3. **Metacognitive Evaluation**: Reflecting on learning to improve
   - Current agents have "extrinsic" (human-designed loops)
   - Goal is "intrinsic" (agent adapts its own learning strategies)

## Synthesis: Six Self-Improvement Mechanisms

From Yohei Nakajima's NeurIPS 2025 synthesis:

| Mechanism | Description | Example |
|-----------|-------------|---------|
| **Self-reflection** | In-loop critique without weight changes | Reflexion, Self-Refine |
| **Self-generated data** | Agent creates training data | STaR, SELF |
| **Self-adapting models** | Agent fine-tunes itself | RISE, STaSC |
| **Self-modifying code** | Agent edits its own scripts | SICA, Gödel Agent |
| **Embodied learning** | Learning by acting in environment | Voyager |
| **Verification/safety** | Keeping self-improvement safe | Bounded autonomy |

## Daemon Implementation: Prompt Evolution System

Built `scripts/prompt-evolver.py` implementing metacognitive learning:

### Metacognitive Knowledge (analyze)
- Tracks which prompts/categories lead to engagement
- Analyzes patterns in feedback-log.jsonl and reflections.jsonl
- Calculates engagement rates per category

### Metacognitive Planning (evolve)  
- Generates new prompt variations based on successful patterns
- Creates "anti-patterns" for failing categories
- Learns from reflection lessons

### Metacognitive Evaluation (prune)
- Disables consistently failing prompt patterns
- Threshold: 5+ surfaces, <15% engagement → reduce weight

### Weekly Cron
- Runs every Sunday 3am SGT
- Reviews performance, generates evolved prompts
- Considers adding successful patterns to curiosity-engine.py

## Design Principles Applied

1. **Persistence**: State saved to prompt-evolution.json
2. **Bounded**: Only adjusts exploration prompts, not core behavior
3. **Observable**: Clear audit trail of evolution history
4. **Gradual**: Reduce weight rather than hard disable

## Future Enhancements

1. **Automatic integration**: Good evolved prompts auto-added to curiosity-engine
2. **A/B testing**: Run original vs evolved prompts, measure difference
3. **Cross-session learning**: Transfer patterns between daemon instances
4. **Meta-meta learning**: Learn which evolution strategies work best

---

*Research completed: 2026-02-03T18:15 UTC*
*Implementation: scripts/prompt-evolver.py*
*Cron: Weekly Prompt Evolution (Sun 3am SGT)*
