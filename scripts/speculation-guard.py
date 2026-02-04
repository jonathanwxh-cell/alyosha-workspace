#!/usr/bin/env python3
"""
Speculation Guard - Detect speculative patterns and suggest alternatives

From MEMORY.md: "Jon tends to speculate more when bored — often betting on 
crashes. When busy/engaged with other things, the urge fades."

This script:
1. Logs speculative questions/requests
2. Detects boredom patterns
3. Suggests engaging alternatives
4. Tracks effectiveness

Usage:
    python3 speculation-guard.py log "looking at puts on SPY"
    python3 speculation-guard.py check              # Check recent activity
    python3 speculation-guard.py suggest            # Get alternative suggestion
    python3 speculation-guard.py status             # Pattern summary
"""

import json
import sys
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

SPECULATION_LOG = Path.home() / '.openclaw/workspace/memory/speculation-log.jsonl'
ALTERNATIVES_FILE = Path.home() / '.openclaw/workspace/memory/alternatives.json'

# Engaging alternatives when speculation urge detected
ALTERNATIVES = {
    'intellectual': [
        "🧠 What if we explored that consciousness research thread instead?",
        "📚 I found an interesting paper on protein folding — want to dive in?",
        "🔍 The AI capex story is evolving — shall I do a deep analysis?",
        "🌐 There's a geopolitical thread I haven't pulled yet. Interested?",
    ],
    'creative': [
        "🎨 Want to generate something? I could make a data visualization.",
        "✍️ That Substack draft is waiting — want to work on it together?",
        "🔧 I have a tool idea that could save time. Want to build it?",
        "📊 The Fragility Index project is ready for its first company.",
    ],
    'family': [
        "👨‍👧‍👦 The kids might enjoy that Sentosa trip this weekend.",
        "🍳 I have a fun new recipe the kids might like.",
        "📖 Want a bedtime story idea for tonight?",
    ],
    'meta': [
        "🤖 Shall I show you what the daemon discovered overnight?",
        "📈 The prediction tracking system could use a new entry.",
        "🔬 There's an interesting research rabbit hole to explore.",
    ],
}

SPECULATIVE_KEYWORDS = [
    'puts', 'calls', 'options', 'short', 'crash', 'collapse', 
    'bet against', 'bearish', 'hedge', 'yolo', 'gamble',
    'weekly', 'expiry', 'strike', '0dte', 'leveraged'
]


def log_speculation(text):
    """Log a speculative query/action."""
    now = datetime.now(timezone.utc)
    
    entry = {
        'timestamp': now.isoformat(),
        'day': now.strftime('%A'),
        'hour_sgt': (now.hour + 8) % 24,
        'text': text[:200],
        'keywords': [k for k in SPECULATIVE_KEYWORDS if k.lower() in text.lower()],
    }
    
    SPECULATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(SPECULATION_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    print(f"📝 Logged speculation signal")
    return entry


def load_logs():
    """Load speculation log."""
    logs = []
    if SPECULATION_LOG.exists():
        with open(SPECULATION_LOG) as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except:
                        pass
    return logs


def check_recent():
    """Check recent speculation activity and detect patterns."""
    logs = load_logs()
    now = datetime.now(timezone.utc)
    
    # Last 24 hours
    cutoff_24h = (now - timedelta(hours=24)).isoformat()
    recent_24h = [l for l in logs if l.get('timestamp', '') > cutoff_24h]
    
    # Last 7 days
    cutoff_7d = (now - timedelta(days=7)).isoformat()
    recent_7d = [l for l in logs if l.get('timestamp', '') > cutoff_7d]
    
    print("📊 Speculation Activity\n")
    print(f"Last 24h: {len(recent_24h)} signals")
    print(f"Last 7d:  {len(recent_7d)} signals")
    
    # Pattern detection
    alerts = []
    
    if len(recent_24h) >= 3:
        alerts.append("⚠️  HIGH: 3+ speculation signals today — boredom pattern?")
    
    if len(recent_7d) >= 10:
        alerts.append("⚠️  ELEVATED: 10+ signals this week — watch for burnout cycle")
    
    # Time patterns
    hours = [l.get('hour_sgt', 12) for l in recent_7d]
    if hours:
        late_night = len([h for h in hours if h >= 22 or h <= 6])
        if late_night >= 3:
            alerts.append("⚠️  PATTERN: Late-night speculation — sleep-deprived trading?")
    
    # Keyword patterns
    all_keywords = []
    for l in recent_7d:
        all_keywords.extend(l.get('keywords', []))
    
    if 'crash' in all_keywords or 'collapse' in all_keywords:
        alerts.append("⚠️  BIAS: Crash-focused language detected — contrarian trap?")
    
    if alerts:
        print("\n**Alerts:**")
        for alert in alerts:
            print(f"  {alert}")
        return True  # Intervention recommended
    
    print("\n✅ Activity within normal range")
    return False


def get_suggestion(category=None):
    """Get an engaging alternative suggestion."""
    if category and category in ALTERNATIVES:
        suggestions = ALTERNATIVES[category]
    else:
        # Weight toward intellectual/creative
        weights = {
            'intellectual': 4,
            'creative': 3,
            'meta': 2,
            'family': 1,
        }
        pool = []
        for cat, weight in weights.items():
            pool.extend(ALTERNATIVES[cat] * weight)
        suggestions = pool
    
    suggestion = random.choice(suggestions)
    print(f"\n💡 **Alternative:**\n{suggestion}")
    return suggestion


def show_status():
    """Show overall speculation pattern status."""
    logs = load_logs()
    
    if not logs:
        print("📭 No speculation history yet")
        return
    
    print("📊 Speculation Pattern Summary\n")
    
    # Total history
    print(f"Total logged: {len(logs)} signals")
    
    # By day of week
    from collections import Counter
    by_day = Counter(l.get('day', 'Unknown') for l in logs)
    print("\n**By Day:**")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        count = by_day.get(day, 0)
        bar = '█' * count
        print(f"  {day:10} {bar}")
    
    # By hour
    by_hour = Counter(l.get('hour_sgt', 0) for l in logs)
    peak_hour = by_hour.most_common(1)[0] if by_hour else (0, 0)
    print(f"\n**Peak hour:** {peak_hour[0]}:00 SGT ({peak_hour[1]} signals)")
    
    # Top keywords
    all_keywords = []
    for l in logs:
        all_keywords.extend(l.get('keywords', []))
    top_keywords = Counter(all_keywords).most_common(5)
    if top_keywords:
        print("\n**Top keywords:**")
        for kw, count in top_keywords:
            print(f"  {kw}: {count}")
    
    # Insight
    print("\n**Insight:**")
    if len(logs) < 10:
        print("  📈 Building baseline — keep logging to see patterns")
    elif peak_hour[0] >= 22 or peak_hour[0] <= 6:
        print("  🌙 Late-night speculation pattern — correlates with boredom/insomnia")
    elif by_day.get('Monday', 0) + by_day.get('Sunday', 0) > len(logs) * 0.4:
        print("  📅 Weekend/Monday cluster — may correlate with market anxiety")
    else:
        print("  📊 Pattern still emerging — continue logging")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'log' and len(sys.argv) >= 3:
        text = ' '.join(sys.argv[2:])
        log_speculation(text)
        
        # Auto-check and suggest if concerning
        if check_recent():
            get_suggestion()
    
    elif cmd == 'check':
        needs_intervention = check_recent()
        if needs_intervention:
            get_suggestion()
    
    elif cmd == 'suggest':
        category = sys.argv[2] if len(sys.argv) >= 3 else None
        get_suggestion(category)
    
    elif cmd == 'status':
        show_status()
    
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
