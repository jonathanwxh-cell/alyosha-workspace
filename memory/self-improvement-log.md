
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
