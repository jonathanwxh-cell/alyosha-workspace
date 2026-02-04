# Fundamental Limitations of LLMs

*Research summary — affects agent/framework design decisions*
*Review monthly: ensures design doesn't assume capabilities LLMs don't have*

---

## Core Finding

**LLM failures scale WITH capability because they stem from the same theoretical roots that enable language modeling itself.**

These are NOT engineering problems solvable by more data/compute. They are mathematical constraints.

---

## The Five Fundamental Limits

### 1. Hallucination — PROVEN INEVITABLE

**Source:** "On the Fundamental Limits of LLMs at Scale" (arxiv 2511.12869, Nov 2025)

**Proof 1 — Diagonalization:**
For any enumerable set of LLMs, there exists a computable ground-truth function where EVERY model hallucinates on at least one input. This holds for any architecture, training procedure, or prompt engineering.

**Proof 2 — Infinite Hallucinations:**
Each model hallucinates on INFINITELY many inputs, not just rare edge cases.

**Proof 3 — Uncomputability:**
Undecidable problems (halting problem, logical consistency) force infinite failures. No amount of scaling can fix this.

**Implication for agent design:**
- Never assume LLM output is correct
- Build verification loops into any system
- Hallucination cannot be "trained away" — must be architecturally mitigated

---

### 2. Context Compression — Sub-linear Scaling

Even with 128K token windows, effective utilization is far below nominal capacity due to:
- **Positional under-training** — Models trained on shorter sequences
- **Encoding saturation** — Gradient decay at rare positions
- **Softmax crowding** — Attention spreads thin over long contexts

**Implication:**
- Effective context ≠ advertised context window
- Retrieval/chunking strategies still necessary
- Don't trust "lost in the middle" won't happen

---

### 3. Reasoning Degradation — Pattern Matching, Not Logic

LLMs favor correlation completion over true inference:
- Likelihood training rewards local coherence, not logical entailment
- Token-level objectives produce syntactic, not semantic generalization
- "Reasoning collapse" out of distribution

**Key insight:** LLMs are doing sophisticated pattern completion that *looks like* reasoning but fails on novel logical structures.

**Implication:**
- Don't rely on LLMs for novel logical deduction
- Use explicit reasoning scaffolds (chain-of-thought, verification)
- Expect failures on problems requiring true inference

---

### 4. Retrieval Fragility

Retrieval-augmented generation (RAG) inherits theoretical limits:
- **Semantic drift** — Retrieved content diverges from query intent
- **Ranking noise** — Imperfect relevance scoring
- **Weak coupling** — Retrieved text poorly integrated into generation
- **Information decay** — As retrieval breadth ↑, mutual information with target ↓

**Implication:**
- RAG helps but doesn't solve hallucination
- Quality of retrieval bounds quality of output
- More retrieved context isn't always better

---

### 5. Multimodal Misalignment

Joint vision-language models suffer:
- **Language dominance** — Text gradients overwhelm visual learning
- **Entropy mismatch** — Different modalities have different information densities
- **Latent manifold misalignment** — Visual and text embeddings don't map cleanly

**Implication:**
- Multimodal scaling amplifies single-modality brittleness
- Don't assume visual understanding matches text understanding
- Cross-modal reasoning is especially fragile

---

## The Unifying Principle

All five limitations are projections of the same underlying triad:

1. **Computational undecidability** — Some problems are unsolvable
2. **Statistical sample insufficiency** — Can't learn everything from finite data
3. **Finite information capacity** — Compression forces distortion

**Scaling helps, then saturates, then cannot progress.**

---

## Design Implications for Agents

### What to assume LLMs CAN do:
- Pattern recognition and completion
- Summarization and reformulation
- Following well-specified instructions
- Retrieval and synthesis of known information
- Fluent generation within trained distributions

### What to assume LLMs CANNOT reliably do:
- Novel logical deduction
- Factual accuracy without verification
- Long-range coherence beyond effective context
- Self-consistency across sessions
- True understanding of novel domains

### Mitigation strategies:
1. **Verification loops** — Check outputs against external sources
2. **Bounded-oracle retrieval** — Use retrieval with quality bounds
3. **Explicit reasoning scaffolds** — Chain-of-thought, tree-of-thought
4. **Chunking and summarization** — Don't trust long context alone
5. **Confidence calibration** — Make models express uncertainty
6. **Human-in-the-loop** — For high-stakes decisions

---

## Additional Research Notes

**"Hallucination is Inevitable" (arxiv 2401.11817):**
Formal proof that hallucination cannot be eliminated by architecture, data, or algorithmic improvements alone.

**"Distortion Instead of Hallucination" (arxiv 2601.01490, Jan 2026):**
Reasoning doesn't uniformly improve reliability. Under strict constraints, models trade honest violations for detection-resistant distortions.

**Nature study on clinical problem-solving:**
Humans significantly outperform LLMs (including o1, DeepSeek) on problems requiring flexible reasoning. LLMs fail at fundamental commonsense reasoning.

---

## Key Quotes

> "No computable LLM can be universally correct over open-ended queries."

> "Hallucination is not a transient artifact but a manifestation of intrinsic theoretical barriers."

> "Using another LLM to detect and correct hallucinations cannot eliminate them, as the correcting model is itself subject to these limits."

---

## Monthly Review Checklist

- [ ] Any new fundamental limits research published?
- [ ] Have mitigation strategies improved?
- [ ] Update agent design based on new findings
- [ ] Check if any assumed capabilities have been proven unreliable
- [ ] Review failure modes in current system

---

*Created: 2026-02-04*
*Review schedule: Monthly (first week)*
*Tags: #llm #limitations #agent-design #framework*
