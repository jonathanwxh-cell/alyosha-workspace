#!/usr/bin/env python3
"""
Session Rotation Monitor
Alerts when context exceeds threshold, recommends restart
"""

import subprocess
import json
import sys

THRESHOLD = 40  # percent

def check_session():
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
                    "percent": round(pct, 1),
                    "tokens": total,
                    "context": context
                }
    except:
        pass
    return None

def main():
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else THRESHOLD
    session = check_session()
    
    if not session:
        print("Could not get session info")
        return 0
    
    pct = session["percent"]
    print(f"Context: {pct}% ({session['tokens']:,} / {session['context']:,})")
    
    if pct >= threshold:
        print(f"\n⚠️ ROTATION RECOMMENDED")
        print(f"Context at {pct}% exceeds {threshold}% threshold")
        print("Action: Restart gateway to reset session")
        print("Command: openclaw gateway restart")
        return 1
    else:
        print(f"✓ OK (threshold: {threshold}%)")
        return 0

if __name__ == "__main__":
    sys.exit(main())
