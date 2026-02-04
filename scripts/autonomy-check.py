#!/usr/bin/env python3
"""
Autonomy Pre-Response Check
Run before responding to verify autonomous behavior patterns.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
CORRECTIONS_FILE = WORKSPACE / 'memory' / 'corrections-log.jsonl'
PREFERENCES_FILE = WORKSPACE / 'memory' / 'preference-model.json'
ANTICIPATIONS_FILE = WORKSPACE / 'memory' / 'anticipations.jsonl'

def load_preferences():
    """Load Jon's preference model."""
    if PREFERENCES_FILE.exists():
        return json.loads(PREFERENCES_FILE.read_text())
    return {
        "communication": {
            "prefers_brevity": True,
            "show_dont_tell": True,
            "no_permission_asking": True,
            "paste_content_directly": True,
            "action_over_discussion": True
        },
        "content": {
            "intellectual_over_financial": True,
            "deep_dives_engage": True,
            "demos_positive": True,
            "meta_discussions_engage": True
        },
        "timing": {
            "active_hours_sgt": [8, 23],
            "weekend_lighter_touch": True
        },
        "anti_patterns": [
            "asking_permission",
            "ending_with_want_me_to",
            "referencing_files_not_pasting",
            "generic_recommendations",
            "feeding_speculation",
            "walls_of_text"
        ]
    }

def check_response(response_text: str) -> dict:
    """Check a response against autonomy patterns."""
    issues = []
    prefs = load_preferences()
    
    # Anti-pattern checks
    permission_phrases = [
        "want me to",
        "shall i",
        "should i",
        "would you like me to",
        "do you want",
        "let me know if",
        "happy to help"
    ]
    
    lower_text = response_text.lower()
    
    for phrase in permission_phrases:
        if phrase in lower_text:
            issues.append(f"Permission-asking detected: '{phrase}'")
    
    # File reference without content
    if "see file" in lower_text or "check the file" in lower_text:
        issues.append("File reference without pasting content")
    
    # Too long check (>500 words for routine responses)
    word_count = len(response_text.split())
    if word_count > 500:
        issues.append(f"Response may be too long ({word_count} words)")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "word_count": word_count
    }

def log_correction(correction_type: str, context: str):
    """Log a correction for tracking."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": correction_type,
        "context": context
    }
    with open(CORRECTIONS_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def get_correction_stats(days: int = 7) -> dict:
    """Get correction statistics."""
    if not CORRECTIONS_FILE.exists():
        return {"total": 0, "by_type": {}, "daily_avg": 0}
    
    from datetime import timedelta
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    corrections = []
    for line in CORRECTIONS_FILE.read_text().strip().split('\n'):
        if line:
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry['ts'].replace('Z', '+00:00'))
            if ts > cutoff:
                corrections.append(entry)
    
    by_type = {}
    for c in corrections:
        t = c['type']
        by_type[t] = by_type.get(t, 0) + 1
    
    return {
        "total": len(corrections),
        "by_type": by_type,
        "daily_avg": round(len(corrections) / days, 2)
    }

def log_anticipation(anticipated: str, outcome: str = "pending"):
    """Log an anticipation for tracking accuracy."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "anticipated": anticipated,
        "outcome": outcome
    }
    with open(ANTICIPATIONS_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')

def update_anticipation(anticipated: str, outcome: str):
    """Update an anticipation with its outcome."""
    if not ANTICIPATIONS_FILE.exists():
        return False
    
    lines = ANTICIPATIONS_FILE.read_text().strip().split('\n')
    updated = False
    new_lines = []
    
    for line in lines:
        if line:
            entry = json.loads(line)
            if entry['anticipated'] == anticipated and entry['outcome'] == 'pending':
                entry['outcome'] = outcome
                entry['resolved_ts'] = datetime.now(timezone.utc).isoformat()
                updated = True
            new_lines.append(json.dumps(entry))
    
    ANTICIPATIONS_FILE.write_text('\n'.join(new_lines) + '\n')
    return updated

def get_anticipation_accuracy() -> dict:
    """Calculate anticipation accuracy."""
    if not ANTICIPATIONS_FILE.exists():
        return {"total": 0, "correct": 0, "accuracy": 0}
    
    total = 0
    correct = 0
    
    for line in ANTICIPATIONS_FILE.read_text().strip().split('\n'):
        if line:
            entry = json.loads(line)
            if entry['outcome'] != 'pending':
                total += 1
                if entry['outcome'] == 'correct':
                    correct += 1
    
    return {
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total * 100, 1) if total > 0 else 0
    }

def save_preferences(prefs: dict):
    """Save preference model."""
    PREFERENCES_FILE.write_text(json.dumps(prefs, indent=2))

def print_status():
    """Print autonomy status."""
    prefs = load_preferences()
    corrections = get_correction_stats()
    anticipations = get_anticipation_accuracy()
    
    print("=== AUTONOMY STATUS ===\n")
    
    print("Corrections (7 days):")
    print(f"  Total: {corrections['total']}")
    print(f"  Daily avg: {corrections['daily_avg']} (target: <1)")
    if corrections['by_type']:
        print("  By type:")
        for t, c in corrections['by_type'].items():
            print(f"    - {t}: {c}")
    
    print(f"\nAnticipations:")
    print(f"  Total resolved: {anticipations['total']}")
    print(f"  Correct: {anticipations['correct']}")
    print(f"  Accuracy: {anticipations['accuracy']}%")
    
    print(f"\nPreference model loaded: {len(prefs.get('anti_patterns', []))} anti-patterns tracked")
    
    # Calculate autonomy score
    correction_score = max(0, 10 - corrections['daily_avg'] * 2)  # 0-10
    anticipation_score = anticipations['accuracy'] / 10  # 0-10
    
    autonomy_estimate = 30 + correction_score * 2 + anticipation_score * 1
    print(f"\nEstimated autonomy: ~{min(autonomy_estimate, 100):.0f}%")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_status()
    elif sys.argv[1] == "check" and len(sys.argv) > 2:
        result = check_response(' '.join(sys.argv[2:]))
        print(json.dumps(result, indent=2))
    elif sys.argv[1] == "correction" and len(sys.argv) > 3:
        log_correction(sys.argv[2], ' '.join(sys.argv[3:]))
        print(f"Logged correction: {sys.argv[2]}")
    elif sys.argv[1] == "anticipate" and len(sys.argv) > 2:
        log_anticipation(' '.join(sys.argv[2:]))
        print(f"Logged anticipation: {sys.argv[2]}")
    elif sys.argv[1] == "resolve" and len(sys.argv) > 3:
        update_anticipation(sys.argv[2], sys.argv[3])
        print(f"Updated anticipation: {sys.argv[2]} -> {sys.argv[3]}")
    elif sys.argv[1] == "status":
        print_status()
    else:
        print("Usage:")
        print("  autonomy-check.py                    # Show status")
        print("  autonomy-check.py status             # Show status")
        print("  autonomy-check.py check <text>       # Check response text")
        print("  autonomy-check.py correction <type> <context>  # Log correction")
        print("  autonomy-check.py anticipate <what>  # Log anticipation")
        print("  autonomy-check.py resolve <what> <correct|incorrect>  # Resolve anticipation")
