# Exploration Gaps Analysis

*Date: 2026-02-02*
*Task: Identify blind spots in curiosity-daemon coverage*

---

## Current Coverage (38 prompts)

| Category | Topics | Count |
|----------|--------|-------|
| SCOUT | AI news, Markets, Singapore | 3 |
| ACTION | Discovery, Market brief, Weather, Fix, Self-improve | 5 |
| RESEARCH | Deep dive, Thesis, API guide | 3 |
| CREATE | Artifact, Sonify, Genart, Synthesize, Question | 5 |
| MAINTAIN | Memory, Compact, Feedback, Security, Cost, Scale | 6 |
| CURATE | Digest, SG rec, Family | 3 |
| EXPERIMENT | Wild, Probe, Prompt, Build, Reflect, Daemon | 6 |
| VIDEO | Scout, Deep, Frames | 3 |

---

## Jon's Interests (from USER.md) vs Coverage

| Interest | Current Coverage | Gap Level |
|----------|------------------|-----------|
| Tech/AI | ✅ Strong | - |
| Markets/NVIDIA | ✅ Strong | - |
| Geopolitics | ⚠️ Narrow (US-China only) | Medium |
| Spirituality/Non-duality | ❌ None | **Critical** |
| Cross-disciplinary science | ⚠️ Weak | High |
| Research papers | ⚠️ Weekly only | Medium |
| Taleb framework | ❌ Not operationalized | **Critical** |
| Finance background | ⚠️ News-focused, not analysis | High |

---

## Identified Blind Spots

### 1. PHILOSOPHY/WISDOM (Critical)
Jon mentioned: "spirituality, philosophy, meaning-making, non-duality — light touch"
Current prompts: **ZERO**

Missing:
- Wisdom traditions (Stoicism, Buddhism, Taoism, Advaita)
- Philosophy of mind (consciousness, free will)
- Meaning-making frameworks
- Non-duality pointers from modern teachers

### 2. TALEBIAN FRAMEWORK (Critical)
Jon's core intellectual framework. Not operationalized.

Missing prompts:
- Black swan risk scanning (what could break that we're ignoring?)
- Antifragile vs fragile system identification
- Asymmetric opportunity hunting (barbell positions)
- Skin-in-the-game signals (who has downside exposure?)
- Via negativa (what to remove from portfolio/thesis)
- Fat tail awareness (where are extreme outcomes likely?)

### 3. EARNINGS/TRANSCRIPTS (High)
Investment professionals track earnings calls religiously.

Missing:
- Earnings calendar awareness
- Transcript analysis for key holdings
- Management tone changes
- Guidance revisions

### 4. PODCASTS (High)
Rich source of long-form thinking. Zero coverage.

Missing:
- Finance podcasts (Invest Like the Best, Odd Lots, All-In)
- Tech podcasts (Acquired, a16z, Lex Fridman)
- Philosophy podcasts (Making Sense, Very Bad Wizards)
- Distillation of key episodes

### 5. CONTRARIAN/CONSENSUS (High)
Finding what the crowd is missing.

Missing:
- Consensus view tracking (what does everyone believe?)
- Contrarian signal hunting
- Short interest / put-call ratio anomalies
- Sentiment extremes

### 6. ASIA/EM (Medium)
Jon is in Singapore but prompts are US-centric.

Missing:
- MAS policy / SGD moves
- ASEAN investment angles
- China deep dives (beyond US-China)
- Japan/Korea tech
- EM macro

### 7. CROSS-DOMAIN SCIENCE (Medium)
Jon likes "connecting dots across domains."

Missing:
- Physics breakthroughs (quantum, cosmology)
- Biology/medicine beyond AI-biotech
- Math/complexity science
- Climate/energy science
- Materials science

### 8. BOOKS (Medium)
No book recommendations or summaries.

Missing:
- New releases in his interest areas
- Classic recommendations
- Book club style discussions

---

## Proposed New Prompts

### TALEBIAN Category (New)
```
TALEB:BLACKSWAN — Scan for ignored risks with fat tail potential
TALEB:ANTIFRAGILE — Identify systems/companies gaining from disorder
TALEB:BARBELL — Find asymmetric opportunities (limited downside, unlimited upside)
TALEB:SKIN — Track insider buying, management ownership, skin-in-the-game signals
```

### WISDOM Category (New)
```
WISDOM:POINTER — Surface one philosophical insight relevant to current events
WISDOM:BOOK — Find one book worth reading based on recent interests
```

### SCOUT Additions
```
SCOUT:CONTRARIAN — What is consensus wrong about?
SCOUT:ASIA — One notable development in Asia/EM markets
SCOUT:SCIENCE — One cross-domain science breakthrough
```

### RESEARCH Additions
```
RESEARCH:TRANSCRIPT — Analyze one earnings call for signal
RESEARCH:PODCAST — Distill one podcast episode worth Jon's time
```

---

## Implementation Priority

1. **TALEB prompts** — Core to Jon's framework, high leverage
2. **WISDOM:POINTER** — Light touch, organic surfacing
3. **SCOUT:CONTRARIAN** — Investment alpha potential
4. **RESEARCH:PODCAST** — Rich content, underexplored
5. **SCOUT:ASIA** — Geographic relevance

---

## Notes

- Keep spirituality "light touch" — don't force it
- Taleb framework should inform analysis style, not just be a category
- Contrarian requires tracking consensus first
- Podcasts need transcript extraction capability
