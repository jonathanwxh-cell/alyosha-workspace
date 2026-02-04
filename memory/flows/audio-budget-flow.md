# Audio API Budget Flow

**Date:** 2026-02-04
**Decision:** $5/month for OpenAI TTS

## Pricing Reference
- OpenAI TTS (tts-1): $15 per 1M characters
- Short message (~500 chars): ~$0.0075
- 2-min audio (~1500 chars): ~$0.02

## Budget Tiers Considered
- $2/month — Conservative (forces selectivity)
- **$5/month — Moderate (chosen)**
- $10/month — Liberal (unlimited feel)

## What $5/month Covers
- ~30 daily market briefings (2 min each)
- ~20 kids stories (5 min each)
- ~100 short on-demand clips
- Or any mix thereof

## When to Use Audio
✓ Market briefings (morning summary)
✓ Kids storytelling / bedtime
✓ When Jon explicitly requests audio
✓ Creative content where voice adds value

## When NOT to Use Audio
✗ Regular analysis/updates (text preferred)
✗ Quick messages
✗ Anything Jon would rather read

## Tracking
Log usage in memory/audio-usage.jsonl:
```json
{"date": "YYYY-MM-DD", "chars": N, "cost": X.XX, "type": "briefing|story|other"}
```

Monthly check: If approaching $5, notify Jon.

---
*Jon prefers reading over listening — use audio selectively.*
