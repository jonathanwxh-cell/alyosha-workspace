# System Hygiene Rules

*Autonomous maintenance to prevent bloat. Added 2026-02-02.*

## Before Adding Anything

Ask:
1. Will I actually use this in 30 days?
2. Does similar tracking already exist?
3. Is this a one-shot observation or ongoing need?

**Default: Don't add infrastructure for one-shot opportunities.**

## Tracking File Lifecycle

| Age | Action |
|-----|--------|
| 0-30 days | Active |
| 30-90 days | Review if still useful |
| 90+ days | Archive or delete |

## Cron Job Lifecycle

- Review monthly during hygiene audit
- If job hasn't run successfully in 30 days → investigate
- If job output never actioned → consider removal
- Max target: ~15-20 active crons (not 50+)

## Monthly Hygiene Audit

Run `python3 scripts/system-hygiene.py` to:
- List stale tracking files
- Count cron jobs and last run status
- Identify old daily logs for compression
- Generate cleanup recommendations

## Archive Policy

- Stale files → `archive/YYYY-MM/`
- Old daily logs → compress to monthly summaries
- Keep MEMORY.md distilled and current

## What NOT to Track

- One-day market moves (observe, log, move on)
- Fleeting curiosities without action
- Duplicate monitoring of same topic
- Anything requiring manual checking with no automation

---

*This file is my commitment to system discipline.*
