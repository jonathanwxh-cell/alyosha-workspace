#!/usr/bin/env python3
"""
Real Cost Tracker - parses actual session data for accurate cost tracking
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
OUTPUT_FILE = Path(__file__).parent.parent / "memory" / "real-costs.jsonl"

def parse_session_costs(session_file: Path) -> dict:
    """Parse a session file and extract cost data."""
    total_cost = 0.0
    total_input = 0
    total_output = 0
    total_cache_read = 0
    total_cache_write = 0
    model_costs = defaultdict(float)
    turn_count = 0
    
    try:
        with open(session_file) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    usage = msg.get("usage", {})
                    cost = usage.get("cost", {})
                    
                    if cost.get("total"):
                        total_cost += cost["total"]
                        total_input += usage.get("input", 0)
                        total_output += usage.get("output", 0)
                        total_cache_read += usage.get("cacheRead", 0)
                        total_cache_write += usage.get("cacheWrite", 0)
                        model = msg.get("model", "unknown")
                        model_costs[model] += cost["total"]
                        turn_count += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        return {"error": str(e)}
    
    return {
        "file": session_file.name,
        "total_cost": round(total_cost, 4),
        "turns": turn_count,
        "tokens": {
            "input": total_input,
            "output": total_output,
            "cache_read": total_cache_read,
            "cache_write": total_cache_write,
        },
        "by_model": {k: round(v, 4) for k, v in model_costs.items()}
    }

def get_recent_sessions(hours: int = 24) -> list:
    """Get session files modified in the last N hours."""
    cutoff = datetime.now(SGT) - timedelta(hours=hours)
    sessions = []
    
    for f in SESSIONS_DIR.glob("*.jsonl"):
        if f.name.endswith(".lock"):
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=SGT)
        if mtime > cutoff:
            sessions.append((f, mtime))
    
    return sorted(sessions, key=lambda x: x[1], reverse=True)

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    if cmd == "today":
        hours = 24
    elif cmd == "week":
        hours = 168
    elif cmd.isdigit():
        hours = int(cmd)
    else:
        hours = 24
    
    sessions = get_recent_sessions(hours)
    
    if not sessions:
        print(f"No sessions found in last {hours} hours")
        return
    
    total = 0.0
    by_model = defaultdict(float)
    
    print(f"📊 REAL COST REPORT (last {hours}h)")
    print("=" * 50)
    
    for session_file, mtime in sessions:
        costs = parse_session_costs(session_file)
        if "error" in costs:
            continue
        
        total += costs["total_cost"]
        for model, cost in costs.get("by_model", {}).items():
            by_model[model] += cost
        
        if costs["total_cost"] > 0.01:  # Only show sessions with meaningful cost
            print(f"\n{session_file.name[:8]}... ({mtime.strftime('%H:%M SGT')})")
            print(f"  Cost: ${costs['total_cost']:.2f} | Turns: {costs['turns']}")
            print(f"  Tokens: in={costs['tokens']['input']:,} out={costs['tokens']['output']:,}")
    
    print("\n" + "=" * 50)
    print(f"TOTAL: ${total:.2f}")
    print("\nBy model:")
    for model, cost in sorted(by_model.items(), key=lambda x: -x[1]):
        print(f"  {model}: ${cost:.2f}")
    
    # Log to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "a") as f:
        entry = {
            "ts": datetime.now(SGT).isoformat(),
            "hours": hours,
            "total": round(total, 2),
            "by_model": {k: round(v, 2) for k, v in by_model.items()},
            "sessions": len(sessions)
        }
        f.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    main()
