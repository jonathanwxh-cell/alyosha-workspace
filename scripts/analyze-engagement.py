#!/usr/bin/env python3
"""
Analyze engagement patterns from feedback-log.jsonl
Updates scheduling-intelligence.json with learned patterns
"""

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/ubuntu/.openclaw/workspace")
FEEDBACK_LOG = WORKSPACE / "memory/feedback-log.jsonl"
SCHEDULING_FILE = WORKSPACE / "memory/scheduling-intelligence.json"

def load_feedback():
    """Load feedback entries from jsonl"""
    entries = []
    if FEEDBACK_LOG.exists():
        with open(FEEDBACK_LOG) as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    return entries

def analyze_patterns(entries):
    """Analyze engagement patterns"""
    
    # Hour analysis (SGT)
    reply_hours = []
    fast_reply_hours = []
    reaction_hours = defaultdict(list)
    
    for e in entries:
        hour = e.get('hourSGT')
        if hour is None:
            # Try to extract from timestamp
            ts = e.get('ts', '')
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    # Convert UTC to SGT (+8)
                    hour = (dt.hour + 8) % 24
                except:
                    continue
        
        if e['type'] == 'reply':
            reply_hours.append(hour)
            if e.get('replySpeed') == 'fast':
                fast_reply_hours.append(hour)
        
        elif e['type'] == 'reaction':
            emoji = e.get('emoji', '')
            reaction_hours[emoji].append(hour)
    
    # Category analysis
    category_engagement = Counter()
    for e in entries:
        if e['type'] in ['reply', 'reaction']:
            cat = e.get('category', 'unknown')
            if e['type'] == 'reaction' and e.get('emoji') in ['👍', '🔥', '👏']:
                category_engagement[cat] += 2  # Positive reaction = 2 points
            elif e['type'] == 'reply':
                category_engagement[cat] += 1
    
    return {
        'reply_hours': Counter(reply_hours),
        'fast_reply_hours': Counter(fast_reply_hours),
        'positive_reaction_hours': Counter(reaction_hours.get('👍', []) + reaction_hours.get('🔥', []) + reaction_hours.get('👏', [])),
        'category_engagement': category_engagement,
        'total_entries': len(entries)
    }

def update_scheduling(patterns):
    """Update scheduling-intelligence.json with new patterns"""
    
    if SCHEDULING_FILE.exists():
        with open(SCHEDULING_FILE) as f:
            config = json.load(f)
    else:
        config = {}
    
    # Update observed patterns
    if 'observedPatterns' not in config:
        config['observedPatterns'] = {}
    
    # Top hours for fast replies
    fast_hours = [h for h, _ in patterns['fast_reply_hours'].most_common(6)]
    config['observedPatterns']['fastReplies'] = {
        'hours': fast_hours,
        'note': f"SGT hours with fast replies (n={sum(patterns['fast_reply_hours'].values())})"
    }
    
    # Top categories
    top_cats = [cat for cat, _ in patterns['category_engagement'].most_common(5)]
    config['observedPatterns']['topCategories'] = {
        'categories': top_cats,
        'note': "Categories with highest engagement"
    }
    
    # Update metadata
    config['meta'] = config.get('meta', {})
    config['meta']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    config['meta']['dataPoints'] = patterns['total_entries']
    
    with open(SCHEDULING_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config

def main():
    print("=== Engagement Pattern Analysis ===")
    
    entries = load_feedback()
    print(f"Loaded {len(entries)} feedback entries")
    
    if len(entries) < 5:
        print("Insufficient data for analysis (need >= 5 entries)")
        return
    
    patterns = analyze_patterns(entries)
    
    print(f"\nReply hours (SGT): {dict(patterns['reply_hours'])}")
    print(f"Fast reply hours (SGT): {dict(patterns['fast_reply_hours'])}")
    print(f"Category engagement: {dict(patterns['category_engagement'])}")
    
    config = update_scheduling(patterns)
    print(f"\nUpdated scheduling-intelligence.json")
    print(f"Top engagement hours: {config['observedPatterns'].get('fastReplies', {}).get('hours', [])}")

if __name__ == '__main__':
    main()
