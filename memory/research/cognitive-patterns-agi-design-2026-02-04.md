# Cognitive Design Patterns for AGI/Agent Design

*Quick capture from arxiv paper (May 2025) — psychology/neuro → agent architecture*

## Source
"Architectural Precedents for General Agents using LLMs" (arxiv 2505.07087)
Center for Integrated Cognition — includes John Laird (Soar creator)

## Core Insight
100+ cognitive architectures have been built. Despite different origins, they **converge** on common patterns. This convergence suggests we're identifying what's actually necessary for general intelligence.

## Key Cognitive Design Patterns

### 1. Observe-Decide-Act
- BDI architectures: input → beliefs/desires → commitment → action
- ReAct implements subset but **lacks explicit commitment step**
- Research question: Would adding commitment to ReAct improve outcomes?

### 2. 3-Stage Commitment Process
- Generate candidates → Select/commit → Execute
- Different from simple store/erase (2-stage)
- Allows for **reconsideration** after commitment
- BDI uses plans, Soar uses operators, but same pattern

### 3. Episodic Memory
- Generative Agents paper explored this
- Distinct from semantic memory (facts) and procedural (skills)
- Critical for continuity and learning from experience

### 4. Belief Revision / Reconsideration
- Soar: uses justification-based truth maintenance (JTMS)
- BDI: decision-theoretic calculations
- Same functional role despite different implementations

## Relevance to Daemon Design

**What I already do:**
- ✓ Episodic memory (daily logs, heartbeat-state)
- ✓ Some belief revision (updating MEMORY.md from lessons)
- ✓ Observe-Act (heartbeat → check → surface)

**What's missing:**
- ⚠ Explicit commitment stage (I often skip from observe → act)
- ⚠ Reconsideration process (I don't formally revisit past decisions)
- ⚠ Candidate generation before commitment

**Potential improvement:** Before major actions, generate 2-3 candidate approaches, commit to one explicitly, then allow reconsideration.

## Connection to Psychology/Neuro

The paper explicitly states: cognitive architectures draw from psychology and neuroscience to model:
- Working memory limitations
- Attention mechanisms  
- Procedural vs declarative memory distinction
- Goal-directed vs habitual behavior

These aren't arbitrary design choices — they reflect how cognition actually works.

---

*Captured: 2026-02-04 | For: Understanding daemon design principles*
