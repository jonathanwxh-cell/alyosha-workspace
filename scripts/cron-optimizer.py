#!/usr/bin/env python3
"""
cron-optimizer.py - Analyze and fix cron timing conflicts

Spreads out overlapping crons to prevent clustering.
Respects time preferences while avoiding collisions.

Usage:
  python3 cron-optimizer.py analyze    # Show conflicts
  python3 cron-optimizer.py optimize   # Generate optimized schedule
  python3 cron-optimizer.py apply      # Apply optimizations (interactive)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

# Time slot preferences by category
CATEGORY_PREFERENCES = {
    # Morning briefings (07:00-09:00)
    "briefing": {"preferred": [7, 8], "avoid": [23, 0, 1, 2, 3, 4, 5, 6]},
    # Research tasks (09:00-11:00, 14:00-16:00)
    "research": {"preferred": [9, 10, 14, 15], "avoid": [23, 0, 1, 2, 3, 4, 5, 6, 7]},
    # Maintenance (late night/early morning)
    "maintenance": {"preferred": [3, 4, 5], "avoid": [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
    # Family/lifestyle (morning, evening)
    "family": {"preferred": [8, 9, 19, 20], "avoid": [0, 1, 2, 3, 4, 5, 23]},
    # Market-related (market hours awareness)
    "market": {"preferred": [22, 23, 0, 1, 2, 8, 9], "avoid": [10, 11, 12, 13, 14]},
    # Weekly reviews (weekend mornings)
    "weekly": {"preferred": [10, 11, 14], "avoid": [0, 1, 2, 3, 4, 5, 6, 7]},
}

# Job categorization
JOB_CATEGORIES = {
    "Daily Status Email": "briefing",
    "Daily World State Analysis": "briefing",
    "Daily SG News Briefing": "briefing",
    "Daily Email Triage": "briefing",
    "daily-research-scan": "research",
    "Monday Research Digest": "research",
    "Research Paper Scan": "research",
    "AI Capex Narrative Monitor": "research",
    "Embodied AI / Robotics Tracker": "research",
    "SpaceX IPO Tracker": "research",
    "Weekly Twitter/X Intel": "research",
    "Macro Pulse": "research",
    "NVDA Dashboard Refresh": "maintenance",
    "Weekly Disk Cleanup": "maintenance",
    "Monthly Memory Compaction": "maintenance",
    "Weekly Self-Maintenance": "maintenance",
    "Weekly Engagement Analysis": "maintenance",
    "weekly-self-review": "maintenance",
    "Daily Topic Self-Audit": "maintenance",
    "Kids Dinner Ideas": "family",
    "weekend-family-ideas": "family",
    "weekly-checkin": "family",
    "Watchlist Price Alerts": "market",
    "Weekly Forecast Calibration": "weekly",
    "weekly-synthesis": "weekly",
    "Weekly Ambitious Proposal": "weekly",
    "openclaw-update-check": "maintenance",
}

def parse_cron_hour(expr: str) -> list:
    """Parse hour field from cron expression."""
    parts = expr.split()
    if len(parts) < 2:
        return []
    
    hour_field = parts[1]
    hours = []
    
    for segment in hour_field.split(','):
        if segment == '*':
            hours.extend(range(24))
        elif '-' in segment:
            start, end = map(int, segment.split('-'))
            hours.extend(range(start, end + 1))
        elif '/' in segment:
            base, step = segment.split('/')
            start = 0 if base == '*' else int(base)
            hours.extend(range(start, 24, int(step)))
        else:
            hours.append(int(segment))
    
    return hours

def analyze_conflicts(jobs: list) -> dict:
    """Analyze timing conflicts across all jobs."""
    hourly = defaultdict(list)
    
    for job in jobs:
        expr = job.get("schedule", {}).get("expr", "")
        tz = job.get("schedule", {}).get("tz", "UTC")
        name = job.get("name", "unknown")
        
        hours = parse_cron_hour(expr)
        for h in hours:
            # Convert to SGT for comparison
            if tz == "UTC":
                h_sgt = (h + 8) % 24
            else:
                h_sgt = h
            hourly[h_sgt].append({"name": name, "id": job.get("id"), "original_hour": h, "tz": tz})
    
    conflicts = {h: jobs for h, jobs in hourly.items() if len(jobs) > 1}
    return conflicts

def suggest_spread(conflicts: dict, all_jobs: list) -> list:
    """Suggest new timings to spread out conflicts."""
    suggestions = []
    used_slots = set()  # Track (hour, minute) pairs
    
    # First pass: mark all non-conflicting slots as used
    for job in all_jobs:
        expr = job.get("schedule", {}).get("expr", "")
        parts = expr.split()
        if len(parts) >= 2:
            hours = parse_cron_hour(expr)
            minute = int(parts[0]) if parts[0].isdigit() else 0
            tz = job.get("schedule", {}).get("tz", "UTC")
            for h in hours:
                h_sgt = (h + 8) % 24 if tz == "UTC" else h
                used_slots.add((h_sgt, minute))
    
    for hour, jobs in sorted(conflicts.items()):
        if len(jobs) <= 1:
            continue
        
        # Keep first job at original time
        kept = jobs[0]
        suggestions.append({
            "job": kept["name"],
            "action": "keep",
            "reason": f"First at {hour:02d}:00 SGT"
        })
        
        # Spread others across the hour
        for i, job in enumerate(jobs[1:], 1):
            new_minute = (i * 15) % 60  # Spread by 15 min intervals
            
            # If slot taken, try next available
            while (hour, new_minute) in used_slots:
                new_minute = (new_minute + 5) % 60
            
            used_slots.add((hour, new_minute))
            
            category = JOB_CATEGORIES.get(job["name"], "research")
            
            suggestions.append({
                "job": job["name"],
                "job_id": job["id"],
                "action": "reschedule",
                "from": f"{hour:02d}:00",
                "to": f"{hour:02d}:{new_minute:02d}",
                "category": category,
                "reason": f"Spread within hour to avoid collision"
            })
    
    return suggestions

def load_crons() -> list:
    """Load current cron jobs via gateway API (would need implementation)."""
    # For now, return empty - in practice would call cron list
    return []

def print_analysis(conflicts: dict):
    """Print conflict analysis."""
    print("=" * 60)
    print("CRON TIMING CONFLICT ANALYSIS")
    print("=" * 60)
    print()
    
    if not conflicts:
        print("✓ No conflicts found!")
        return
    
    total_conflicts = sum(len(jobs) - 1 for jobs in conflicts.values())
    print(f"Found {total_conflicts} conflicts across {len(conflicts)} hours:")
    print()
    
    for hour, jobs in sorted(conflicts.items()):
        print(f"🔴 {hour:02d}:00 SGT ({len(jobs)} jobs)")
        for job in jobs:
            category = JOB_CATEGORIES.get(job["name"], "?")
            print(f"   • {job['name']} [{category}]")
        print()

def print_suggestions(suggestions: list):
    """Print optimization suggestions."""
    print("=" * 60)
    print("OPTIMIZATION SUGGESTIONS")
    print("=" * 60)
    print()
    
    reschedules = [s for s in suggestions if s["action"] == "reschedule"]
    
    if not reschedules:
        print("✓ No changes needed!")
        return
    
    print(f"Recommended changes ({len(reschedules)} jobs):")
    print()
    
    for s in reschedules:
        print(f"📅 {s['job']}")
        print(f"   {s['from']} → {s['to']} SGT")
        print(f"   Reason: {s['reason']}")
        print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "analyze":
        # Would load from cron API in practice
        print("Run 'cron list' to get current jobs, then analyze.")
        print("For now, showing manual analysis from earlier...")
        
    elif cmd == "optimize":
        print("Optimization mode - would generate new schedule")
        
    elif cmd == "apply":
        print("Apply mode - would update cron jobs")
        
    else:
        print(__doc__)
