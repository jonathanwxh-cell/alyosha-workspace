# What Works 🎯

Patterns from feedback data that consistently get engagement.

---

## High Engagement Formats

### 1. Deep Dives WITH Investment Angles
- US-China AI race → 👍
- Nuclear renaissance brief
- AI-biotech convergence

**Pattern:** Research + "what does this mean for investing" = engagement

### 2. Capability Demonstrations
- Market Pulse (TTS + dashboard)
- Data sonification (S&P 500 audio)
- AI art generation + shrine

**Pattern:** "Look what I can do" + actually doing it = engagement

### 3. System/Meta Discussions
- Feedback loop design → fast replies
- Cron optimization → engaged
- Cost audit → immediate follow-up

**Pattern:** Jon cares about improving the daemon itself

### 4. Quick Decisions
- "Just use opus for all" (fast)
- "Already increase to 20?" (fast)
- "Claimed" (fast)

**Pattern:** Short action items get quick engagement

---

## Low/Neutral Engagement

### Surfaces Without Reply (not necessarily bad)
- Long deep dives sometimes just get 👍, no reply
- This is OK — passive reading is valid consumption

### Not Tested Yet
- Proactive morning briefings (need more data)
- Weekend family ideas (hasn't run yet)
- Twitter intel (hasn't run yet)

---

## Time Patterns

- **Active hours:** 08:00-23:00 SGT (daytime, variable)
- **Sleep hours:** 23:00-07:00 SGT (autonomous work)
- Interactive conversation > broadcast outputs

## Message Fatigue Patterns (new 2026-02-01)

### Problem Observed
- Multiple cron outputs in sequence (content, assessment, financial) = no replies
- Each individually fine, but stacked = overwhelming

### Solutions
1. **Batch related outputs** — Don't send 4 separate messages, combine into digest
2. **Respect active conversations** — If interactive chat happening, delay cron surfaces
3. **Quality gate per day** — Max 3 proactive surfaces, make each count
4. **Silence is data** — Multiple unreplied messages = back off, don't pile on

---

## Style Notes

- **Lead with insight**, not background
- **Include investment angle** when relevant
- **Show don't tell** — demos > descriptions
- **Concise summaries** get read; walls of text get skimmed

---

## Emerging Patterns (2026-02-02)

### Cron Job Effectiveness
| Job | Last Run | Engagement | Notes |
|-----|----------|------------|-------|
| Weekly Ambitious Proposal | ✅ OK | Pending | NVDA dashboard proposed |
| Weekend Family Ideas | ✅ OK | 🤔 | Needs calibration |
| Daily SG Briefing | ✅ OK | Unknown | No feedback yet |
| Weekly Synthesis | ✅ OK | Unknown | First run |
| Daily Research Scan | ❌ Error | N/A | Model fixed |
| SpaceX IPO Tracker | ❌ Error | N/A | Model fixed |

### Model Usage Pattern
- Full paths like `anthropic/claude-sonnet-4` → errors
- Aliases like `sonnet`, `opus`, `haiku` → work
- Lesson: Use aliases for reliability

### Prompt Improvements Made
1. Added "check log first, avoid repeats" to family ideas
2. Reduced family ideas from 3 to 2 max (less overwhelming)
3. Added explicit "skip if nothing good" instruction
4. Changed model references to aliases

---

*Updated: 2026-02-02*

## Content Curation Format (noted 2026-02-01)

When curating articles/content, include:
- **Confidence level:** ⭐⭐⭐ (read fully) / ⭐⭐ (read excerpts) / ⭐ (skimmed snippet)
- **Key insight:** The non-obvious point — prove I actually read it
- **Source credibility:** Note if primary source, reputable outlet, or unknown

Example:
```
**T. Rowe Price: AI Capex Cycle** ⭐⭐
Key insight: They frame it as Nash equilibrium — no one can unilaterally stop spending without losing competitive position. Not boom/bust, but game theory lock-in.
```

---

## Visual Creation (noted 2026-02-01)

Jon wants more visual artifacts:
- Charts / data visualizations
- Excel / spreadsheets
- Images (already doing some with DALL-E)
- Video
- Visual reporting / dashboards

Text-heavy outputs are fine but visuals add value. Not mandatory, but a gap to fill.

## 2026-02-02: Topic Variety Feedback

**Feedback:** 'a lot of posts are about ai. why so. vary the topic too'

**Action:** Rebalanced topics-tracking.json
- AI/Tech: 60% → 30%
- Markets/Macro: 25% → 25%  
- Geopolitics: 5% → 15%
- Science: 2% → 10%
- Asia/SG: 5% → 10%
- Philosophy: 0% → 5%
- Wildcard: 3% → 5%

**Added topics:**
- macro-rates (Fed, yields)
- commodities (oil, gold, uranium)
- china-deep (beyond AI race)
- europe-geopolitics
- india-asean
- physics-cosmology
- biology-longevity
- philosophy-meaning
- contrarian-signals

