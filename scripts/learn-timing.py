#!/usr/bin/env python3
"""
Adaptive Timing Learner
=======================

Automatically learns optimal scheduling from engagement data.
Updates scheduling-intelligence.json with empirically-derived scores.

Usage:
    python3 scripts/learn-timing.py analyze     # Show analysis without updating
    python3 scripts/learn-timing.py update      # Learn and update config
    python3 scripts/learn-timing.py predict     # Predict best time to surface now
    python3 scripts/learn-timing.py status      # Show current learned state

Runs automatically during weekly maintenance to keep timing optimal.
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict
import math

FEEDBACK_LOG = Path.home() / '.openclaw/workspace/memory/feedback-log.jsonl'
SCHEDULING_FILE = Path.home() / '.openclaw/workspace/memory/scheduling-intelligence.json'
LEARNING_STATE = Path.home() / '.openclaw/workspace/memory/timing-learner-state.json'

SGT_OFFSET = 8

def load_feedback():
    """Load all feedback entries."""
    entries = []
    if not FEEDBACK_LOG.exists():
        return entries
    with open(FEEDBACK_LOG) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    return entries


def load_scheduling():
    """Load current scheduling config."""
    if not SCHEDULING_FILE.exists():
        return {}
    with open(SCHEDULING_FILE) as f:
        return json.load(f)


def save_scheduling(config):
    """Save scheduling config."""
    with open(SCHEDULING_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_hour_from_entry(entry):
    """Extract SGT hour from entry."""
    if 'hourSGT' in entry:
        return entry['hourSGT']
    
    # Parse timestamp
    ts = entry.get('ts') or entry.get('timestamp')
    if ts:
        try:
            if ts.endswith('Z'):
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(ts)
            sgt_hour = (dt.hour + SGT_OFFSET) % 24
            return sgt_hour
        except:
            pass
    return None


def get_day_from_entry(entry):
    """Extract day of week (0=Mon, 6=Sun) from entry."""
    ts = entry.get('ts') or entry.get('timestamp')
    if ts:
        try:
            if ts.endswith('Z'):
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(ts)
            sgt_dt = dt + timedelta(hours=SGT_OFFSET)
            return sgt_dt.weekday()
        except:
            pass
    return None


def is_positive_engagement(entry):
    """Determine if entry represents positive engagement."""
    entry_type = entry.get('type', '')
    
    if entry_type == 'reply':
        return True
    
    if entry_type == 'reaction':
        emoji = entry.get('emoji', '')
        negative = ['👎', '😴', '🤔']  # 🤔 is uncertain, not clearly positive
        return emoji not in negative
    
    # Instructions, preferences count as engagement
    if entry_type in ['instruction', 'preference', 'request']:
        return True
    
    return False


def analyze_by_hour(entries):
    """Compute engagement rate by hour."""
    hour_stats = defaultdict(lambda: {'engaged': 0, 'total': 0, 'fast_replies': 0})
    
    for entry in entries:
        hour = get_hour_from_entry(entry)
        if hour is None:
            continue
        
        entry_type = entry.get('type', '')
        
        # Count surfaces
        if entry_type == 'surface':
            hour_stats[hour]['total'] += 1
            if entry.get('gotReply', False):
                hour_stats[hour]['engaged'] += 1
        
        # Count engagements
        elif is_positive_engagement(entry):
            hour_stats[hour]['engaged'] += 1
            hour_stats[hour]['total'] += 1
            if entry.get('replySpeed') == 'fast':
                hour_stats[hour]['fast_replies'] += 1
    
    return dict(hour_stats)


def analyze_by_day(entries):
    """Compute engagement rate by day of week."""
    day_stats = defaultdict(lambda: {'engaged': 0, 'total': 0})
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    for entry in entries:
        day = get_day_from_entry(entry)
        if day is None:
            continue
        
        if is_positive_engagement(entry):
            day_stats[day]['engaged'] += 1
        
        day_stats[day]['total'] += 1
    
    return {day_names[k]: v for k, v in sorted(day_stats.items())}


def analyze_by_category(entries):
    """Compute engagement rate by category."""
    cat_stats = defaultdict(lambda: {'engaged': 0, 'total': 0})
    
    for entry in entries:
        cat = entry.get('category')
        if not cat:
            continue
        
        cat_stats[cat]['total'] += 1
        if is_positive_engagement(entry):
            cat_stats[cat]['engaged'] += 1
    
    return dict(cat_stats)


def compute_score(engaged, total, prior_score=0.5, prior_weight=2):
    """
    Bayesian score update: blend prior with observed data.
    More samples = less weight on prior.
    """
    if total == 0:
        return prior_score
    
    observed_rate = engaged / total
    
    # Weighted blend: prior matters less as samples increase
    effective_prior = prior_weight / (prior_weight + total)
    score = effective_prior * prior_score + (1 - effective_prior) * observed_rate
    
    return round(score, 3)


def compute_confidence(samples):
    """Confidence level based on sample size."""
    if samples >= 20:
        return 'high'
    elif samples >= 10:
        return 'medium'
    elif samples >= 3:
        return 'low'
    else:
        return 'insufficient'


def predict_best_time(hour_scores, current_hour=None):
    """Predict best time to surface based on learned scores."""
    if current_hour is None:
        utc_now = datetime.now(timezone.utc)
        current_hour = (utc_now.hour + SGT_OFFSET) % 24
    
    # Filter to waking hours (8-23 SGT)
    candidates = []
    for hour in range(8, 24):
        score_info = hour_scores.get(str(hour), {})
        score = score_info.get('score', 0.5)
        samples = score_info.get('samples', 0)
        confidence = compute_confidence(samples)
        
        # Penalize low-confidence scores
        if confidence == 'insufficient':
            effective_score = 0.5  # Default to neutral
        elif confidence == 'low':
            effective_score = 0.5 + (score - 0.5) * 0.5  # Shrink toward mean
        else:
            effective_score = score
        
        candidates.append({
            'hour': hour,
            'score': effective_score,
            'raw_score': score,
            'confidence': confidence,
            'samples': samples
        })
    
    # Sort by score
    candidates.sort(key=lambda x: -x['score'])
    
    return candidates


def run_analysis():
    """Analyze engagement patterns."""
    entries = load_feedback()
    
    if not entries:
        print("📭 No feedback data found")
        return
    
    print(f"📊 Analyzing {len(entries)} feedback entries\n")
    
    # By hour
    hour_stats = analyze_by_hour(entries)
    print("⏰ ENGAGEMENT BY HOUR (SGT):")
    print("-" * 50)
    for hour in sorted(hour_stats.keys()):
        stats = hour_stats[hour]
        rate = stats['engaged'] / stats['total'] if stats['total'] > 0 else 0
        confidence = compute_confidence(stats['total'])
        bar = '█' * int(rate * 20)
        print(f"  {hour:02d}:00  {bar:20} {rate:.0%} ({stats['total']} samples, {confidence})")
    
    # By day
    print("\n📅 ENGAGEMENT BY DAY:")
    print("-" * 50)
    day_stats = analyze_by_day(entries)
    for day, stats in day_stats.items():
        rate = stats['engaged'] / stats['total'] if stats['total'] > 0 else 0
        bar = '█' * int(rate * 20)
        print(f"  {day:3}  {bar:20} {rate:.0%} ({stats['total']} samples)")
    
    # By category
    print("\n📁 ENGAGEMENT BY CATEGORY:")
    print("-" * 50)
    cat_stats = analyze_by_category(entries)
    for cat, stats in sorted(cat_stats.items(), key=lambda x: -x[1]['engaged']/max(x[1]['total'],1)):
        rate = stats['engaged'] / stats['total'] if stats['total'] > 0 else 0
        conf = compute_confidence(stats['total'])
        print(f"  {cat:25} {rate:.0%} ({stats['total']} samples, {conf})")
    
    # Predictions
    print("\n🎯 PREDICTED BEST HOURS:")
    print("-" * 50)
    config = load_scheduling()
    hour_scores = config.get('timeSlotScoring', {}).get('scores', {})
    candidates = predict_best_time(hour_scores)[:5]
    for c in candidates:
        print(f"  {c['hour']:02d}:00 SGT — score {c['score']:.2f} ({c['confidence']} confidence)")


def run_update():
    """Learn from data and update scheduling config."""
    entries = load_feedback()
    config = load_scheduling()
    
    if not entries:
        print("📭 No feedback data to learn from")
        return
    
    print(f"🧠 Learning from {len(entries)} feedback entries...")
    
    # Analyze
    hour_stats = analyze_by_hour(entries)
    day_stats = analyze_by_day(entries)
    cat_stats = analyze_by_category(entries)
    
    # Update hour scores
    if 'timeSlotScoring' not in config:
        config['timeSlotScoring'] = {'enabled': True, 'scores': {}}
    
    scores = config['timeSlotScoring'].get('scores', {})
    
    for hour, stats in hour_stats.items():
        prior = scores.get(str(hour), {}).get('score', 0.5)
        new_score = compute_score(stats['engaged'], stats['total'], prior)
        confidence = compute_confidence(stats['total'])
        
        scores[str(hour)] = {
            'score': new_score,
            'samples': stats['total'],
            'engaged': stats['engaged'],
            'confidence': confidence,
            'lastUpdated': datetime.now().isoformat()
        }
    
    config['timeSlotScoring']['scores'] = scores
    
    # Update category engagement
    if 'observedPatterns' not in config:
        config['observedPatterns'] = {}
    
    config['observedPatterns']['categoryEngagement'] = {
        'data': {cat: stats for cat, stats in cat_stats.items()},
        'lastUpdated': datetime.now().isoformat()
    }
    
    # Update day-of-week patterns
    config['observedPatterns']['dayEngagement'] = {
        'data': day_stats,
        'lastUpdated': datetime.now().isoformat()
    }
    
    # Add meta
    config['meta']['lastLearningUpdate'] = datetime.now().isoformat()
    config['meta']['learningDataPoints'] = len(entries)
    
    save_scheduling(config)
    
    print("✅ Updated scheduling-intelligence.json")
    print(f"   Hours updated: {len(hour_stats)}")
    print(f"   Categories tracked: {len(cat_stats)}")
    
    # Show top hours
    print("\n🎯 Top hours by learned score:")
    sorted_hours = sorted(scores.items(), key=lambda x: -x[1].get('score', 0))[:5]
    for hour, info in sorted_hours:
        print(f"   {hour}:00 SGT — {info['score']:.2f} ({info.get('confidence', '?')})")


def run_predict():
    """Predict best time to surface right now."""
    config = load_scheduling()
    hour_scores = config.get('timeSlotScoring', {}).get('scores', {})
    
    utc_now = datetime.now(timezone.utc)
    current_hour = (utc_now.hour + SGT_OFFSET) % 24
    
    print(f"🕐 Current time: {current_hour:02d}:00 SGT\n")
    
    candidates = predict_best_time(hour_scores, current_hour)
    
    # Find current hour score
    current_info = next((c for c in candidates if c['hour'] == current_hour), None)
    
    if current_info:
        print(f"📍 Current hour score: {current_info['score']:.2f} ({current_info['confidence']})")
    
    print("\n🎯 Best upcoming windows:")
    shown = 0
    for c in candidates:
        if c['hour'] >= current_hour and shown < 5:
            marker = "← NOW" if c['hour'] == current_hour else ""
            print(f"   {c['hour']:02d}:00 — score {c['score']:.2f} ({c['confidence']}) {marker}")
            shown += 1
    
    # Recommendation
    best = candidates[0]
    if best['score'] >= 0.7:
        print(f"\n✅ Recommendation: Good to surface now or at {best['hour']:02d}:00")
    elif best['score'] >= 0.5:
        print(f"\n🟡 Recommendation: Moderate timing, {best['hour']:02d}:00 is slightly better")
    else:
        print(f"\n⚠️  Recommendation: Consider waiting for better window")


def run_status():
    """Show current learned state."""
    config = load_scheduling()
    
    meta = config.get('meta', {})
    print("📊 Timing Learner Status\n")
    print(f"Last learning update: {meta.get('lastLearningUpdate', 'Never')}")
    print(f"Data points used: {meta.get('learningDataPoints', 0)}")
    
    scores = config.get('timeSlotScoring', {}).get('scores', {})
    
    high_conf = sum(1 for s in scores.values() if s.get('confidence') == 'high')
    med_conf = sum(1 for s in scores.values() if s.get('confidence') == 'medium')
    low_conf = sum(1 for s in scores.values() if s.get('confidence') == 'low')
    
    print(f"\nHour scores: {len(scores)} tracked")
    print(f"  High confidence: {high_conf}")
    print(f"  Medium confidence: {med_conf}")
    print(f"  Low confidence: {low_conf}")
    
    # Top/bottom hours
    sorted_scores = sorted(scores.items(), key=lambda x: -x[1].get('score', 0))
    
    print("\n🏆 Best hours:")
    for h, s in sorted_scores[:3]:
        print(f"   {h}:00 — {s['score']:.2f}")
    
    print("\n⚠️  Worst hours:")
    for h, s in sorted_scores[-3:]:
        print(f"   {h}:00 — {s['score']:.2f}")


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help']:
        print(__doc__)
        return
    
    cmd = args[0].lower()
    
    if cmd == 'analyze':
        run_analysis()
    elif cmd == 'update':
        run_update()
    elif cmd == 'predict':
        run_predict()
    elif cmd == 'status':
        run_status()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
