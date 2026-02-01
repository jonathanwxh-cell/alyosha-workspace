# Feedback System

## How It Works

### Explicit Signals (Jon's choice)

| Emoji | Meaning | My Action |
|-------|---------|-----------|
| 👍 | Useful / Good | More of this |
| 👎 | Not useful / Stop this | Less or eliminate |
| 🔥 | Really good / More like this | High priority to repeat |
| 🤔 | Interesting but unsure | Note for calibration |
| 💤 | Too long / boring | Shorten or skip type |
| ⭐ | Save / Reference later | Add to highlights file |

- No reaction = Neutral → **No penalty** (passive reading is valid)

### Implicit Signals (I observe)
- **Reply** = Engaged enough to respond → Positive signal
- **Reply speed** = Fast reply (<5 min) suggests high interest
- **Reply depth** = Long reply / follow-up questions = very engaged
- **Time patterns** = When does Jon engage? (Track hour SGT)
- **Topic patterns** = What topics get replies vs. silence over time

## Logging

All feedback logged to `memory/feedback-log.jsonl`:
```json
{"ts": "...", "msgId": "...", "type": "reaction", "emoji": "👍", "topic": "...", "category": "..."}
{"ts": "...", "msgId": "...", "type": "reply", "replySpeed": "fast|normal|slow", "replyDepth": "short|medium|long", "hourSGT": 22, "topic": "...", "category": "..."}
{"ts": "...", "msgId": "...", "type": "surface", "hourSGT": 14, "topic": "...", "category": "...", "gotReply": false}
```

### Implicit Tracking Rules

1. **Log every surface I send** with timestamp + category
2. **When Jon replies**, link it back to what he's replying to
3. **Calculate reply speed**: <5min = fast, 5-30min = normal, >30min = slow
4. **Track hour (SGT)** for time-of-day patterns
5. **Weekly: analyze** what categories/times get engagement

## Categories to Track

- `research_brief` — Deep dives, investment landscapes
- `quick_share` — Short observations, links
- `question` — Me asking Jon something
- `tool_demo` — New capability demonstrations
- `proactive_alert` — Unsolicited surfaces
- `market_update` — Market-related content

## Weekly Review

During weekly self-review (Monday 3am UTC cron), analyze:

### Explicit Signals
1. What got 👍? → Do more of this category/style
2. What got 👎? → Stop or significantly change approach

### Implicit Patterns
3. **Reply rate by category**: Which categories get replies vs. silence?
4. **Time-of-day**: When does Jon engage most? (Likely late night SGT)
5. **Reply speed**: What topics get fast replies? (= high interest)
6. **Reply depth**: What sparks longer conversations?

### Actions
- Update `memory/topics-tracking.json` weights based on engagement
- Adjust HEARTBEAT.md timing guidance if patterns emerge
- Note high-performers in `memory/what-works.md`

### Sample Analysis Query
```python
# Count replies by category
from collections import Counter
import json
with open('memory/feedback-log.jsonl') as f:
    entries = [json.loads(l) for l in f if l.strip()]
replies = [e for e in entries if e['type'] == 'reply']
print(Counter(e['category'] for e in replies))
```

## Key Principle

**Silence ≠ failure.** Jon reads passively. Only explicit negative signals (👎 or "stop this") mean something's wrong.

## Model Quality Monitoring

Cron jobs switched to Sonnet are monitored. If Jon reacts 👎 or 💤 to a Sonnet-powered job output, check if it's a model quality issue and consider reverting to Opus.

See `memory/model-quality-monitor.md` for tracking.
