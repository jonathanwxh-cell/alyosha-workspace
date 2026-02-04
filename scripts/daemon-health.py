#!/usr/bin/env python3
"""
Daemon Health Dashboard - Quick ASCII visualization
Shows topic balance, engagement, fatigue status at a glance
"""

import json
from pathlib import Path
from datetime import datetime

def load_json(path):
    try:
        with open(Path.home() / f'.openclaw/workspace/{path}') as f:
            return json.load(f)
    except:
        return {}

def bar(pct, width=20, filled='█', empty='░'):
    """Create ASCII progress bar"""
    fill = int(pct / 100 * width)
    return filled * fill + empty * (width - fill)

def main():
    # Load data
    topics = load_json('memory/topic-balance.json')
    sched = load_json('memory/scheduling-intelligence.json')
    hb = load_json('memory/heartbeat-state.json')
    
    # Header
    now = datetime.now()
    sgt = (now.hour + 8) % 24
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           🤖 DAEMON HEALTH — {now.strftime('%Y-%m-%d')} {sgt:02d}:{now.minute:02d} SGT           ║
╠══════════════════════════════════════════════════════════╣""")
    
    # Topic Balance
    print("║  📊 TOPIC BALANCE (this week)                            ║")
    print("╟──────────────────────────────────────────────────────────╢")
    
    cats = topics.get('categories', {})
    total = sum(c.get('currentWeekCount', 0) for c in cats.values())
    
    for name, data in sorted(cats.items(), key=lambda x: -x[1].get('maxPct', 0))[:6]:
        count = data.get('currentWeekCount', 0)
        max_pct = data.get('maxPct', 20)
        pct = (count / total * 100) if total > 0 else 0
        status = '🔴' if pct > max_pct else '🟢'
        print(f"║  {name[:12]:<12} {bar(pct, 15)} {pct:5.1f}% (max {max_pct}%) {status} ║")
    
    print("╟──────────────────────────────────────────────────────────╢")
    
    # Engagement
    rolling = sched.get('adaptiveIntervals', {}).get('rollingEngagement', {})
    rate = rolling.get('currentRate', 0)
    samples = rolling.get('samples', 0)
    
    print("║  📈 ENGAGEMENT                                           ║")
    print(f"║  Rolling rate: {bar(rate*100, 20)} {rate*100:5.1f}%          ║")
    print(f"║  Samples: {samples:<3}  Interpretation: {'HIGH ✨' if rate > 0.6 else 'NORMAL 👍' if rate > 0.3 else 'LOW ⚠️ ':<10}          ║")
    
    print("╟──────────────────────────────────────────────────────────╢")
    
    # Fatigue Status
    backoff = sched.get('adaptiveScheduling', {}).get('backoffRules', {})
    level = backoff.get('currentBackoffLevel', 0)
    fatigue_status = '🟢 OK' if level < 1 else '🟡 MILD' if level < 3 else '🔴 HIGH'
    
    print("║  😴 FATIGUE STATUS                                       ║")
    print(f"║  Backoff level: {level:.1f}/5  Status: {fatigue_status:<20}        ║")
    print(f"║  (Only 👎/stop/less triggers fatigue, silence=neutral)   ║")
    
    print("╟──────────────────────────────────────────────────────────╢")
    
    # Last Action
    last = hb.get('lastAction', {})
    last_cat = last.get('category', '?')[:15]
    last_topic = last.get('topic', '?')[:30]
    
    print("║  ⏰ LAST ACTION                                          ║")
    print(f"║  Category: {last_cat:<15}                              ║")
    print(f"║  Topic: {last_topic:<40}   ║")
    
    print("╚══════════════════════════════════════════════════════════╝")

if __name__ == '__main__':
    main()
