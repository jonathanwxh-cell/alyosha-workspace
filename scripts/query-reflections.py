#!/usr/bin/env python3
"""
Query past reflections for relevant lessons before similar tasks.
Part of the Reflexion pattern for self-improving agents.

Usage:
    python3 scripts/query-reflections.py "research"     # Find research lessons
    python3 scripts/query-reflections.py "tool"         # Find tool-building lessons
    python3 scripts/query-reflections.py --recent 5     # Last 5 reflections
    python3 scripts/query-reflections.py --failures     # Only failures
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

REFLECTIONS_FILE = Path.home() / ".openclaw/workspace/memory/reflections.jsonl"

def load_reflections():
    """Load all reflections from JSONL file."""
    if not REFLECTIONS_FILE.exists():
        return []
    
    reflections = []
    with open(REFLECTIONS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    reflections.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return reflections

def search_reflections(query, reflections):
    """Simple keyword search in reflections."""
    query_lower = query.lower()
    matches = []
    
    for r in reflections:
        # Search in task, reflection, and lesson fields
        searchable = ' '.join([
            r.get('task', ''),
            r.get('reflection', ''),
            r.get('lesson', ''),
            r.get('outcome', '')
        ]).lower()
        
        if query_lower in searchable:
            matches.append(r)
    
    return matches

def format_reflection(r):
    """Format a reflection for display."""
    timestamp = r.get('timestamp', 'unknown')[:10]
    task = r.get('task', 'unknown task')
    outcome = r.get('outcome', '?')
    lesson = r.get('lesson', 'no lesson recorded')
    
    emoji = "✅" if outcome == "success" else "⚠️" if outcome == "partial" else "❌"
    return f"{emoji} [{timestamp}] {task}\n   Lesson: {lesson}"

def main():
    args = sys.argv[1:]
    reflections = load_reflections()
    
    if not reflections:
        print("No reflections found. Start logging lessons!")
        return
    
    # Filter modes
    if "--recent" in args:
        idx = args.index("--recent")
        count = int(args[idx + 1]) if idx + 1 < len(args) else 5
        recent = reflections[-count:]
        print(f"📚 Last {len(recent)} reflections:\n")
        for r in recent:
            print(format_reflection(r))
            print()
        return
    
    if "--failures" in args:
        failures = [r for r in reflections if r.get('outcome') in ['failure', 'partial']]
        print(f"❌ {len(failures)} failures/partial successes:\n")
        for r in failures[-10:]:  # Last 10
            print(format_reflection(r))
            print()
        return
    
    if "--stats" in args:
        total = len(reflections)
        successes = len([r for r in reflections if r.get('outcome') == 'success'])
        failures = len([r for r in reflections if r.get('outcome') == 'failure'])
        partial = len([r for r in reflections if r.get('outcome') == 'partial'])
        
        print(f"📊 Reflection Stats:")
        print(f"   Total: {total}")
        print(f"   ✅ Success: {successes} ({100*successes/total:.0f}%)" if total else "")
        print(f"   ⚠️ Partial: {partial} ({100*partial/total:.0f}%)" if total else "")
        print(f"   ❌ Failure: {failures} ({100*failures/total:.0f}%)" if total else "")
        return
    
    # Default: keyword search
    if args and not args[0].startswith('--'):
        query = args[0]
        matches = search_reflections(query, reflections)
        
        if matches:
            print(f"🔍 Found {len(matches)} reflections matching '{query}':\n")
            for r in matches[-5:]:  # Last 5 matches
                print(format_reflection(r))
                print()
        else:
            print(f"No reflections found matching '{query}'")
        return
    
    # No args: show recent
    print("📚 Recent reflections:\n")
    for r in reflections[-5:]:
        print(format_reflection(r))
        print()
    print(f"\nTotal: {len(reflections)} reflections")
    print("Use: --recent N, --failures, --stats, or search term")

if __name__ == "__main__":
    main()
