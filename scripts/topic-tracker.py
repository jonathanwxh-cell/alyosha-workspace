#!/usr/bin/env python3
"""
Topic Balance Tracker
=====================

Track and enforce topic variety across daemon surfaces.

Usage:
    python3 topic-tracker.py track <category>       # Increment count for category
    python3 topic-tracker.py check <category>       # Check if category over-budget
    python3 topic-tracker.py status                 # Show current week's balance
    python3 topic-tracker.py reset                  # Reset weekly counts (run Sundays)
    python3 topic-tracker.py suggest                # Suggest under-served categories
    python3 topic-tracker.py set-emergent <topic> [rationale]  # Set week's emergent topic

Categories: finance, consciousness, science, philosophy, geopolitics, family, creative, contrarian, emergent
"""

import json
import sys
from datetime import datetime
from pathlib import Path

BALANCE_FILE = Path.home() / '.openclaw/workspace/memory/topic-balance.json'

def load_balance():
    if not BALANCE_FILE.exists():
        return create_default()
    with open(BALANCE_FILE) as f:
        return json.load(f)

def save_balance(data):
    data['meta']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    with open(BALANCE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def create_default():
    return {
        "meta": {
            "purpose": "Track topic variety to prevent over-concentration",
            "rule": "Silence ≠ disengagement. Only downweight on explicit negative signal",
            "lastUpdated": datetime.now().strftime('%Y-%m-%d'),
            "weekStart": datetime.now().strftime('%Y-%m-%d')
        },
        "categories": {
            "finance": {"weeklyTarget": "5-10%", "currentWeekCount": 0, "maxPct": 10},
            "consciousness": {"weeklyTarget": "20-25%", "currentWeekCount": 0, "maxPct": 25, "priority": "high"},
            "science": {"weeklyTarget": "15-20%", "currentWeekCount": 0, "maxPct": 20},
            "philosophy": {"weeklyTarget": "15-20%", "currentWeekCount": 0, "maxPct": 20},
            "geopolitics": {"weeklyTarget": "15-20%", "currentWeekCount": 0, "maxPct": 20},
            "family": {"weeklyTarget": "10-15%", "currentWeekCount": 0, "maxPct": 15},
            "creative": {"weeklyTarget": "10-15%", "currentWeekCount": 0, "maxPct": 15},
            "contrarian": {"weeklyTarget": "5-10%", "currentWeekCount": 0, "maxPct": 10}
        }
    }

def get_total(data):
    return sum(c.get('currentWeekCount', 0) for c in data['categories'].values())

def get_pct(data, category):
    total = get_total(data)
    if total == 0:
        return 0
    count = data['categories'].get(category, {}).get('currentWeekCount', 0)
    return (count / total) * 100

def track(category):
    data = load_balance()
    if category not in data['categories']:
        print(f"❌ Unknown category: {category}")
        print(f"Valid: {', '.join(data['categories'].keys())}")
        return False
    
    data['categories'][category]['currentWeekCount'] += 1
    data['categories'][category]['lastSurface'] = datetime.now().isoformat()
    save_balance(data)
    
    count = data['categories'][category]['currentWeekCount']
    total = get_total(data)
    pct = get_pct(data, category)
    print(f"✅ {category}: {count} surfaces ({pct:.0f}% of {total} total)")
    return True

def check(category):
    data = load_balance()
    if category not in data['categories']:
        print(f"❌ Unknown category: {category}")
        return False
    
    total = get_total(data)
    if total < 3:  # Too few to enforce
        print(f"✅ OK (only {total} surfaces this week, no enforcement yet)")
        return True
    
    pct = get_pct(data, category)
    max_pct = data['categories'][category].get('maxPct', 40)
    
    if pct >= max_pct:
        print(f"⚠️ OVER-BUDGET: {category} at {pct:.0f}% (max {max_pct}%)")
        print(f"   Consider: {suggest_alternatives(data, category)}")
        return False
    elif pct >= max_pct * 0.8:
        print(f"🟡 NEAR LIMIT: {category} at {pct:.0f}% (max {max_pct}%)")
        return True
    else:
        print(f"✅ OK: {category} at {pct:.0f}% (max {max_pct}%)")
        return True

def suggest_alternatives(data, exclude=None):
    """Find under-served categories."""
    total = get_total(data)
    under_served = []
    
    for cat, info in data['categories'].items():
        if cat == exclude:
            continue
        count = info.get('currentWeekCount', 0)
        # Parse target like "15-20%" to get midpoint
        target_str = info.get('weeklyTarget', '10-15%')
        try:
            low, high = target_str.replace('%', '').split('-')
            target_pct = (int(low) + int(high)) / 2
        except:
            target_pct = 15
        
        current_pct = (count / total * 100) if total > 0 else 0
        gap = target_pct - current_pct
        
        if gap > 0:
            under_served.append((cat, gap, info.get('priority', 'normal')))
    
    # Sort by gap (biggest first), then priority
    under_served.sort(key=lambda x: (-1 if x[2] == 'high' else 0, -x[1]))
    
    return ', '.join([cat for cat, _, _ in under_served[:3]]) or 'all balanced'

def status():
    data = load_balance()
    total = get_total(data)
    week_start = data.get('meta', {}).get('weekStart', 'unknown')
    
    print(f"📊 Topic Balance (week of {week_start})")
    print(f"   Total surfaces: {total}\n")
    
    for cat, info in sorted(data['categories'].items(), key=lambda x: -x[1].get('currentWeekCount', 0)):
        count = info.get('currentWeekCount', 0)
        target = info.get('weeklyTarget', '?')
        max_pct = info.get('maxPct', 40)
        pct = (count / total * 100) if total > 0 else 0
        priority = ' ⭐' if info.get('priority') == 'high' else ''
        
        # Special handling for emergent category
        if cat == 'emergent':
            current_topic = info.get('currentTopic')
            if current_topic:
                priority = f' → "{current_topic}"'
            else:
                priority = ' (no topic set)'
        
        # Status indicator
        if pct >= max_pct:
            indicator = '🔴'
        elif pct >= max_pct * 0.8:
            indicator = '🟡'
        elif count == 0 and info.get('priority') == 'high':
            indicator = '⚪'  # Priority but zero
        else:
            indicator = '🟢'
        
        print(f"   {indicator} {cat}: {count} ({pct:.0f}%) — target {target}{priority}")
    
    print(f"\n💡 Under-served: {suggest_alternatives(data)}")

def reset():
    data = load_balance()
    
    # Archive current week
    history_entry = {
        'weekStart': data.get('meta', {}).get('weekStart'),
        'weekEnd': datetime.now().strftime('%Y-%m-%d'),
        'counts': {cat: info.get('currentWeekCount', 0) for cat, info in data['categories'].items()}
    }
    
    if 'weeklyHistory' not in data:
        data['weeklyHistory'] = []
    data['weeklyHistory'].append(history_entry)
    # Keep last 8 weeks
    data['weeklyHistory'] = data['weeklyHistory'][-8:]
    
    # Reset counts
    for cat in data['categories']:
        data['categories'][cat]['currentWeekCount'] = 0
        if 'lastSurface' in data['categories'][cat]:
            del data['categories'][cat]['lastSurface']
    
    data['meta']['weekStart'] = datetime.now().strftime('%Y-%m-%d')
    save_balance(data)
    
    print(f"✅ Reset complete. New week started {datetime.now().strftime('%Y-%m-%d')}")
    print(f"   Archived: {history_entry['counts']}")

def suggest():
    data = load_balance()
    suggestions = suggest_alternatives(data)
    print(f"💡 Suggested topics: {suggestions}")

def set_emergent(topic, rationale=None):
    """Set the emergent topic for the week."""
    data = load_balance()
    if 'emergent' not in data['categories']:
        data['categories']['emergent'] = {
            "description": "Weekly trending topic",
            "weeklyTarget": "10-15%",
            "maxPct": 20,
            "currentWeekCount": 0
        }
    
    data['categories']['emergent']['currentTopic'] = topic
    data['categories']['emergent']['topicSetDate'] = datetime.now().strftime('%Y-%m-%d')
    data['categories']['emergent']['topicRationale'] = rationale
    save_balance(data)
    
    print(f"🔭 Emergent topic set: {topic}")
    if rationale:
        print(f"   Rationale: {rationale}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'track' and len(sys.argv) >= 3:
        track(sys.argv[2].lower())
    elif cmd == 'check' and len(sys.argv) >= 3:
        check(sys.argv[2].lower())
    elif cmd == 'status':
        status()
    elif cmd == 'reset':
        reset()
    elif cmd == 'suggest':
        suggest()
    elif cmd == 'set-emergent' and len(sys.argv) >= 3:
        topic = sys.argv[2]
        rationale = ' '.join(sys.argv[3:]) if len(sys.argv) > 3 else None
        set_emergent(topic, rationale)
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
