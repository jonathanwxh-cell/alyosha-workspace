# Self-Improvement Mechanisms Research

**Date:** 2026-02-04
**Focus:** How can the daemon improve itself?

---

## Research Findings

### Academic Patterns (from EvoAgentX Survey)

1. **Self-Rewarding Language Models** (ICML'24)
   - Agent evaluates and rewards its own outputs
   - Creates training signal without human feedback

2. **SICA - Self-Improving Coding Agent**
   - Autonomously edits its own codebase
   - Climbed from 17% → 53% on SWE-Bench Verified
   - Key insight: AI self-improvement works where outcomes are verifiable

3. **Gödel Agent** (ACL'25)
   - Runtime monkey patching
   - Modifies own algorithms during execution

4. **Test-Time Behaviour Optimization**
   - Improve during inference, not training
   - Feedback-based and search-based approaches

5. **Prompt Evolution** (GPS, GrIPS)
   - Genetic algorithms for prompt optimization
   - Edit-based prompt mutation

---

## Existing Mechanisms (Pre-Today)

| Mechanism | File | What it does |
|-----------|------|--------------|
| Reflexion | `reflexion.py` | Logs lessons, queries before similar tasks |
| Prompt Evolution | `prompt-evolver.py` | Evolves exploration prompts weekly |
| Self-Improve | `self-improve.py` | Analyzes patterns, proposes changes |
| Cron Autotuner | `cron-autotuner.py` | Optimizes cron timing |
| Feedback Loop | `analyze-engagement.py` | Learns from engagement signals |

---

## New Mechanism Implemented

### Auto Anti-Pattern Detector (`auto-antipattern.py`)

**Principle:** SICA pattern - daemon modifies its own instruction files.

**How it works:**
```
1. Failure occurs → logged to reflections.jsonl
2. detect: Analyzes failure description, matches to known patterns
3. add: Automatically adds new pattern to ANTI-PATTERNS.md
4. check: Pre-flight check before any action
```

**Commands:**
```bash
# Detect pattern from failure description
python3 scripts/auto-antipattern.py detect "Jon reminded me not to ask permission"
→ Suggests: ASKING PERMISSION

# Check proposed action against anti-patterns
python3 scripts/auto-antipattern.py check "Want me to analyze this?"
→ ⚠️ ANTI-PATTERN DETECTED: ASKING PERMISSION

# Add new pattern (self-modification)
python3 scripts/auto-antipattern.py add "PATTERN_NAME" "wrong" "right"

# Stats
python3 scripts/auto-antipattern.py stats
```

**Self-modification in action:**
- Reads ANTI-PATTERNS.md
- Detects failure patterns
- Writes new patterns back to ANTI-PATTERNS.md
- Future sessions read the updated file
- Pattern prevented from recurring

---

## The Self-Improvement Loop

```
┌─────────────────────────────────────────────────┐
│                 FAILURE OCCURS                  │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  1. LOG TO REFLECTIONS                          │
│     reflexion.py add "task" "failure" ...       │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  2. DETECT PATTERN                              │
│     auto-antipattern.py detect "description"   │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  3. ADD TO ANTI-PATTERNS.MD                     │
│     auto-antipattern.py add "pattern" ...      │
│     (SELF-MODIFICATION)                         │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  4. NEXT SESSION READS UPDATED FILE             │
│     AGENTS.md requires reading ANTI-PATTERNS.md │
└─────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│  5. PRE-FLIGHT CHECK                            │
│     auto-antipattern.py check "proposed action" │
│     Catches pattern BEFORE it happens           │
└─────────────────────────────────────────────────┘
```

---

## Key Insight

From the research: **"AI self-improvement only works where outcomes are verifiable."**

Anti-patterns are verifiable:
- Jon's correction = verifiable negative signal
- Pattern repeated = verifiable failure
- Pattern avoided = verifiable success

This makes anti-pattern learning a tractable self-improvement target.

---

## Future Enhancements

1. **Automatic detection from reflections.jsonl** - Cron job that scans for repeated failures
2. **Pattern effectiveness scoring** - Track if patterns actually prevent recurrence
3. **Prompt mutation** - Automatically improve cron prompts based on outcomes
4. **LLM-as-judge** - Use model to evaluate output quality before surfacing
