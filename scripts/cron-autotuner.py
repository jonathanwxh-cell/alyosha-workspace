#!/usr/bin/env python3
"""
Cron Auto-Tuner: Self-Improving Daemon Mechanism
=================================================

Analyzes cron job performance and suggests/applies improvements:
1. Health scoring - engagement rate per job
2. Auto-disable - persistently ignored jobs
3. Time optimization - shift to better windows
4. Model selection - track cost/quality tradeoffs

Usage:
    python3 cron-autotuner.py analyze          # Show health report
    python3 cron-autotuner.py suggest          # Suggest improvements
    python3 cron-autotuner.py apply            # Apply safe improvements
    python3 cron-autotuner.py evolve           # Full evolution cycle
"""

import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from collections import defaultdict

# Paths
MEMORY_DIR = Path.home() / '.openclaw/workspace/memory'
FEEDBACK_LOG = MEMORY_DIR / 'feedback-log.jsonl'
CRON_HEALTH = MEMORY_DIR / 'cron-health.json'
SCHEDULING_INTEL = MEMORY_DIR / 'scheduling-intelligence.json'
EVOLUTION_LOG = MEMORY_DIR / 'cron-evolution.jsonl'

# Thresholds
MIN_SAMPLES = 3  # Minimum runs before judging
LOW_ENGAGEMENT_THRESHOLD = 0.2  # Below this = underperforming
HIGH_ENGAGEMENT_THRESHOLD = 0.7  # Above this = keep
ERROR_THRESHOLD = 3  # Consecutive errors before flagging
STALE_DAYS = 14  # Days without run = stale


def load_feedback() -> list:
    """Load feedback log entries."""
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


def load_cron_health() -> dict:
    """Load existing cron health data."""
    if CRON_HEALTH.exists():
        with open(CRON_HEALTH) as f:
            return json.load(f)
    return {"jobs": {}, "meta": {"lastUpdated": None}}


def save_cron_health(data: dict):
    """Save cron health data."""
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(CRON_HEALTH, 'w') as f:
        json.dump(data, f, indent=2)


def log_evolution(action: str, job_name: str, details: dict):
    """Log an evolution action."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "job": job_name,
        "details": details
    }
    with open(EVOLUTION_LOG, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def get_optimal_hours() -> list:
    """Get optimal hours from scheduling intelligence."""
    if not SCHEDULING_INTEL.exists():
        return [6, 9, 14, 15, 20, 21]  # Defaults
    
    with open(SCHEDULING_INTEL) as f:
        config = json.load(f)
    
    patterns = config.get('observedPatterns', {})
    hour_data = patterns.get('hourEngagement', {})
    optimal = hour_data.get('optimal', [])
    
    return optimal if optimal else [6, 9, 14, 15, 20, 21]


def analyze_job_health(feedback: list) -> dict:
    """Analyze health by CATEGORY (more meaningful than job names)."""
    cat_stats = defaultdict(lambda: {
        'surfaces': 0,
        'engaged': 0,
        'hours': [],
        'topics': set()
    })
    
    # First pass: count surfaces per category
    surface_cats = []
    for entry in feedback:
        typ = entry.get('type')
        category = entry.get('category', 'unknown')
        hour = entry.get('hourSGT')
        topic = entry.get('topic', '')
        
        if typ == 'surface':
            cat_stats[category]['surfaces'] += 1
            surface_cats.append(category)
            if hour:
                cat_stats[category]['hours'].append(hour)
            if topic:
                cat_stats[category]['topics'].add(topic)
        
        elif typ in ('reply', 'reaction'):
            # Credit the most recent surface category
            if surface_cats:
                recent_cat = surface_cats[-1]
                cat_stats[recent_cat]['engaged'] += 1
    
    # Calculate health scores
    health = {}
    for cat, stats in cat_stats.items():
        surfaces = stats['surfaces']
        engaged = min(stats['engaged'], surfaces)
        
        engagement_rate = engaged / surfaces if surfaces > 0 else 0
        
        # Health score based on engagement
        health_score = engagement_rate
        
        health[cat] = {
            'surfaces': surfaces,
            'engaged': engaged,
            'engagement_rate': round(engagement_rate, 2),
            'health_score': round(health_score, 2),
            'avg_hour': round(sum(stats['hours']) / len(stats['hours'])) if stats['hours'] else None,
            'topics': list(stats['topics'])[:5],  # Top 5 topics
            'status': 'healthy' if health_score > HIGH_ENGAGEMENT_THRESHOLD else 
                     'underperforming' if health_score < LOW_ENGAGEMENT_THRESHOLD else 'moderate'
        }
    
    return health


def suggest_improvements(health: dict) -> list:
    """Generate improvement suggestions based on health analysis."""
    suggestions = []
    optimal_hours = get_optimal_hours()
    
    for category, stats in health.items():
        # Skip categories with insufficient data
        if stats['surfaces'] < MIN_SAMPLES:
            continue
        
        # Suggest reducing underperforming categories
        if stats['status'] == 'underperforming' and stats['surfaces'] >= 5:
            suggestions.append({
                'type': 'reduce_frequency',
                'category': category,
                'reason': f"Low engagement ({stats['engagement_rate']:.0%}) over {stats['surfaces']} surfaces",
                'severity': 'medium',
                'auto_apply': False,
                'recommendation': f"Consider reducing {category} content or improving format"
            })
        
        # Suggest boosting high-performing categories
        if stats['status'] == 'healthy' and stats['surfaces'] >= 3:
            suggestions.append({
                'type': 'boost',
                'category': category,
                'reason': f"High engagement ({stats['engagement_rate']:.0%}) - this content works!",
                'severity': 'low',
                'auto_apply': False,
                'recommendation': f"Consider more {category} content"
            })
        
        # Suggest time shifts for categories not in optimal hours
        if stats['avg_hour'] and stats['avg_hour'] not in optimal_hours:
            best_hour = optimal_hours[0] if optimal_hours else 9
            suggestions.append({
                'type': 'time_shift',
                'category': category,
                'current_hour': stats['avg_hour'],
                'suggested_hour': best_hour,
                'reason': f"Currently surfaces at ~{stats['avg_hour']}h SGT, optimal hours are {optimal_hours}",
                'severity': 'low',
                'auto_apply': False
            })
    
    return suggestions


def apply_improvement(suggestion: dict) -> bool:
    """Apply a single improvement (placeholder - would need cron API)."""
    # Log the evolution attempt
    log_evolution(
        action=suggestion['type'],
        job_name=suggestion['job'],
        details=suggestion
    )
    
    # Actual implementation would use cron tool
    # For now, just log
    return True


def print_health_report(health: dict):
    """Print formatted health report."""
    print("=" * 60)
    print("CATEGORY HEALTH REPORT")
    print("=" * 60)
    
    # Sort by health score
    sorted_cats = sorted(health.items(), key=lambda x: x[1]['health_score'], reverse=True)
    
    for cat, stats in sorted_cats:
        emoji = "🟢" if stats['status'] == 'healthy' else "🟡" if stats['status'] == 'moderate' else "🔴"
        print(f"\n{emoji} **{cat}**")
        print(f"   Engagement: {stats['engagement_rate']:.0%} ({stats['engaged']}/{stats['surfaces']} surfaces)")
        if stats['avg_hour']:
            print(f"   Avg hour: {stats['avg_hour']}:00 SGT")
        if stats['topics']:
            print(f"   Topics: {', '.join(stats['topics'][:3])}")
    
    print("\n" + "=" * 60)


def print_suggestions(suggestions: list):
    """Print formatted suggestions."""
    if not suggestions:
        print("\n✅ No improvements suggested - daemon is healthy!")
        return
    
    print("\n📋 IMPROVEMENT SUGGESTIONS")
    print("-" * 40)
    
    for i, s in enumerate(suggestions, 1):
        severity_emoji = "🔴" if s['severity'] == 'high' else "🟡" if s['severity'] == 'medium' else "🟢"
        auto = "✓ auto" if s.get('auto_apply') else "⚡ manual"
        
        print(f"\n{i}. {severity_emoji} [{s['type'].upper()}] {s['job']}")
        print(f"   Reason: {s['reason']}")
        print(f"   Apply: {auto}")


def evolve():
    """Run full evolution cycle."""
    print("🧬 Running daemon evolution cycle...\n")
    
    # 1. Load data
    feedback = load_feedback()
    if len(feedback) < 10:
        print("⚠️ Insufficient feedback data for evolution (need 10+ entries)")
        return
    
    # 2. Analyze health
    health = analyze_job_health(feedback)
    
    # 3. Save health data
    health_data = load_cron_health()
    health_data['jobs'] = health
    save_cron_health(health_data)
    
    # 4. Generate suggestions
    suggestions = suggest_improvements(health)
    
    # 5. Auto-apply safe suggestions
    applied = 0
    for s in suggestions:
        if s.get('auto_apply'):
            if apply_improvement(s):
                applied += 1
                print(f"✅ Applied: {s['type']} for {s['job']}")
    
    # 6. Report
    print_health_report(health)
    print_suggestions([s for s in suggestions if not s.get('auto_apply')])
    
    print(f"\n🧬 Evolution complete: {applied} auto-improvements applied")


def main():
    if len(sys.argv) < 2:
        print("Usage: cron-autotuner.py <analyze|suggest|apply|evolve>")
        return
    
    cmd = sys.argv[1]
    
    feedback = load_feedback()
    
    if cmd == 'analyze':
        health = analyze_job_health(feedback)
        print_health_report(health)
        
        # Save
        health_data = load_cron_health()
        health_data['jobs'] = health
        save_cron_health(health_data)
    
    elif cmd == 'suggest':
        health = analyze_job_health(feedback)
        suggestions = suggest_improvements(health)
        print_suggestions(suggestions)
    
    elif cmd == 'apply':
        health = analyze_job_health(feedback)
        suggestions = suggest_improvements(health)
        for s in suggestions:
            if s.get('auto_apply'):
                apply_improvement(s)
                print(f"Applied: {s}")
    
    elif cmd == 'evolve':
        evolve()
    
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
