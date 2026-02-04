# Daemon Improvement Research — 2026-02-04

## Executive Summary

Researched autonomous agent architectures, prompt engineering advances, and memory management patterns. Found several techniques we already use + new improvements to implement.

---

## 1. Memory Blocks (Letta/MemGPT Pattern)

**Source:** Letta blog, MemGPT paper

**What it is:** Break context window into discrete, purposeful blocks:
- Human block: user info, preferences
- Persona block: agent identity, traits
- Task-state block: current focus
- Knowledge block: domain facts

**Status:** ✅ Already implemented in `memory/blocks/`

**Improvement:** 
- Add "sleep-time compute" — background agent that reviews conversations and updates memory blocks during idle time
- We have Nightly Memory Extraction cron — could enhance with block-specific updates

---

## 2. Ambient Agent Pattern

**Source:** Moveworks, ZBrain, Akira AI

**What it is:** Always-on agents that:
- Monitor streams continuously (not wait for prompts)
- Act proactively on system triggers
- Surface only on meaningful change (delta detection)

**Status:** ✅ Partially implemented via heartbeats + crons

**Key insight:** "They don't wait for commands — they monitor signals and act when triggers occur"

**Improvement:**
- Strengthen delta detection before surfacing
- Add explicit "notify / question / review" communication modes (already in HEARTBEAT.md)
- Better trigger definitions for each cron

---

## 3. Prompt Engineering Techniques (2025)

**Source:** Forbes, Medium (Alonso Aguilar), Prompt Engineering Guide

### 3a. Recursive Self-Improvement Prompting (RSIP)
- Generate → Critique → Improve cycle
- Evaluate on different criteria each pass (accuracy → clarity → completeness)
- **Claim:** 60% reduction in revision cycles

**Implementation:** Add to complex analysis crons (Fragility Index, Research Scan)

### 3b. Context-Aware Decomposition (CAD)
- Break complex problems into components
- Maintain "thinking journal" tracking why each component matters
- Synthesize with interdependency awareness

**Implementation:** Good for deep research, stock analysis

### 3c. Multi-Perspective Simulation (MPS)
- Run virtual expert panel in single conversation
- Articulate assumptions, arguments, weaknesses for each viewpoint
- Conclude with integrated analysis

**Claim:** Identifies overlooked considerations in ~70% of analyses

**Implementation:** Add to Talebian Lens, Contrarian Scanner prompts

### 3d. Calibrated Confidence Prompting (CCP)
- Explicit confidence levels (95%, 80-95%, <80%, unknown)
- Justify high-confidence claims
- Ask what would increase confidence for uncertain claims

**Status:** ✅ Partially in HEARTBEAT.md ("CONFIDENCE: [1-10]")

**Implementation:** Make more explicit in investment-related crons

---

## 4. ReAct Pattern (Reasoning + Acting)

**Source:** Google Research, IBM, arXiv

**What it is:**
```
THOUGHT: What am I trying to do?
ACTION: Tool/step to take
OBSERVATION: What happened?
→ Repeat
```

**Status:** ✅ Already in HEARTBEAT.md

**Key insight:** "ReAct overcomes hallucination by interacting with external APIs and generating interpretable task-solving trajectories"

---

## 5. Reflexion Pattern

**Source:** arXiv (Shinn et al.), Hugging Face

**What it is:**
1. Generate trajectory
2. Evaluate outcome
3. Reflect verbally on failure
4. Store reflection in long-term memory
5. Use reflections to improve next attempt

**Status:** ✅ Have `scripts/reflexion.py` and pattern in HEARTBEAT.md

**Improvement:** 
- Actually USE reflexion queries before similar tasks (currently underused)
- Make it mandatory in cron prompts for recurring tasks

---

## 6. Self-Evolving Agents

**Source:** OpenAI Cookbook

**What it is:**
- Baseline agent produces outputs
- Human feedback or LLM-as-judge evaluates
- Meta-prompting generates improved prompts
- Loop until score exceeds threshold

**Status:** ✅ Have `scripts/self-improve.py` and `scripts/prompt-evolver.py`

**Key insight:** "Gradually shift human effort from detailed correction to high-level oversight"

**Improvement:**
- Run self-improve analysis more frequently
- Track which cron prompts have been evolved

---

## Actionable Improvements

### Immediate (implement now)

1. **Add multi-perspective to Talebian Lens prompt**
   - Bull case / Bear case / Black swan case perspectives

2. **Strengthen delta detection in surfacing crons**
   - Before surfacing, explicitly ask: "What CHANGED since last check?"

3. **Add confidence scoring to Research Scan**
   - Every claim gets [HIGH/MEDIUM/LOW] with reasoning

### Short-term (this week)

4. **Enhance reflexion usage**
   - Add `python3 scripts/reflexion.py query "topic"` to top of repeating crons

5. **Sleep-time memory update**
   - Enhance Nightly Memory Extraction to update memory blocks

### Medium-term (experiment)

6. **RSIP for deep analyses**
   - Fragility Index: generate → self-critique → improve before sending

7. **Automated prompt evolution scoring**
   - Track cron success rate, auto-suggest prompt improvements

---

## Sources

1. Letta Blog: Memory Blocks - https://www.letta.com/blog/memory-blocks
2. MemGPT Paper - https://arxiv.org/abs/2310.08560
3. Moveworks: Ambient Agents - https://www.moveworks.com/us/en/resources/blog/what-is-an-ambient-agent
4. Prompt Engineering Guide - https://www.promptingguide.ai/
5. Reflexion Paper - https://arxiv.org/abs/2303.11366
6. OpenAI Cookbook: Self-Evolving Agents - https://cookbook.openai.com/examples/partners/self_evolving_agents/
7. Forbes: Prompt Engineering 2025 - https://www.forbes.com/sites/lanceeliot/2025/04/09/annual-compilation-of-the-best-prompt-engineering-techniques/
8. Medium (Aguilar): Complete Prompt Guide 2025 - https://aloaguilar20.medium.com/the-complete-prompt-engineering-guide-for-2025/

---

*Research completed 2026-02-04. Priority: implement multi-perspective and confidence scoring.*
