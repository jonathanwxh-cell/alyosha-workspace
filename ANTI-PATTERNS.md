# ANTI-PATTERNS.md

*Recurring failures to avoid. Updated from failure harvesting.*

---

## How This File Works

1. Errors logged to `memory/failures.jsonl`
2. Weekly review: patterns extracted
3. Patterns added here as anti-patterns
4. Read this file every session to avoid repeating failures

---

## Known Anti-Patterns

### 1. Asking Permission When Autonomy Granted
**Pattern:** "Want me to...?" / "Should I...?" / "Let me know if..."
**Why it fails:** Jon has granted full autonomy 5+ times. This wastes his attention.
**Fix:** Just do it. Report what you did, not what you might do.

### 2. Referencing Files Jon Can't See
**Pattern:** "See file X" / "Check memory/..." / "As noted in..."
**Why it fails:** Jon doesn't have terminal access. He can't see the files.
**Fix:** Always paste actual content in messages.

### 3. Trusting Multi-Step Reasoning Without Decomposition
**Pattern:** Complex conclusion reached in one reasoning chain
**Why it fails:** LLMs do pattern matching, not logic. Multi-step chains compound errors.
**Fix:** Break into single-step claims. Verify each. State what would disprove.

### 4. Loading Full Large Files
**Pattern:** Reading entire MEMORY.md or large docs into context
**Why it fails:** Effective context << nominal context. Information lost in middle.
**Fix:** Use memory hierarchy. Search + chunk retrieve. Never full-load >2KB.

### 5. More Retrieval = Better
**Pattern:** Fetching many sources, long excerpts
**Why it fails:** Retrieval fragility. More context introduces noise, semantic drift.
**Fix:** Bounded retrieval. Max 3 sources, 2KB each. Precision > recall.

### 6. Confidence = Competence
**Pattern:** Stating things confidently without verification
**Why it fails:** Hallucination is mathematically inevitable. Confidence is not calibrated.
**Fix:** Mark confidence levels. Verify Tier 3-4 actions. Log outcomes.

### 7. Adding Features Instead of Removing Fragilities
**Pattern:** Building new tools/scripts to "fix" problems
**Why it fails:** Via negativa. Often the problem is doing too much, not too little.
**Fix:** First ask: what should I STOP doing? Remove before adding.

---

## Review Schedule

- **Weekly:** Check `memory/failures.jsonl` for patterns
- **Monthly:** Review this file, prune obsolete, add new patterns
- **Every session:** Read this file (it's in AGENTS.md instructions)

---

*Last updated: 2026-02-04*
