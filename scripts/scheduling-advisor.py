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
        elif e.get('type') in ('reply', 'reaction', 'positive', 'engagement'):
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


def check_message_fatigue(config):
    """
    Check if message fatigue threshold reached.
    
    IMPORTANT: Silence = neutral (passive reading is valid).
    Only count EXPLICIT NEGATIVE signals as fatigue triggers.
    
    Returns (is_fatigued, negative_count, details)
    """
    fatigue_config = config.get('adaptiveScheduling', {}).get('messageFatigue', {})
    engagement_signals = config.get('adaptiveScheduling', {}).get('engagementSignals', {})
    
    # Only these trigger fatigue - explicit negative signals
    backoff_triggers = engagement_signals.get('backoffTriggers', ['👎', 'stop', 'less', 'too much'])
    max_negative = fatigue_config.get('maxNegativeSignals', 2)  # 2 explicit negatives = fatigue
    
    if not FEEDBACK_LOG.exists():
        return False, 0, {"threshold": max_negative, "action": "pause"}
    
    entries = []
    with open(FEEDBACK_LOG) as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    # Count recent negative signals (last 7 days)
    # ONLY count explicit negative feedback about surfacing frequency
    recent_negative = 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    
    for e in entries:
        try:
            ts = datetime.fromisoformat(e.get('timestamp', '').replace('Z', '+00:00'))
            if ts < cutoff:
                continue
        except:
            continue
        
        entry_type = e.get('type', '')
        
        # Only these count as negative:
        # 1. Explicit 'negative' type entry
        # 2. 👎 reaction
        # 3. Entry specifically about reducing surfaces
        if entry_type == 'negative':
            recent_negative += 1
        elif entry_type == 'reaction' and e.get('emoji') == '👎':
            recent_negative += 1
        elif entry_type == 'surface_feedback' and e.get('sentiment') == 'negative':
            recent_negative += 1
        # Note: Don't count substring matches - too many false positives
    
    is_fatigued = recent_negative >= max_negative
    
    return is_fatigued, recent_negative, {
        'threshold': max_negative,
        'action': fatigue_config.get('action', 'pause'),
        'note': 'Silence=neutral. Only explicit negative (👎/stop/less) triggers fatigue.'
    }


def log_surface(category, topic=None, source=None):
    """Log a surface event for fatigue tracking."""
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'type': 'surface',
        'category': category,
        'topic': topic,
        'source': source
    }
    
    with open(FEEDBACK_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    return entry


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
    
    # Apply circadian modifier
    base_score *= get_circadian_modifier(hour, dow, config)
    
    return min(base_score, 1.0)  # Cap at 1.0


def get_circadian_modifier(hour, dow, config):
    """
    Apply circadian rhythm awareness based on research:
    - 11 AM and 3 PM are energy peaks (1.3x boost)
    - 1-2 PM is post-lunch dip (0.7x penalty)
    - Tuesday 8 PM is "golden hour" (1.4x boost)
    """
    circadian = config.get('circadianAwareness', {})
    if not circadian.get('enabled', False):
        return 1.0
    
    modifier = 1.0
    
    # Check peaks
    peaks = circadian.get('peaks', {})
    for peak_name, peak_config in peaks.items():
        if hour == peak_config.get('hour'):
            modifier *= peak_config.get('boost', 1.0)
    
    # Check dips
    dips = circadian.get('dips', {})
    for dip_name, dip_config in dips.items():
        if hour in dip_config.get('hours', []):
            modifier *= dip_config.get('penalty', 1.0)
    
    # Check golden hour (Tuesday 8 PM)
    golden = circadian.get('goldenHour', {})
    if golden:
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day = dow_names[dow] if dow is not None else None
        if current_day == golden.get('day') and hour == golden.get('hour'):
            modifier *= golden.get('boost', 1.0)
    
    return modifier


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
    
    # Check message fatigue FIRST (only triggers on EXPLICIT negative, not silence)
    is_fatigued, negative_count, fatigue_details = check_message_fatigue(config)
    if is_fatigued:
        return {
            'decision': 'no',
            'reason': f'Explicit negative signals detected: {negative_count} in last 7 days (threshold: {fatigue_details["threshold"]})',
            'score': 0.0,
            'hour': hour,
            'fatigue': True,
            'negative_signals': negative_count,
            'action': fatigue_details['action'],
            'note': fatigue_details.get('note'),
            'fix': 'Reduce frequency or adjust content type'
        }
    
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


def detect_workflow_boundary():
    """
    Detect if we're at a workflow boundary (good time to interrupt).
    
    Based on arXiv 2601.10253 (IUI 2026):
    - Workflow boundaries (post-commit, task completion): 52% engagement
    - Mid-task interruptions: 62% dismissal rate
    - Well-timed proactive: 45s interpretation time (vs 101s for poorly-timed)
    
    Returns:
    - is_boundary: bool
    - confidence: 0-1
    - boundary_type: str
    """
    state = load_heartbeat_state()
    
    # Signal 1: Time since last Jon message
    last_interaction = state.get('lastInteraction', {}).get('timestamp')
    minutes_since = None
    
    if last_interaction:
        try:
            last_dt = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
            minutes_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 60
        except:
            pass
    
    # Signal 2: Check for recent activity markers
    last_activity = state.get('lastActivity', {})
    activity_type = last_activity.get('type', 'unknown')
    
    # Boundary detection logic
    boundary_signals = []
    
    # Long silence = likely at boundary (finished task, stepped away)
    if minutes_since is not None:
        if minutes_since > 30:
            boundary_signals.append(('long_silence', 0.8, 'User idle >30min'))
        elif minutes_since > 10:
            boundary_signals.append(('medium_silence', 0.6, 'User idle >10min'))
        elif minutes_since < 2:
            boundary_signals.append(('active', -0.5, 'User very recently active'))
    
    # Time-based boundaries (natural breaks)
    hour = get_sgt_hour()
    if hour in [8, 9]:  # Morning start
        boundary_signals.append(('morning_start', 0.7, 'Beginning of day'))
    elif hour in [12, 13]:  # Lunch
        boundary_signals.append(('lunch_break', 0.5, 'Lunch time'))
    elif hour in [17, 18]:  # End of work
        boundary_signals.append(('day_end', 0.6, 'End of workday'))
    elif hour >= 22 or hour < 7:  # Night
        boundary_signals.append(('night', 0.3, 'Night hours - autonomous'))
    
    # Activity type signals
    if activity_type == 'task_complete':
        boundary_signals.append(('task_complete', 0.9, 'Task just completed'))
    elif activity_type == 'conversation_end':
        boundary_signals.append(('convo_end', 0.8, 'Conversation concluded'))
    
    # Calculate overall boundary score
    if not boundary_signals:
        return {
            'is_boundary': False,
            'confidence': 0.5,
            'boundary_type': 'unknown',
            'signals': [],
            'recommendation': 'Insufficient signals - use time-based heuristics'
        }
    
    # Weighted average of signals (ignore negative for type)
    positive_signals = [(name, score, reason) for name, score, reason in boundary_signals if score > 0]
    negative_signals = [(name, score, reason) for name, score, reason in boundary_signals if score < 0]
    
    if negative_signals:
        # Any strong negative signal = not a boundary
        return {
            'is_boundary': False,
            'confidence': 0.8,
            'boundary_type': 'mid_task',
            'signals': boundary_signals,
            'recommendation': 'User recently active - wait for natural break'
        }
    
    if positive_signals:
        avg_score = sum(s[1] for s in positive_signals) / len(positive_signals)
        best_signal = max(positive_signals, key=lambda x: x[1])
        
        return {
            'is_boundary': avg_score >= 0.5,
            'confidence': round(avg_score, 2),
            'boundary_type': best_signal[0],
            'signals': boundary_signals,
            'recommendation': 'Good time to surface' if avg_score >= 0.5 else 'Marginal - surface only if important'
        }
    
    return {
        'is_boundary': False,
        'confidence': 0.5,
        'boundary_type': 'unknown',
        'signals': boundary_signals,
        'recommendation': 'Mixed signals'
    }


def infer_cognitive_state():
    """
    Infer user's cognitive availability from observable signals.
    Based on CHI 2026 research: timing alignment with cognitive state
    improves outcomes by 21%.
    
    Returns score 0-1 where:
    - 1.0 = Highly available (good time to surface)
    - 0.5 = Neutral
    - 0.0 = Unavailable (avoid interruption)
    """
    config = load_config()
    hour = get_sgt_hour()
    dow = get_sgt_dow()
    
    factors = {}
    weights = {}
    
    # Factor 1: Time of day (from research: morning = higher capacity)
    if 8 <= hour <= 11:
        factors['time_of_day'] = 0.9  # Morning peak
    elif 14 <= hour <= 17:
        factors['time_of_day'] = 0.8  # Afternoon productive
    elif 20 <= hour <= 22:
        factors['time_of_day'] = 0.6  # Evening wind-down
    elif hour >= 23 or hour < 7:
        factors['time_of_day'] = 0.2  # Sleep hours
    else:
        factors['time_of_day'] = 0.5  # Transitional
    weights['time_of_day'] = 0.3
    
    # Factor 2: Day of week
    if dow >= 5:  # Weekend
        factors['day_of_week'] = 0.4  # Family time, less available
    elif dow == 0:  # Monday
        factors['day_of_week'] = 0.7  # Week start, catching up
    elif dow == 4:  # Friday
        factors['day_of_week'] = 0.6  # Week end, winding down
    else:
        factors['day_of_week'] = 0.8  # Mid-week productivity
    weights['day_of_week'] = 0.2
    
    # Factor 3: Recent engagement rate (proxy for attention)
    rate, samples = get_recent_engagement()
    if rate is not None and samples >= 3:
        # High engagement = available, low = busy or disengaged
        factors['engagement'] = min(rate + 0.2, 1.0)  # Slight optimism bias
    else:
        factors['engagement'] = 0.5  # Unknown, assume neutral
    weights['engagement'] = 0.3
    
    # Factor 4: Time since last interaction
    state = load_heartbeat_state()
    last_surface = state.get('lastSurface', {}).get('timestamp')
    if last_surface:
        try:
            last_dt = datetime.fromisoformat(last_surface.replace('Z', '+00:00'))
            hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
            
            if hours_since < 0.5:
                factors['recency'] = 0.3  # Very recent, give space
            elif hours_since < 2:
                factors['recency'] = 0.6  # Recent but ok
            elif hours_since < 6:
                factors['recency'] = 0.9  # Good gap
            else:
                factors['recency'] = 0.7  # Long gap, might be away
        except:
            factors['recency'] = 0.5
    else:
        factors['recency'] = 0.5
    weights['recency'] = 0.2
    
    # Weighted average
    total_weight = sum(weights.values())
    weighted_sum = sum(factors[k] * weights[k] for k in factors)
    cognitive_score = weighted_sum / total_weight
    
    # Interpretation
    if cognitive_score >= 0.7:
        interpretation = 'available'
        recommendation = 'Good time to surface meaningful content'
    elif cognitive_score >= 0.5:
        interpretation = 'neutral'
        recommendation = 'Surface only if high-value or time-sensitive'
    elif cognitive_score >= 0.3:
        interpretation = 'busy'
        recommendation = 'Prefer silent work; surface only if urgent'
    else:
        interpretation = 'unavailable'
        recommendation = 'Do not disturb; work silently'
    
    return {
        'cognitive_score': round(cognitive_score, 2),
        'interpretation': interpretation,
        'recommendation': recommendation,
        'factors': {k: round(v, 2) for k, v in factors.items()},
        'weights': weights,
        'hour_sgt': hour,
        'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dow]
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
    
    # Add cognitive state
    cognitive = infer_cognitive_state()
    
    # Add workflow boundary detection
    boundary = detect_workflow_boundary()
    
    # Add message fatigue check
    is_fatigued, unreplied, fatigue_details = check_message_fatigue(config)
    
    return {
        'current_time': {
            'hour_sgt': hour,
            'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][dow],
            'is_weekend': dow >= 5
        },
        'workflow_boundary': boundary,
        'cognitive_state': cognitive,
        'message_fatigue': {
            'fatigued': is_fatigued,
            'consecutive_unreplied': unreplied,
            'threshold': fatigue_details.get('threshold'),
            'status': '🔴 FATIGUED' if is_fatigued else '🟢 OK'
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
        print("Commands: should-surface, best-category, update-engagement, log-surface, fatigue-status, cognitive-state, workflow-boundary, status")
        return
    
    cmd = sys.argv[1]
    
    if cmd == 'workflow-boundary':
        result = detect_workflow_boundary()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'cognitive-state':
        result = infer_cognitive_state()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'should-surface':
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
    
    elif cmd == 'log-surface':
        # Log a surface event: log-surface --category CAT [--topic TOPIC] [--source SRC]
        category = None
        topic = None
        source = None
        if '--category' in sys.argv:
            idx = sys.argv.index('--category')
            if idx + 1 < len(sys.argv):
                category = sys.argv[idx + 1]
        if '--topic' in sys.argv:
            idx = sys.argv.index('--topic')
            if idx + 1 < len(sys.argv):
                topic = sys.argv[idx + 1]
        if '--source' in sys.argv:
            idx = sys.argv.index('--source')
            if idx + 1 < len(sys.argv):
                source = sys.argv[idx + 1]
        if not category:
            print("Specify --category")
            return
        result = log_surface(category, topic, source)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'fatigue-status':
        config = load_config()
        is_fatigued, unreplied, details = check_message_fatigue(config)
        print(json.dumps({
            'fatigued': is_fatigued,
            'consecutive_unreplied': unreplied,
            'threshold': details.get('threshold'),
            'action': details.get('action'),
            'status': '🔴 FATIGUED - pause surfaces' if is_fatigued else '🟢 OK to surface'
        }, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
