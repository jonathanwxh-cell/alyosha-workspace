
## 2026-01-31 14:40 UTC - watch-video.sh improvements

**File:** `scripts/watch-video.sh`

**Issues found:**
1. Bug: Fallback logic was broken — set `VIDEO_ID=""` on transcript failure, then re-checked it causing incorrect flow
2. Missing: No way to skip expensive video download when only transcript wanted
3. Messy: MEDIA lines mixed with result text in stdout

**Fixes applied:**
1. Introduced `GOT_TRANSCRIPT` flag for clean state tracking
2. Added `--transcript-only` flag (skip frame extraction on failure)
3. Added `--frames-only` flag (skip transcript attempt entirely)
4. Separate MEDIA lines output before result text

**Result:** Script is more reliable, flexible, and efficient. `--transcript-only` saves bandwidth/time when transcript is available.

## 2026-02-01 00:25 SGT - sonify.py improvements

**File:** `scripts/sonify.py`

**Issues found:**
1. No CLI arguments — couldn't control duration, seed, or mode
2. Hardcoded seed (42) — every ambient piece sounded identical
3. `data_to_melody` function was unreachable from CLI
4. No help text or usage examples

**Fixes applied:**
1. Added proper CLI parsing with --help
2. Added --duration flag (default: 20s)
3. Added --seed flag (default: random)
4. Added --data FILE and --data-str "..." modes for sonification
5. Added --note-len for data mode timing
6. Removed hardcoded seed from create_ambient_piece()

**Result:** Script now fully usable from command line with all features accessible.

```bash
# Examples that now work:
sonify.py --seed 2026 --duration 30 output.wav
sonify.py --data-str "1,2,3,5,8,13" fibonacci.wav
```

## 2026-02-01: Adaptive Scheduling Implementation

**Change:** Added adaptive scheduling logic to `scheduling-intelligence.json` and created `scripts/should-surface.py`

**New features:**
1. **Backoff rules** - If 3+ surfaces without reply, multiply gap by 1.5x
2. **Conversation awareness** - If reply within 30min, consider convo active and delay surfaces
3. **Day-of-week weighting** - Weekend = 0.7x surface weight, prefer casual content
4. **Recent engagement tracking** - Track last 10 surfaces, adjust frequency based on reply rate

**Evidence:** Jon requested more autonomous operation. Fixed schedules don't adapt to actual patterns.

**Expected impact:** Less message fatigue, better timing, more responsive to actual engagement patterns.
