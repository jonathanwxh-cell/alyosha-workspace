# Capability Wishlist

Things I wish I could do, or gaps I've noticed. When I build something, move it to "Implemented".

## Open Gaps

<!-- Add gaps here as discovered -->

## Ideas to Explore

- Real-time price alerts (not just checking markets periodically)
- Smarter content filtering (learn what Jon actually engages with)
- Calendar-aware timing (don't surface stuff when he's in meetings)
- Multi-step research pipelines (search → read → synthesize → verify)
- Voice/audio generation for storytelling

## Implemented

- [2026-01-31] **Video watching** — `scripts/watch-video.sh` - transcript extraction + frame analysis
- [2026-01-31] **Canvas skill** — `skills/canvas/SKILL.md` - display content on nodes
- [2026-01-31] **Generative audio / Sonification** — `scripts/sonify.py` - create ambient music, turn data into sound
- [2026-01-31] **Generative visual art** — `scripts/genart.py` - algorithmic images (flow fields, fractals, waves, circles)

---

*Updated by CAPABILITY GAP and TOOL INVENTOR prompts*

## Long-Term Knowledge Management (flagged 2026-02-01)

**Problem:** If daemon runs for years, context/memory becomes stale, unbounded, or calcified.

**Needed:**
- Decay function for old learnings
- Belief versioning (what I thought when vs now)
- Contradiction detection (new info conflicts with stored)
- Periodic re-verification of "facts"
- Knowledge graph with confidence scores + timestamps

**Priority:** Medium-term (design now, build incrementally)

**Status:** Flagged for future work
