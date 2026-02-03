#!/usr/bin/env python3
"""
Engagement Pattern Analyzer
============================

Analyzes feedback-log.jsonl to find optimal timing patterns.
Updates scheduling-intelligence.json with learned patterns.

Usage:
    python3 analyze-engagement.py           # Analyze and show patterns
    python3 analyze-engagement.py --update  # Update scheduling-intelligence.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

FEEDBACK_LOG = Path.home() / '.openclaw/workspace/memory/feedback-log.jsonl'
SCHEDULING_FILE = Path.home() / '.openclaw/workspace/memory/scheduling-intelligence.json'


def load_feedback():
    """Load feedback log entries."""
    entries = []
    if not FEEDBACK_LOG.exists():
        return entries
    
    with open(FEEDBACK_LOG) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def analyze_patterns(entries):
    """Analyze engagement patterns from feedback."""
    
    # Hour-based engagement (SGT)
    hour_stats = defaultdict(lambda: {'engaged': 0, 'total': 0, 'fast_replies': 0})
    
    # Category engagement
    category_stats = defaultdict(lambda: {'engaged': 0, 'total': 0})
    
    # Day of week (0=Mon, 6=Sun)
    dow_stats = defaultdict(lambda: {'engaged': 0, 'total': 0})
    
    # Content type x time matching
    content_time = defaultdict(lambda: defaultdict(lambda: {'engaged': 0, 'total': 0}))
    
    for e in entries:
        typ = e.get('type')
        hour = e.get('hourSGT')
        cat = e.get('category', 'unknown')
        speed = e.get('replySpeed')
        
        # Parse timestamp for day of week
        ts = e.get('ts') or e.get('timestamp')
        dow = None
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                # Convert to SGT (UTC+8)
                dow = (dt.weekday() + (8 // 24)) % 7  # Rough approximation
            except:
                pass
        
        # Track engagement by hour
        if hour is not None:
            if typ in ('reply', 'reaction'):
                hour_stats[hour]['engaged'] += 1
                hour_stats[hour]['total'] += 1
                if speed == 'fast':
                    hour_stats[hour]['fast_replies'] += 1
            elif typ == 'surface':
                hour_stats[hour]['total'] += 1
        
        # Track by category
        if typ in ('reply', 'reaction'):
            category_stats[cat]['engaged'] += 1
            category_stats[cat]['total'] += 1
        elif typ == 'surface':
            category_stats[cat]['total'] += 1
        
        # Track by day of week
        if dow is not None:
            if typ in ('reply', 'reaction'):
                dow_stats[dow]['engaged'] += 1
                dow_stats[dow]['total'] += 1
            elif typ == 'surface':
                dow_stats[dow]['total'] += 1
        
        # Track content x time
        if hour is not None and cat:
            if typ in ('reply', 'reaction'):
                content_time[cat][hour]['engaged'] += 1
                content_time[cat][hour]['total'] += 1
            elif typ == 'surface':
                content_time[cat][hour]['total'] += 1
    
    return {
        'hour_stats': dict(hour_stats),
        'category_stats': dict(category_stats),
        'dow_stats': dict(dow_stats),
        'content_time': {k: dict(v) for k, v in content_time.items()},
        'total_entries': len(entries)
    }


def calculate_optimal_hours(hour_stats, min_data=2):
    """Calculate optimal hours based on engagement rate."""
    scored_hours = []
    
    for hour, stats in hour_stats.items():
        if stats['total'] >= min_data:
            rate = stats['engaged'] / stats['total']
            fast_rate = stats['fast_replies'] / stats['total'] if stats['total'] > 0 else 0
            # Score = engagement rate + bonus for fast replies
            score = rate + (fast_rate * 0.5)
            scored_hours.append((hour, score, rate, stats['total']))
    
    # Sort by score descending
    scored_hours.sort(key=lambda x: -x[1])
    
    return scored_hours


def generate_recommendations(patterns):
    """Generate scheduling recommendations from patterns."""
    recommendations = {
        'optimal_hours': [],
        'avoid_hours': [],
        'category_timing': {},
        'confidence': 'low'  # low/medium/high based on data volume
    }
    
    # Confidence based on data volume
    total = patterns['total_entries']
    if total >= 50:
        recommendations['confidence'] = 'high'
    elif total >= 20:
        recommendations['confidence'] = 'medium'
    else:
        recommendations['confidence'] = 'low'
    
    # Optimal hours
    scored = calculate_optimal_hours(patterns['hour_stats'], min_data=1)
    if scored:
        recommendations['optimal_hours'] = [h for h, s, r, n in scored[:5] if r >= 0.5]
        recommendations['avoid_hours'] = [h for h, s, r, n in scored if r < 0.3]
    
    # Category recommendations
    for cat, stats in patterns['category_stats'].items():
        if stats['total'] >= 2:
            rate = stats['engaged'] / stats['total']
            recommendations['category_timing'][cat] = {
                'engagement_rate': round(rate, 2),
                'sample_size': stats['total'],
                'recommendation': 'high_value' if rate >= 0.7 else 'normal' if rate >= 0.4 else 'reduce'
            }
    
    return recommendations


def calculate_rolling_engagement(entries, window=10):
    """Calculate rolling engagement rate from recent surfaces."""
    surfaces = []
    for e in entries:
        if e.get('type') == 'surface':
            surfaces.append({
                'ts': e.get('ts') or e.get('timestamp'),
                'engaged': False,
                'category': e.get('category')
            })
        elif e.get('type') in ('reply', 'reaction'):
            # Mark most recent unengaged surface as engaged
            for s in reversed(surfaces):
                if not s['engaged']:
                    s['engaged'] = True
                    break
    
    recent = surfaces[-window:] if len(surfaces) >= window else surfaces
    if not recent:
        return None, 0
    
    engaged_count = sum(1 for s in recent if s['engaged'])
    return engaged_count / len(recent), len(recent)


def update_scheduling_file(recommendations, patterns):
    """Update scheduling-intelligence.json with learned patterns."""
    if not SCHEDULING_FILE.exists():
        print("Scheduling file not found")
        return False
    
    with open(SCHEDULING_FILE) as f:
        config = json.load(f)
    
    # Update observed patterns
    if 'observedPatterns' not in config:
        config['observedPatterns'] = {}
    
    config['observedPatterns']['hourEngagement'] = {
        'data': patterns['hour_stats'],
        'optimal': recommendations['optimal_hours'],
        'avoid': recommendations['avoid_hours'],
        'confidence': recommendations['confidence'],
        'lastUpdated': datetime.now().isoformat()
    }
    
    config['observedPatterns']['categoryEngagement'] = {
        'data': {k: v for k, v in patterns['category_stats'].items()},
        'recommendations': recommendations['category_timing'],
        'lastUpdated': datetime.now().isoformat()
    }
    
    # Update adaptive rules if high confidence
    if recommendations['confidence'] in ('medium', 'high'):
        if recommendations['optimal_hours']:
            config['adaptiveRules']['proactiveSurface']['preferredHours'] = (
                recommendations['optimal_hours'] + 
                [h for h in range(8, 23) if h not in recommendations['avoid_hours']]
            )
    
    # Calculate and update rolling engagement
    entries = load_feedback()
    rolling_rate, samples = calculate_rolling_engagement(entries)
    
    if 'adaptiveIntervals' not in config:
        config['adaptiveIntervals'] = {}
    if 'rollingEngagement' not in config['adaptiveIntervals']:
        config['adaptiveIntervals']['rollingEngagement'] = {}
    
    config['adaptiveIntervals']['rollingEngagement'].update({
        'currentRate': round(rolling_rate, 2) if rolling_rate else None,
        'windowSize': 10,
        'samples': samples,
        'lastCalculated': datetime.now().isoformat()
    })
    
    # Update meta
    config['meta']['lastUpdated'] = datetime.now().strftime('%Y-%m-%d')
    config['meta']['dataPoints'] = patterns['total_entries']
    
    with open(SCHEDULING_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    return True


def main():
    update_mode = '--update' in sys.argv
    
    entries = load_feedback()
    if not entries:
        print("No feedback data found")
        return
    
    patterns = analyze_patterns(entries)
    recommendations = generate_recommendations(patterns)
    
    print(f"=== Engagement Analysis ({patterns['total_entries']} data points) ===\n")
    
    print("Hour Engagement (SGT):")
    for hour in sorted(patterns['hour_stats'].keys()):
        stats = patterns['hour_stats'][hour]
        rate = stats['engaged'] / stats['total'] if stats['total'] > 0 else 0
        bar = '█' * int(rate * 10)
        print(f"  {hour:02d}:00  {bar:<10} {rate:.0%} (n={stats['total']})")
    
    print("\nCategory Engagement:")
    sorted_cats = sorted(patterns['category_stats'].items(), 
                        key=lambda x: -x[1]['engaged']/max(x[1]['total'],1))
    for cat, stats in sorted_cats:
        rate = stats['engaged'] / stats['total'] if stats['total'] > 0 else 0
        rec = recommendations['category_timing'].get(cat, {}).get('recommendation', '?')
        print(f"  {cat:<20} {rate:.0%} (n={stats['total']}) → {rec}")
    
    print(f"\nConfidence: {recommendations['confidence']}")
    print(f"Optimal hours: {recommendations['optimal_hours'] or 'insufficient data'}")
    print(f"Avoid hours: {recommendations['avoid_hours'] or 'none identified'}")
    
    if update_mode:
        if update_scheduling_file(recommendations, patterns):
            print("\n✅ Updated scheduling-intelligence.json")
        else:
            print("\n❌ Failed to update scheduling file")


if __name__ == '__main__':
    main()
