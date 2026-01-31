# Scaling Risks

Things that could break or become problematic over time. Updated by SUSTAINABILITY AUDIT prompts.

## Mitigated

| Risk | Mitigation | Date |
|------|------------|------|
| Daily log accumulation | `scripts/memory-compact.sh` + monthly cron | 2026-01-31 |
| Reports/briefings pile-up | Archived by memory-compact.sh | 2026-01-31 |
| reflections.jsonl unbounded | Trimmed to 100 entries by compaction | 2026-01-31 |

## Open Risks

| Risk | Impact | Potential Mitigation |
|------|--------|---------------------|
| Git history bloat | Repo size grows, clone times increase | Periodic `git gc`, or archive old repo and start fresh yearly |
| Session transcripts (JSONL) | Disk usage, slow searches | Transcript rotation/archival in OpenClaw config? |
| MEMORY.md bloat | Eats context window if too large | Periodic pruning, maybe split into sections |
| Cron job accumulation | Too many jobs = too many interruptions | Audit quarterly, consolidate or remove stale jobs |
| Stale capability-wishlist items | Clutter, outdated ideas | Quarterly review, archive completed/abandoned |

## Monitoring

Check these periodically:
- `du -sh memory/` — memory folder size
- `du -sh .git/` — git repo size  
- `wc -l memory/*.jsonl` — JSONL file lengths
- `wc -l MEMORY.md` — main memory file size
- `ls reports/ briefings/ | wc -l` — file counts

---

*Updated by SUSTAINABILITY AUDIT daemon prompt*
