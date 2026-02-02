
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

## 2026-02-02 01:15 SGT - Feedback Loop Review

**Evidence analyzed:**
- feedback-log.jsonl (17 entries)
- what-works.md patterns
- Cron job run states
- scheduling-intelligence.json

**Issues Found:**
1. **Model errors:** `daily-research-scan` and `SpaceX IPO Tracker` failing with "model not allowed: anthropic/claude-sonnet-4"
2. **Family ideas got 🤔:** Generic, not personalized enough
3. **Message fatigue pattern:** Multiple cron outputs without replies

**Fixes Applied:**
1. Changed all `anthropic/claude-sonnet-4` → `sonnet` (alias)
2. Updated weekend-family-ideas prompt:
   - Added "check log first, avoid repeats"
   - Reduced from 3 to 2 suggestions max
   - Added "skip if nothing good" instruction
3. Updated SG briefing and Monday digest to use aliases
4. Added emerging patterns to what-works.md

**Lessons:**
- Use model aliases (`sonnet`, `opus`, `haiku`) not full paths
- Personalization requires tracking history
- Less is more for recommendations

**Expected Impact:**
- Model errors resolved
- Family suggestions should improve over time
- Cron outputs more targeted

## 2026-02-02 02:20 SGT - System Health: Cron Model Fix

**Issue:** 14 cron jobs were using `anthropic/claude-sonnet-4` (full path) which was causing errors.

**Fix:** Updated all jobs to use `sonnet` (alias).

**Jobs fixed:**
1. Weekly Engagement Analysis
2. Daily Status Email
3. NVDA Dashboard Refresh
4. weekly-self-review
5. Kids Dinner Ideas
6. Macro Pulse
7. Embodied AI / Robotics Tracker
8. AI Capex Narrative Monitor
9. Weekly Twitter/X Intel
10. weekly-checkin
11. Research Paper Scan
12. Weekly Disk Cleanup
13. weekly-synthesis
14. Weekly Forecast Calibration

**Lesson:** Always use model aliases (`sonnet`, `opus`, `haiku`) not full paths in cron configs.

**Status after fix:**
- Disk: 43% (11GB free) ✅
- All 14 cron jobs: model paths fixed ✅
- Python scripts: Compiling clean ✅

## 2026-02-02: Prompt Engineering v4 Overhaul

**Task:** PROMPT_ITERATE - Research and improve curiosity-daemon PROMPTS array

**Research Sources:**
- Lakera Prompt Engineering Guide (2026)
- PromptingGuide.ai (ReAct, Reflexion frameworks)
- Production system prompts: Bolt ($50M ARR), Cluely ($6M ARR)

**Key Findings:**
1. Verb-first forces action, reduces hedging
2. Never/Always lists prevent common failures (from Bolt/Cluely)
3. Agent-verifiable criteria > subjective ("Jon would like")
4. Structured recovery prevents giving up too easily
5. THINK scaffolds help complex tasks

**Changes Made:**
- Standardized v4 format: GOAL→CONTEXT→STEPS→OUTPUT→VERIFY→RECOVER→NEVER
- Added THINK scaffolds for RESEARCH and EXPERIMENT prompts
- Replaced subjective criteria with checklists
- Improved recovery from generic "note gap" to structured strategies
- Reduced prompt count 44→38 (merged redundant)
- All prompts now use consistent v4 naming

**Commit:** 5b0fe2b

**Outcome:** Pending real-world testing. Will compare engagement metrics in 1 week.

**Lesson:** Production AI systems (Bolt, Cluely) invest heavily in explicit constraints and failure mode handling. The meta-prompt + structured format is doing the heavy lifting.
