#!/usr/bin/env python3
"""
Session Rotation Monitor
Alerts when context exceeds threshold, recommends restart
Generates session summary before rotation for continuity
"""

import subprocess
import json
import sys
from pathlib import Path

THRESHOLD = 40  # percent

def check_session():
    result = subprocess.run(
        ["openclaw", "sessions", "--json", "--active", "60"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    
    try:
        data = json.loads(result.stdout)
        sessions = data.get("sessions", [])
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

def generate_summary():
    """Generate session summary before rotation."""
    try:
        script = Path(__file__).parent / "session-summary.py"
        result = subprocess.run(
            ["python3", str(script), "generate"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return True
    except:
        pass
    return False

def main():
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else THRESHOLD
    session = check_session()
    
    if not session:
        print("Could not get session info")
        return 0
    
    pct = session["percent"]
    print(f"Context: {pct}% ({session['tokens']:,} / {session['context']:,})")
    
    if pct >= threshold:
        # Generate summary for continuity
        if generate_summary():
            print("📝 Session summary saved to memory/session-summary.md")
        
        print(f"\n⚠️ ROTATION RECOMMENDED")
        print(f"Context at {pct}% exceeds {threshold}% threshold")
        print("Action: Restart gateway to reset session")
        return 1
    else:
        print(f"✓ OK (threshold: {threshold}%)")
        return 0

if __name__ == "__main__":
    sys.exit(main())
