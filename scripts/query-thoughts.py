#!/usr/bin/env python3
"""
Query the thought log.

Usage:
  query-thoughts.py --date 2026-02-02          # All entries on date
  query-thoughts.py --entity "jon"             # All mentioning entity
  query-thoughts.py --type decision            # All decisions
  query-thoughts.py --tag "investing"          # All with tag
  query-thoughts.py --search "vector"          # Text search
  query-thoughts.py --recent 5                 # Last N entries
  query-thoughts.py --questions                # Open questions
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

THOUGHTS_DIR = Path.home() / ".openclaw/workspace/memory/thoughts"

def load_all_entries():
    entries = []
    for f in sorted(THOUGHTS_DIR.glob("*.jsonl")):
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    entries.append(json.loads(line))
    return entries

def filter_entries(entries, args):
    results = entries
    
    if args.date:
        results = [e for e in results if e.get("ts", "").startswith(args.date)]
    
    if args.entity:
        entity = args.entity.lower()
        results = [e for e in results if entity in [x.lower() for x in e.get("entities", [])]]
    
    if args.type:
        results = [e for e in results if e.get("type") == args.type]
    
    if args.tag:
        tag = args.tag.lower()
        results = [e for e in results if tag in [x.lower() for x in e.get("tags", [])]]
    
    if args.search:
        search = args.search.lower()
        results = [e for e in results if search in json.dumps(e).lower()]
    
    if args.questions:
        results = [e for e in results if e.get("type") == "question" and e.get("status") == "open"]
    
    if args.recent:
        results = results[-args.recent:]
    
    return results

def format_entry(e):
    ts = e.get("ts", "")[:19].replace("T", " ")
    t = e.get("type", "?")
    
    if t == "conversation":
        return f"[{ts}] 💬 {e.get('topic')}: {e.get('summary')}"
    elif t == "thought":
        return f"[{ts}] 💭 {e.get('content')}"
    elif t == "decision":
        return f"[{ts}] ⚖️ {e.get('what')} — {e.get('why')}"
    elif t == "question":
        status = "❓" if e.get("status") == "open" else "✅"
        return f"[{ts}] {status} {e.get('question')}"
    elif t == "connection":
        return f"[{ts}] 🔗 {e.get('from')} → {e.get('to')}: {e.get('relationship')}"
    else:
        return f"[{ts}] {t}: {json.dumps(e)[:100]}"

def main():
    parser = argparse.ArgumentParser(description="Query thought log")
    parser.add_argument("--date", help="Filter by date (YYYY-MM-DD)")
    parser.add_argument("--entity", help="Filter by entity")
    parser.add_argument("--type", help="Filter by type")
    parser.add_argument("--tag", help="Filter by tag")
    parser.add_argument("--search", help="Text search")
    parser.add_argument("--recent", type=int, help="Last N entries")
    parser.add_argument("--questions", action="store_true", help="Open questions only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    entries = load_all_entries()
    results = filter_entries(entries, args)
    
    if not results:
        print("No entries found.")
        return
    
    print(f"Found {len(results)} entries:\n")
    
    for e in results:
        if args.json:
            print(json.dumps(e, indent=2))
        else:
            print(format_entry(e))
    
if __name__ == "__main__":
    main()
