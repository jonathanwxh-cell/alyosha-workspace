#!/usr/bin/env python3
"""
Delta Detector v2 - Comprehensive state change tracking
Detects meaningful changes across multiple domains
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
DELTA_STATE = WORKSPACE / "memory" / "delta-state.json"

def load_state():
    """Load previous state snapshot"""
    if DELTA_STATE.exists():
        with open(DELTA_STATE) as f:
            return json.load(f)
    return {}

def save_state(state):
    """Save current state snapshot"""
    DELTA_STATE.parent.mkdir(parents=True, exist_ok=True)
    with open(DELTA_STATE, 'w') as f:
        json.dump(state, f, indent=2, default=str)

def get_file_hash(filepath):
    """Get quick hash of file content"""
    try:
        with open(filepath, 'rb') as f:
            import hashlib
            return hashlib.md5(f.read()).hexdigest()[:8]
    except:
        return None

def get_current_state():
    """Collect current state from various sources"""
    state = {
        "timestamp": datetime.now().isoformat(),
        "memory_hashes": {},
        "goals_hash": None,
        "projects_hash": None,
        "exploration_hash": None,
        "heartbeat_state_hash": None,
        "recent_logs": [],
        "cron_errors": 0,
    }
    
    # Track key memory files by content hash (not just mtime)
    memory_dir = WORKSPACE / "memory"
    key_files = [
        "goals.json",
        "active-projects.json",
        "exploration-state.json",
        "curiosities.json",
        "topic-graph.json",
        "surface-budget.json",
    ]
    
    for fname in key_files:
        fpath = memory_dir / fname
        if fpath.exists():
            state["memory_hashes"][fname] = get_file_hash(fpath)
    
    # Check today's daily log size (new entries = growth)
    today = datetime.now().strftime("%Y-%m-%d")
    daily_log = memory_dir / f"{today}.md"
    if daily_log.exists():
        state["daily_log_size"] = daily_log.stat().st_size
    
    # Check for recent research files (last 24h)
    research_dir = WORKSPACE / "memory" / "research"
    if research_dir.exists():
        recent = []
        cutoff = datetime.now() - timedelta(hours=24)
        for f in research_dir.glob("*.md"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if mtime > cutoff:
                recent.append(f.name)
        state["recent_research"] = recent
    
    return state

def compute_deltas(old_state, new_state):
    """Compute meaningful changes between states"""
    deltas = {
        "changed": [],
        "significance": "none"  # none, low, medium, high
    }
    
    if not old_state:
        deltas["changed"].append("🆕 First run - establishing baseline")
        deltas["significance"] = "low"
        return deltas
    
    # Check memory file content changes
    old_hashes = old_state.get("memory_hashes", {})
    new_hashes = new_state.get("memory_hashes", {})
    
    important_files = ["goals.json", "active-projects.json", "exploration-state.json"]
    
    for fname, new_hash in new_hashes.items():
        old_hash = old_hashes.get(fname)
        if old_hash != new_hash:
            if fname in important_files:
                deltas["changed"].append(f"📝 {fname} updated")
                deltas["significance"] = "medium"
            else:
                deltas["changed"].append(f"📄 {fname} changed")
    
    # Check daily log growth (significant new entries)
    old_log_size = old_state.get("daily_log_size", 0)
    new_log_size = new_state.get("daily_log_size", 0)
    if new_log_size - old_log_size > 500:  # >500 bytes of new entries
        deltas["changed"].append(f"📋 Daily log grew by {new_log_size - old_log_size} bytes")
    
    # Check new research
    old_research = set(old_state.get("recent_research", []))
    new_research = set(new_state.get("recent_research", []))
    new_files = new_research - old_research
    if new_files:
        deltas["changed"].append(f"🔬 New research: {', '.join(new_files)}")
        deltas["significance"] = "high"
    
    # Determine overall significance
    if len(deltas["changed"]) >= 3:
        deltas["significance"] = "high"
    elif len(deltas["changed"]) >= 1 and deltas["significance"] == "none":
        deltas["significance"] = "low"
    
    return deltas

def format_output(deltas):
    """Format deltas for display"""
    if not deltas["changed"]:
        return "✨ No significant changes detected."
    
    sig_emoji = {"none": "⚪", "low": "🟡", "medium": "🟠", "high": "🔴"}
    
    output = [f"📊 **Delta Report** [{sig_emoji[deltas['significance']]} {deltas['significance'].upper()}]"]
    output.append("")
    for change in deltas["changed"]:
        output.append(f"  {change}")
    
    return "\n".join(output)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Detect state changes since last heartbeat")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--check-only", action="store_true", help="Don't update state, just check")
    args = parser.parse_args()
    
    old_state = load_state()
    new_state = get_current_state()
    
    deltas = compute_deltas(old_state, new_state)
    
    # Save new state for next comparison (unless check-only)
    if not args.check_only:
        save_state(new_state)
    
    if args.json:
        print(json.dumps(deltas, indent=2))
    else:
        print(format_output(deltas))
    
    # Exit code: 0 = changes found, 1 = no changes
    return 0 if deltas["changed"] else 1

if __name__ == "__main__":
    exit(main())
