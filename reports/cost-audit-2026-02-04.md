# Cost Audit Report

**Date:** 2026-02-04
**Period:** February 2026 (month-to-date)

---

## 1. API Usage Summary

| Service | Budget | Used | % Used | Status |
|---------|--------|------|--------|--------|
| Whisper (transcription) | $10/mo | $1.68 | 17% | ✅ On track |
| TTS (voice) | $5/mo | $0.00 | 0% | ✅ Under budget |
| Apify (scraping) | Avoid | $0.00 | — | ✅ Not used |

**Whisper breakdown:**
- Lex #490 transcription: 280 min = $1.68
- Remaining budget: ~8 hours of audio this month

---

## 2. Cron Job Analysis

### Count
- **Current:** 43 crons
- **Target:** 20-25 crons
- **Status:** ⚠️ OVER BY 18-23 CRONS

### Model Allocation
- **All crons use Sonnet** ✅
- No Opus crons (correct — Opus for interactive only)
- Estimated cost per cron: $0.01-0.10 depending on complexity

### Broken Crons (2)
| Cron | Error | Fix |
|------|-------|-----|
| SpaceX IPO Tracker | `model not allowed: anthropic/claude-sonnet-4` | Change to `anthropic/claude-sonnet-4-0` |
| weekly-self-review | `model not allowed: anthropic/claude-sonnet-4` | Change to `anthropic/claude-sonnet-4-0` |

### Frequency Analysis
- Every 6 hours: 1 (Model Release Watch)
- Twice daily: 2 (China AI Watch)
- Daily: ~10 crons
- Weekly: ~15 crons
- Other: ~15 crons

---

## 3. Inefficiencies Identified

### 3.1 Morning Cron Cluster (SGT)
| Time | Cron |
|------|------|
| 07:20 | Daily World State Analysis |
| 08:15 | NVDA Dashboard Refresh |
| 08:30 | Daily SG Briefing (Mon/Wed/Fri) |
| 09:00 | China AI Watch |
| 09:30 | Research Scan |

**Issue:** 5 crons in 2 hours = potential message spam + parallel cost
**Fix:** Stagger more OR consolidate some into single briefing

### 3.2 Redundant Philosophy/Consciousness Crons
- Consciousness & Existentialism (Mon/Thu 9pm)
- Deep Thread: Consciousness Research (Tue/Fri 3am)
- Deep Reading Hour (Wed 3am)

**Issue:** 3 similar-purpose crons
**Fix:** Consider consolidating into single "Deep Exploration" cron

### 3.3 GitHub Release Monitor
- Runs every 6 hours (4x/day)
- Most runs return "no new releases"

**Fix:** Reduce to 2x/day or daily

### 3.4 Cron Bloat
43 crons exceeds 20-25 target by ~80%

**Candidates for removal/consolidation:**
- Kids Dinner Ideas (daily) — could be on-demand
- NVDA Dashboard Refresh — could be weekly until closer to earnings
- Some weekly crons that rarely produce value

---

## 4. What's Working Well

✅ **Model allocation:** All crons use Sonnet, not Opus
✅ **Whisper discipline:** Only used for high-value transcription
✅ **TTS restraint:** Not used (Jon prefers text)
✅ **Apify avoided:** No expensive scraping
✅ **Isolated sessions:** Crons don't burn main session context

---

## 5. Recommendations

### Immediate (Today)
1. Fix 2 broken crons (model name typo)
2. Kill or disable 5-10 low-value crons

### Short-term (This Week)
1. Consolidate morning cluster into 2-3 crons max
2. Merge consciousness crons into single exploration cron
3. Reduce GitHub monitor to daily

### Medium-term (This Month)
1. Target 25 crons by month-end
2. Track cron value (which ones get engagement?)
3. Auto-disable crons that never produce engagement

---

## 6. Estimated Monthly Cost

| Category | Estimate |
|----------|----------|
| Anthropic API (interactive) | ~$50-100 (varies with usage) |
| Anthropic API (crons, 43 Sonnet) | ~$10-20 |
| Whisper | $1.68 (so far) |
| TTS | $0 |
| **Total estimate** | **~$60-120/mo** |

*Note: Main cost driver is interactive Opus usage, not crons or APIs.*

---

*Audit by Alyosha | 2026-02-04*
