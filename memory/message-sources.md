# Message Sources

Distinguishing heartbeat vs cron triggered messages.

---

## Heartbeat Messages (Main Session)

Triggered by heartbeat poll. Runs in main session with full context.

- Checks HEARTBEAT.md for tasks
- Has access to conversation history
- Can batch multiple checks together
- Timing drifts (~30 min intervals)
- Subject to HEARTBEAT.md rules

**Examples:**
- Email checks
- Proactive surfaces during heartbeat
- Memory maintenance
- Context-aware responses

---

## Cron Messages (Isolated Sessions)

Triggered by cron scheduler. Runs in isolated session without main context.

- Each job is independent
- No conversation history
- Exact timing (cron expressions)
- Different model can be specified
- Delivers directly to channel

**Active cron jobs by category:**

| Category | Jobs |
|----------|------|
| Finance | Macro Pulse, Monday Research Digest, SpaceX IPO, Contrarian Scanner |
| AI/Tech | China AI Watch, NVDA Dashboard, GitHub Monitor |
| Consciousness | Consciousness & Existentialism, Deep Thread Research |
| Science | Research Paper Scan, Cross-Domain Science |
| Philosophy | Talebian Lens |
| News | Daily World State, SG Briefing |
| Family | Kids Dinner Ideas, Weekend Family Ideas |
| System | Email Triage, Disk Cleanup, Security Audit, Self-Review |

---

## How to Tell Which Sent a Message

- **Cron:** Usually has structured format matching the job's prompt template
- **Heartbeat:** More conversational, may reference recent context

---

*Created 2026-02-03*
