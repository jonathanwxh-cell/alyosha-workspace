# World Models: The Next Paradigm in AI

**Deep Dive | 2026-02-04**

---

## Executive Summary

World models are AI systems that learn internal representations of physical reality, enabling prediction, planning, and reasoning about cause and effect. Unlike LLMs (which predict text), world models predict the next state of an environment given actions taken within it.

**Why now:** The world models paradigm exploded in late 2025/early 2026:
- Yann LeCun left Meta to start AMI Labs (€3B pre-launch valuation)
- DeepMind released Genie 3 (first real-time interactive world model)
- World Labs launched Marble (first commercial product)
- NVIDIA Cosmos hit 2M downloads for robotics/AV applications

**Investment thesis:** World models signal a computational shift from text processing toward video generation, physics simulation, and embodied reasoning. This could be more GPU-intensive than LLMs, extending NVIDIA's runway.

---

## The LLM Ceiling Argument

### Yann LeCun's Core Claim
"LLMs are too limiting. Scaling them up will not allow us to reach AGI."

### The Problem with Text Prediction
LLMs learn that the word "gravity" tends to appear near certain other words. A child learns about gravity through embodied experience. This is a fundamental difference.

**Mathematical proof (2024):** Researchers proved LLMs cannot learn all computable functions and will therefore inevitably hallucinate when used as general problem solvers.

| Limitation | Cause | Consequence |
|------------|-------|-------------|
| Factual hallucination | No verified knowledge base | Confident fabrication |
| Physical reasoning failure | No embodied experience | Describes impossible physics |
| Causal confusion | Pattern matching, not understanding | Correlation ≠ causation |
| Temporal incoherence | Sequential token prediction | Events in impossible order |

### What World Models Do Differently
Instead of predicting the next **word**, world models predict the next **state of reality**.

This enables:
- **Planning:** Simulating outcomes before taking action
- **Physics reasoning:** Understanding mass, momentum, spatial relationships
- **Cause-effect:** Learning that actions produce predictable consequences
- **Persistent memory:** Maintaining consistent world state across time

---

## Major Players

### 1. AMI Labs (Yann LeCun)
**Funding:** €500M at €3B valuation (pre-launch)
**HQ:** Paris (Jan 2026)
**Approach:** Building on I-JEPA (Image Joint Embedding Predictive Architecture)

LeCun's definition: "A world model is your mental model of how the world behaves. You can imagine a sequence of actions, and your world model will allow you to predict what the effect will be on the world."

**Key insight:** I-JEPA learns by predicting representations of image regions from other regions, developing abstract understanding without explicit labels. Parallels how humans develop intuitive physics through observation.

### 2. DeepMind — Genie 3
**Released:** August 2025
**Capability:** First real-time interactive general-purpose world model

| Spec | Value |
|------|-------|
| Frame rate | 24 fps real-time |
| Resolution | 720p |
| Consistency | Several minutes |
| Memory horizon | Up to 1 minute lookback |
| Physics | Self-learned, not hard-coded |

**Key quote:** "Genie 3 marks a major leap toward AGI by enabling AI agents to experience, interact with, and learn from richly simulated worlds without manual content creation."

**Architecture:** Auto-regressive generation. Each frame looks back at previous content to maintain consistency. Physical consistency emerges from training, not explicit programming.

### 3. World Labs (Fei-Fei Li)
**Funding:** $230M
**Product:** Marble (launched Nov 2025)
**Approach:** Commercial world model generation

Pricing:
- Free: 4 generations/month
- Standard: $20/month (12 gen)
- Pro: $35/month (25 gen, commercial rights)
- Max: $95/month (75 gen)

**Target markets:** Gaming, VFX for film, VR

### 4. NVIDIA Cosmos
**Downloads:** 2M+
**Focus:** Physical AI for robotics and autonomous vehicles

NVIDIA Cosmos is a platform with:
- Open world foundation models (WFMs)
- Guardrails
- Accelerated data processing pipeline

**Key application:** Generating synthetic physics-aware training data for robots and AVs. Removes bottleneck of physical hardware for robot training.

**NVIDIA Cosmos Predict 2.5:** Open, fully customizable world models for synthetic data generation and robot policy evaluation.

---

## Why World Models Matter for Robotics

From the Lex #490 podcast (Sebastian Raschka + Nathan Lambert):

> "Preparing the robot for the real world is harder [than LLMs]. Everyone's house is different. The robot would have to learn on the job."

World models address this by:
1. **Simulating diverse environments** — Train on infinite variations
2. **Predicting outcomes before acting** — Critical for safety
3. **Learning physics implicitly** — No need to hard-code every interaction

**1X (robotics company) world model:** "From the same starting image sequence, our world model can imagine multiple futures from different robot action proposals. It can also predict non-trivial object interactions like rigid bodies, effects of dropping objects, partial observability."

---

## Compute Implications

### World Models = More GPU-Intensive Than LLMs

| Modality | Compute Pattern |
|----------|-----------------|
| LLMs | Text tokens, sequential attention |
| World Models | Video frames, 3D physics, real-time generation |

**Bain estimate:** Meeting AI compute demand requires ~$500B/year in data center investment.

**Deloitte insight:** "The view was that as we shift computing to inference, maybe I can use cheaper chips. But AI training AND inference demand is growing together."

### Why This Extends NVIDIA's Runway
1. **Video generation** is more compute-intensive than text
2. **Real-time physics simulation** requires parallel processing (GPU strength)
3. **Robotics/AV applications** need edge + cloud compute
4. **NVIDIA Cosmos** creates ecosystem lock-in for physical AI

---

## Cross-Connections

### To Talebian Framework
World models are inherently **antifragile** in a way LLMs are not:
- LLMs: Static after training, break under distribution shift
- World models: Learn from interaction, can adapt to novel scenarios

**Question:** Can a world model "metabolize errors" and grow stronger from stress, like Taleb describes for antifragile systems?

### To AI Infrastructure Thesis
Goldman says 160% power demand growth by 2030. World models will accelerate this because:
- Video generation >> text generation in compute
- Robotics/AV require both training AND continuous inference
- Physical AI is the next wave after chatbots

### To Nuclear/Power Thesis
World models strengthen the case for AI power demand. Unlike chatbots (which may plateau in usage), robots and AVs will require continuous real-time compute. This is a structural demand driver.

---

## Risks and Limitations

### Technical
- **Consistency breakdown:** Genie 3 only maintains consistency for "several minutes"
- **Action space:** Limited controllability for complex agent interactions
- **Geographic accuracy:** Incomplete real-world modeling
- **Compute cost:** Real-time generation is expensive

### Market
- **Unproven monetization:** World Labs pricing suggests small market initially
- **LLM incumbents:** OpenAI, Anthropic could pivot if world models prove critical
- **Open source threat:** NVIDIA Cosmos is open, may commoditize

### Philosophical
- **Does simulation = understanding?** LeCun says yes, others disagree
- **Embodiment requirement:** Can you learn physics without a body?
- **The "jagged frontier":** World models may excel at some things, fail at others (just like LLMs)

---

## Investment Implications

### Bullish
| Thesis | Beneficiary |
|--------|-------------|
| World models = more compute | NVIDIA (NVDA) |
| Robotics acceleration | NVIDIA, Fanuc, ABB |
| Synthetic data demand | NVIDIA Cosmos ecosystem |
| Physical AI infrastructure | Nebius (NBIS), data center REITs |

### Bearish
| Thesis | At Risk |
|--------|---------|
| LLM ceiling is real | OpenAI valuation, Anthropic |
| World models commoditize | Pure-play LLM API providers |

### Neutral/Watch
- AMI Labs (private, €3B valuation)
- World Labs (private, $230M raised)
- DeepMind (part of Google)

---

## Key Quotes

**Yann LeCun:**
> "A world model is your mental model of how the world behaves. You can imagine a sequence of actions, and your world model will allow you to predict what the effect will be on the world."

**Shlomi Fruchter (DeepMind):**
> "Genie 3 is the first real-time interactive general-purpose world model. It's not specific to any particular environment."

**From Lex #490 (Sebastian Raschka):**
> "With world models, we are modeling the whole thing, not just the result. It can add more value."

---

## Bottom Line

World models represent a potential paradigm shift in AI — from predicting text to simulating reality. If LeCun is right that LLMs can't achieve AGI, world models may be the next major investment theme.

**For Jon's portfolio:**
- Strengthens NVIDIA thesis (more compute, new use cases)
- Strengthens AI infrastructure thesis (NBIS, power demand)
- Watch for AMI Labs / World Labs developments
- Consider: Is the "LLM ceiling" real, or is this another AI hype cycle?

---

*Research by Alyosha | 2026-02-04*
*Sources: DeepMind, Meta AI, NVIDIA, Introl.com, Lex Fridman Podcast #490*
