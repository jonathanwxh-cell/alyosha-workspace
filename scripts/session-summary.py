#!/usr/bin/env python3
"""
Session Summary Generator

Creates a compressed summary of the current session context
to preserve continuity across session rotations.

Usage:
    python3 scripts/session-summary.py generate
    python3 scripts/session-summary.py show
"""

import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
SUMMARY_FILE = WORKSPACE / "memory" / "session-summary.md"

def generate_summary():
    """Generate a session summary from today's context."""
    
    today = datetime.now().strftime("%Y-%m-%d")
    daily_log = WORKSPACE / "memory" / f"{today}.md"
    
    summary_parts = []
    
    # Header
    summary_parts.append(f"# Session Summary — {today}")
    summary_parts.append(f"*Generated: {datetime.now().strftime('%H:%M SGT')}*")
    summary_parts.append("")
    
    # Active projects
    projects_file = WORKSPACE / "memory" / "active-projects.md"
    if projects_file.exists():
        summary_parts.append("## Active Projects")
        content = projects_file.read_text()
        # Extract just the key items
        for line in content.split('\n'):
            if line.startswith('- **') or line.startswith('## '):
                summary_parts.append(line)
        summary_parts.append("")
    
    # Exploration state
    exploration_file = WORKSPACE / "memory" / "exploration-state.json"
    if exploration_file.exists():
        try:
            state = json.loads(exploration_file.read_text())
            if state.get("active_threads"):
                summary_parts.append("## Active Exploration Threads")
                for thread in state["active_threads"][:3]:  # Top 3
                    summary_parts.append(f"- **{thread.get('topic', 'Unknown')}**: {thread.get('lastInsight', 'No insight yet')[:100]}")
                summary_parts.append("")
        except:
            pass
    
    # Recent reflections
    reflections_file = WORKSPACE / "memory" / "reflections.jsonl"
    if reflections_file.exists():
        summary_parts.append("## Recent Lessons")
        lines = reflections_file.read_text().strip().split('\n')
        recent = lines[-5:] if len(lines) >= 5 else lines
        for line in recent:
            try:
                r = json.loads(line)
                if r.get("lesson"):
                    summary_parts.append(f"- {r['lesson'][:100]}")
            except:
                pass
        summary_parts.append("")
    
    # Today's key events
    if daily_log.exists():
        summary_parts.append("## Today's Key Events")
        content = daily_log.read_text()
        # Extract headers (## lines)
        for line in content.split('\n'):
            if line.startswith('## '):
                summary_parts.append(f"- {line[3:]}")
        summary_parts.append("")
    
    # Pending items
    summary_parts.append("## Carry Forward")
    summary_parts.append("- Check active-projects.md for WIP")
    summary_parts.append("- Review exploration-state.json for threads")
    summary_parts.append("- Continue consciousness + LLM research thread")
    summary_parts.append("")
    
    summary = '\n'.join(summary_parts)
    
    # Write to file
    SUMMARY_FILE.write_text(summary)
    print(f"✅ Summary written to {SUMMARY_FILE}")
    print(f"   Size: {len(summary)} chars")
    
    return summary

def show_summary():
    """Display current summary."""
    if SUMMARY_FILE.exists():
        print(SUMMARY_FILE.read_text())
    else:
        print("No summary exists. Run 'generate' first.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 session-summary.py [generate|show]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "generate":
        generate_summary()
    elif cmd == "show":
        show_summary()
    else:
        print(f"Unknown command: {cmd}")
