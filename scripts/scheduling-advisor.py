#!/usr/bin/env python3
"""
Scheduling Advisor - Smart Surface Decision Engine
===================================================

Provides real-time scheduling decisions for heartbeats:
- Should I surface now? (time scoring)
- What category fits best? (content-time matching)
- Am I in backoff mode? (engagement-based)
- When's the next good window? (planning)

Usage:
    python3 scheduling-advisor.py should-surface [--category CAT]
    python3 scheduling-advisor.py best-category
    python3 scheduling-advisor.py next-window [--category CAT]
    python3 scheduling-advisor.py update-engagement --engaged|--no-reply|--negative
    python3 scheduling-advisor.py status
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCHEDULING_FILE = Path.home() / '.openclaw/workspace/memory/scheduling-intelligence.json'
HEARTBEAT_STATE = Path.home() / '.openclaw/workspace/memory/heartbeat-state.json'
FEEDBACK_LOG = Path.home() / '.openclaw/workspace/memory/feedback-log.jsonl'

# Singapore timezone offset
SGT_OFFSET = 8


def get_sgt_hour():
    """Get current hour in SGT (0-23)."""
    utc_now = datetime.now(timezone.utc)
    sgt_hour = (utc_now.hour + SGT_OFFSET) % 24
    return sgt_hour


def get_sgt_dow():
    """Get day of week in SGT (0=Mon, 6=Sun)."""
    utc_now = datetime.now(timezone.utc)
    sgt_dt = utc_now + timedelta(hours=SGT_OFFSET)
    return sgt_dt.weekday()


def load_config():
    """Load scheduling intelligence config."""
    if not SCHEDULING_FILE.exists():
        return None
    with open(SCHEDULING_FILE) as f:
        return json.load(f)


def save_config(config):
    """Save scheduling intelligence config."""
    with open(SCHEDULING_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_heartbeat_state():
    """Load heartbeat state."""
    if not HEARTBEAT_STATE.exists():
        return {}
    with open(HEARTBEAT_STATE) as f:
        return json.load(f)


def get_recent_engagement(n=10):
    """Calculate rolling engagement rate from recent feedback."""
    if not FEEDBACK_LOG.exists():
        return None, 0
    
    entries = []
    with open(FEEDBACK_LOG) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    # Get recent surfaces and their outcomes
    surfaces = []
    for e in entries:
        if e.get('type') == 'surface':
            surfaces.append({
                'ts': e.get('ts') or e.get('timestamp'),
                'engaged': False,
                'category': e.get('category')
            })
        elif e.get('type') in ('reply', 'reaction'):
            # Mark recent surface as engaged
            for s in reversed(surfaces):
                if not s['engaged']:
                    s['engaged'] = True
                    break
    
    # Calculate rate for last N surfaces
    recent = surfaces[-n:] if len(surfaces) >= n else surfaces
    if not recent:
        return None, 0
    
    engaged_count = sum(1 for s in recent if s['engaged'])
    rate = engaged_count / len(recent)
    return rate, len(recent)


def calculate_time_score(hour, config, dow=None):
    """Calculate score for a given hour."""
    scores = config.get('timeSlotScoring', {}).get('scores', {})
    default = config.get('timeSlotScoring', {}).get('defaultScore', 0.5)
    
    # Get base score
    slot = scores.get(str(hour), {})
    base_score = slot.get('score', default) if isinstance(slot, dict) else slot
    
    # Weekend adjustment
    if dow is not None and dow >= 5:  # Saturday or Sunday
        weekend_weight = config.get('observedPatterns', {}).get('dayOfWeek', {}).get('saturday', {}).get('weight', 0.7)
        base_score *= weekend_weight
    
    return base_score


def get_best_categories_for_hour(hour, config):
    """Get categories that work well at this hour."""
    rules = config.get('contentTimeMatching', {}).get('rules', [])
    matches = []
    
    for rule in rules:
        preferred = rule.get('preferredHours', [])
        if hour in preferred:
            matches.append({
                'category': rule.get('category'),
                'engagement_rate': rule.get('engagementRate', 0.5),
                'reason': rule.get('reason')
            })
    
    # Sort by engagement rate
    matches.sort(key=lambda x: -x['engagement_rate'])
    return matches


def should_surface(category=None):
    """Decide if now is a good time to surface."""
    config = load_config()
    if not config:
        return {'decision': 'unknown', 'reason': 'No config found'}
    
    hour = get_sgt_hour()
    dow = get_sgt_dow()
    
    # Check if in avoid hours
    avoid = config.get('adaptiveRules', {}).get('proactiveSurface', {}).get('avoidHours', [])
    if hour in avoid:
        return {
            'decision': 'no',
            'reason': f'Hour {hour} SGT is in avoid list (sleep/low engagement)',
            'score': 0.0,
            'hour': hour,
            'next_good_hour': find_next_good_hour(hour, config)
        }
    
    # Calculate time score
    time_score = calculate_time_score(hour, config, dow)
    
    # Check rolling engagement for backoff
    engagement_rate, samples = get_recent_engagement()
    backoff_multiplier = 1.0
    
    if engagement_rate is not None:
        adaptive = config.get('adaptiveIntervals', {}).get('adjustments', {})
        
        if engagement_rate < adaptive.get('lowEngagement', {}).get('threshold', 0.3):
            backoff_multiplier = adaptive.get('lowEngagement', {}).get('gapMultiplier', 2.0)
        elif engagement_rate > adaptive.get('highEngagement', {}).get('threshold', 0.7):
            backoff_multiplier = adaptive.get('highEngagement', {}).get('gapMultiplier', 0.8)
    
    # Check category match
    category_bonus = 0
    if category:
        best_cats = get_best_categories_for_hour(hour, config)
        for cat in best_cats:
            if cat['category'] == category:
                category_bonus = 0.2
                break
    
    # Final score
    final_score = (time_score + category_bonus) / backoff_multiplier
    
    # Decision threshold
    threshold = 0.4  # Minimum score to surface
    
    result = {
        'decision': 'yes' if final_score >= threshold else 'wait',
        'score': round(final_score, 2),
        'time_score': round(time_score, 2),
        'engagement_rate': round(engagement_rate, 2) if engagement_rate else None,
        'backoff_multiplier': backoff_multiplier,
        'category_bonus': category_bonus,
        'hour': hour,
        'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dow],
        'is_weekend': dow >= 5
    }
    
    if final_score < threshold:
        result['next_good_hour'] = find_next_good_hour(hour, config)
        result['reason'] = f'Score {final_score:.2f} below threshold {threshold}'
    
    return result


def find_next_good_hour(current_hour, config):
    """Find the next hour with good engagement potential."""
    preferred = config.get('adaptiveRules', {}).get('proactiveSurface', {}).get('preferredHours', [])
    
    for offset in range(1, 24):
        next_hour = (current_hour + offset) % 24
        if next_hour in preferred:
            return next_hour
    
    return (current_hour + 2) % 24  # Default to 2 hours later


def best_category():
    """Get the best category for current time."""
    config = load_config()
    if not config:
        return {'error': 'No config'}
    
    hour = get_sgt_hour()
    matches = get_best_categories_for_hour(hour, config)
    
    return {
        'hour': hour,
        'recommended': matches[:3] if matches else [],
        'fallback': 'create' if not matches else None
    }


def update_engagement_state(outcome):
    """Update rolling engagement state after a surface."""
    config = load_config()
    if not config:
        return {'error': 'No config'}
    
    rate, samples = get_recent_engagement()
    
    # Update rolling engagement in config
    if 'adaptiveIntervals' not in config:
        config['adaptiveIntervals'] = {}
    if 'rollingEngagement' not in config['adaptiveIntervals']:
        config['adaptiveIntervals']['rollingEngagement'] = {}
    
    config['adaptiveIntervals']['rollingEngagement'].update({
        'currentRate': round(rate, 2) if rate else None,
        'windowSize': 10,
        'samples': samples,
        'lastCalculated': datetime.now(timezone.utc).isoformat()
    })
    
    # Update backoff level based on outcome
    adaptive_sched = config.get('adaptiveScheduling', {}).get('backoffRules', {})
    current_backoff = adaptive_sched.get('currentBackoffLevel', 0)
    
    if outcome == 'engaged':
        current_backoff = 0  # Reset on engagement
    elif outcome == 'no-reply':
        current_backoff = min(current_backoff + 0.5, 3)  # Gentle increase
    elif outcome == 'negative':
        current_backoff = min(current_backoff + 2, 5)  # Faster backoff
    
    if 'adaptiveScheduling' not in config:
        config['adaptiveScheduling'] = {}
    if 'backoffRules' not in config['adaptiveScheduling']:
        config['adaptiveScheduling']['backoffRules'] = {}
    
    config['adaptiveScheduling']['backoffRules']['currentBackoffLevel'] = current_backoff
    
    save_config(config)
    
    return {
        'updated': True,
        'rolling_engagement': rate,
        'samples': samples,
        'backoff_level': current_backoff
    }


def status():
    """Get full scheduling status."""
    config = load_config()
    if not config:
        return {'error': 'No config'}
    
    hour = get_sgt_hour()
    dow = get_sgt_dow()
    rate, samples = get_recent_engagement()
    
    backoff = config.get('adaptiveScheduling', {}).get('backoffRules', {}).get('currentBackoffLevel', 0)
    
    return {
        'current_time': {
            'hour_sgt': hour,
            'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dow],
            'is_weekend': dow >= 5
        },
        'engagement': {
            'rolling_rate': round(rate, 2) if rate else None,
            'samples': samples,
            'backoff_level': backoff,
            'interpretation': 'high' if rate and rate > 0.6 else 'normal' if rate and rate > 0.3 else 'low' if rate else 'unknown'
        },
        'time_score': calculate_time_score(hour, config, dow),
        'best_categories': get_best_categories_for_hour(hour, config)[:3],
        'should_surface': should_surface()
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: scheduling-advisor.py <command> [options]")
        print("Commands: should-surface, best-category, update-engagement, status")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'should-surface':
        category = None
        if '--category' in sys.argv:
            idx = sys.argv.index('--category')
            if idx + 1 < len(sys.argv):
                category = sys.argv[idx + 1]
        result = should_surface(category)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'best-category':
        result = best_category()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'update-engagement':
        if '--engaged' in sys.argv:
            outcome = 'engaged'
        elif '--no-reply' in sys.argv:
            outcome = 'no-reply'
        elif '--negative' in sys.argv:
            outcome = 'negative'
        else:
            print("Specify outcome: --engaged, --no-reply, or --negative")
            return
        result = update_engagement_state(outcome)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'status':
        result = status()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
