#!/usr/bin/env python3
"""
Surface Deduplication Tracker
=============================

Track recently surfaced topics to avoid repetition across crons.

Usage:
    python3 surface-tracker.py check "topic"      # Check if surfaced in last N days
    python3 surface-tracker.py add "topic"        # Mark topic as surfaced
    python3 surface-tracker.py list               # Show recent surfaces
    python3 surface-tracker.py clear [days]       # Clear entries older than N days (default 7)

Returns exit code 1 if topic was recently surfaced (use in conditionals).
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

TRACKER_FILE = Path.home() / '.openclaw/workspace/memory/recently-surfaced.json'
DEFAULT_LOOKBACK_DAYS = 3  # Don't repeat within 3 days


def load_tracker():
    if not TRACKER_FILE.exists():
        return {"surfaces": [], "meta": {"created": datetime.now().isoformat()}}
    with open(TRACKER_FILE) as f:
        return json.load(f)


def save_tracker(data):
    data['meta']['updated'] = datetime.now().isoformat()
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def normalize_topic(topic):
    """Normalize topic for matching (lowercase, strip, collapse spaces)."""
    return ' '.join(topic.lower().strip().split())


def check_topic(topic, lookback_days=DEFAULT_LOOKBACK_DAYS):
    """Check if topic was surfaced recently. Returns True if DUPLICATE."""
    data = load_tracker()
    normalized = normalize_topic(topic)
    cutoff = datetime.now() - timedelta(days=lookback_days)
    
    for entry in data.get('surfaces', []):
        entry_time = datetime.fromisoformat(entry['timestamp'])
        if entry_time < cutoff:
            continue
        
        # Check for fuzzy match (topic contains or is contained)
        entry_norm = normalize_topic(entry['topic'])
        if normalized in entry_norm or entry_norm in normalized:
            days_ago = (datetime.now() - entry_time).days
            print(f"⚠️ DUPLICATE: '{topic}' surfaced {days_ago}d ago by {entry.get('source', 'unknown')}")
            return True
    
    print(f"✅ OK: '{topic}' not recently surfaced")
    return False


def add_topic(topic, source=None):
    """Mark topic as surfaced."""
    data = load_tracker()
    
    entry = {
        "topic": topic,
        "timestamp": datetime.now().isoformat(),
        "source": source or "manual"
    }
    
    data['surfaces'].append(entry)
    save_tracker(data)
    print(f"✅ Tracked: '{topic}' from {source or 'manual'}")


def list_recent(days=7):
    """List recently surfaced topics."""
    data = load_tracker()
    cutoff = datetime.now() - timedelta(days=days)
    
    recent = [e for e in data.get('surfaces', []) 
              if datetime.fromisoformat(e['timestamp']) >= cutoff]
    
    if not recent:
        print(f"📭 No surfaces in last {days} days")
        return
    
    print(f"📋 Surfaces (last {days} days):\n")
    for entry in sorted(recent, key=lambda x: x['timestamp'], reverse=True):
        ts = datetime.fromisoformat(entry['timestamp'])
        age = (datetime.now() - ts).days
        src = entry.get('source', '?')
        print(f"   {age}d ago | {src:20} | {entry['topic']}")


def clear_old(days=7):
    """Remove entries older than N days."""
    data = load_tracker()
    cutoff = datetime.now() - timedelta(days=days)
    
    before = len(data.get('surfaces', []))
    data['surfaces'] = [e for e in data.get('surfaces', [])
                        if datetime.fromisoformat(e['timestamp']) >= cutoff]
    after = len(data['surfaces'])
    
    save_tracker(data)
    print(f"🧹 Cleared {before - after} old entries (kept {after})")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'check' and len(sys.argv) >= 3:
        topic = ' '.join(sys.argv[2:])
        is_dup = check_topic(topic)
        sys.exit(1 if is_dup else 0)
    
    elif cmd == 'add' and len(sys.argv) >= 3:
        topic = sys.argv[2]
        source = sys.argv[3] if len(sys.argv) > 3 else None
        add_topic(topic, source)
    
    elif cmd == 'list':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        list_recent(days)
    
    elif cmd == 'clear':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        clear_old(days)
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
