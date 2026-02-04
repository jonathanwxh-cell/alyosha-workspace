#!/usr/bin/env python3
"""
Context Monitor - alerts when session context exceeds threshold
"""

import json
import subprocess
import sys

THRESHOLD = 50  # percent

def get_main_session():
    """Get main session context usage."""
    result = subprocess.run(
        ["openclaw", "sessions", "--json", "--active", "60"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    
    try:
        sessions = json.loads(result.stdout)
        for s in sessions:
            if s.get("key") == "agent:main:main":
                total = s.get("totalTokens", 0)
                context = s.get("contextTokens", 200000)
                pct = (total / context) * 100 if context > 0 else 0
                return {
                    "key": s["key"],
                    "tokens": total,
                    "context": context,
                    "percent": round(pct, 1),
                    "session_id": s.get("sessionId", "unknown")
                }
    except:
        pass
    return None

def main():
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else THRESHOLD
    
    session = get_main_session()
    if not session:
        print("Could not get session info")
        return
    
    print(f"Context: {session['percent']}% ({session['tokens']:,} / {session['context']:,})")
    
    if session['percent'] >= threshold:
        print(f"⚠️ ALERT: Context at {session['percent']}% (threshold: {threshold}%)")
        print(f"Session: {session['session_id'][:8]}...")
        print("Recommend: Restart gateway to reset session")
        return 1
    else:
        print(f"✓ OK (threshold: {threshold}%)")
        return 0

if __name__ == "__main__":
    sys.exit(main() or 0)
