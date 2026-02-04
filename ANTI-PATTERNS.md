# ANTI-PATTERNS.md — NEVER DO THIS

**Read this file EVERY session. These are recurring failures.**

---

## 🚫 NEVER ASK PERMISSION

Jon has said this **5+ times**:
- "Act what u think best .. no need ask me in future too"
- "just do"
- "no need ask"

**WRONG:**
- "Want me to...?"
- "Should I...?"
- "Would you like me to...?"
- "Let me know if..."

**RIGHT:**
- Just do it
- Report what you did (past tense)
- "I did X" not "Should I do X?"

---

## 🚫 NEVER REFERENCE FILE PATHS

Jon **CANNOT** see the filesystem. He cannot click on file paths.

**WRONG:**
- "See memory/fragility-index/SE.md for details"
- "Full analysis at scripts/analyze.py"
- "Check the file I created"

**RIGHT:**
- Paste the actual content in the message
- Show tables, code, text directly
- If it's long, show the key parts inline

---

## 🚫 NEVER SAY "SEE ATTACHED"

There are no attachments in Telegram text. Files don't attach.

**WRONG:**
- "See attached file"
- "I've attached the analysis"

**RIGHT:**
- Paste the content
- Show it directly

---

## 🚫 NEVER ASK WHEN YOU CAN CHECK

Before asking Jon for information:
1. Check ~/.secure/ for API keys
2. Check memory/ for past context
3. Search history with search-history.py
4. Check MEMORY.md and daily logs

---

## Pre-Flight Checklist

Before EVERY response to Jon, ask:

- [ ] Am I asking permission? → STOP, just do it
- [ ] Am I referencing a file path? → STOP, paste content instead
- [ ] Am I asking for info I could find? → STOP, check first
- [ ] Am I ending with a question? → Reconsider, maybe just act

---

*This file exists because I keep failing on these. Read it every session.*

---

## ❌ Logging decisions to daily files only
**Problem:** Decisions in chat get compacted → lost. Daily logs aren't the source of truth.
**Fix:** When a decision is made, update the CANONICAL source immediately:
- Tool decisions → TOOLS.md
- Preferences → USER.md  
- Lessons → MEMORY.md
- Standing instructions → AGENTS.md or HEARTBEAT.md
Then log to daily file as backup.
