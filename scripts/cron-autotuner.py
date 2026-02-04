#!/usr/bin/env python3
"""
Cron Auto-Tuner - Self-modifying agent pattern

Observes cron engagement → Adjusts behavior → Logs changes

Rules:
- ONLY disable on explicit negative signals (thumbs down, "stop", "less")
- Silence = neutral (Jon reads passively, doesn't mean dislike)
- >50% explicit positive (reply, 👍) → flag for frequency increase
- Auto-logs all modifications to memory/self-improvement-log.md
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from zoneinfo import ZoneInfo

SGT = ZoneInfo("Asia/Singapore")
FEEDBACK_LOG = Path(__file__).parent.parent / "memory" / "feedback-log.jsonl"
IMPROVEMENT_LOG = Path(__file__).parent.parent / "memory" / "self-improvement-log.md"
MIN_RUNS = 3
DISABLE_THRESHOLD = -1  # Only on explicit negative, not silence
BOOST_THRESHOLD = 50   # 50%+ engagement

def load_feedback():
    """Load feedback log and aggregate by topic."""
    if not FEEDBACK_LOG.exists():
        return {}
    
    topics = defaultdict(lambda: {"runs": 0, "engaged": 0})
    
    with open(FEEDBACK_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line)
                topic = entry.get("topic", "unknown")
                topics[topic]["runs"] += 1
                # Check for EXPLICIT signals only
                # Positive: reply, 👍, engaged=true
                # Negative: 👎, "stop", "less" 
                # Silence = neutral (not counted either way)
                if entry.get("engaged") or entry.get("replied") or entry.get("reaction") == "👍":
                    topics[topic]["engaged"] += 1
                if entry.get("negative") or entry.get("reaction") == "👎":
                    topics[topic]["negative"] = topics[topic].get("negative", 0) + 1
            except:
                continue
    
    return dict(topics)

def get_cron_jobs():
    """Get all enabled cron jobs."""
    result = subprocess.run(
        ["openclaw", "cron", "list", "--json"],
        capture_output=True, text=True, cwd=str(Path.home())
    )
    if result.returncode != 0:
        return []
    
    try:
        data = json.loads(result.stdout)
        return [j for j in data.get("jobs", []) if j.get("enabled")]
    except:
        return []

def disable_cron(job_id: str, reason: str) -> bool:
    """Disable a cron job."""
    result = subprocess.run(
        ["openclaw", "cron", "update", job_id, "--enabled", "false"],
        capture_output=True, text=True, cwd=str(Path.home())
    )
    return result.returncode == 0

def log_improvement(action: str, target: str, reason: str, result: str):
    """Log self-modification to improvement log."""
    IMPROVEMENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT")
    entry = f"\n### {timestamp}\n**Action:** {action}\n**Target:** {target}\n**Reason:** {reason}\n**Result:** {result}\n"
    
    with open(IMPROVEMENT_LOG, "a") as f:
        f.write(entry)

def analyze_and_tune():
    """Main auto-tuning loop."""
    feedback = load_feedback()
    jobs = get_cron_jobs()
    
    if not feedback:
        print("No feedback data yet. Need more runs to tune.")
        return
    
    actions_taken = []
    
    # Map job names to topics (simplified matching)
    for job in jobs:
        name = job.get("name", "").lower()
        job_id = job.get("id")
        
        # Find matching topic in feedback
        matched_topic = None
        for topic in feedback:
            if topic.lower() in name or name in topic.lower():
                matched_topic = topic
                break
        
        if not matched_topic:
            continue
        
        stats = feedback[matched_topic]
        runs = stats["runs"]
        engaged = stats["engaged"]
        
        if runs < MIN_RUNS:
            continue
        
        engagement_rate = (engaged / runs) * 100 if runs > 0 else 0
        
        # Rule 1: Disable ONLY if explicit negative signals
        negative_count = stats.get("negative", 0)
        if negative_count >= 2 and runs >= MIN_RUNS:
            print(f"🔴 {job['name']}: {runs} runs, {negative_count} negative signals → DISABLING")
            
            # Actually disable via cron tool
            success = disable_cron(job_id, "zero engagement")
            
            if success:
                log_improvement(
                    action="AUTO-DISABLE",
                    target=job['name'],
                    reason=f"{runs} runs with {negative_count} explicit negative signals",
                    result="Cron disabled automatically"
                )
                actions_taken.append(f"Disabled: {job['name']}")
            else:
                print(f"  Failed to disable {job['name']}")
        
        # Rule 2: Flag high engagement for potential boost
        elif engagement_rate >= BOOST_THRESHOLD and runs >= MIN_RUNS:
            print(f"🟢 {job['name']}: {runs} runs, {engagement_rate:.0f}% engagement → KEEP/BOOST")
            # Don't auto-boost frequency, just log for review
            log_improvement(
                action="FLAG-HIGH-ENGAGEMENT",
                target=job['name'],
                reason=f"{runs} runs with {engagement_rate:.0f}% engagement",
                result="Flagged for potential frequency increase"
            )
    
    if actions_taken:
        print(f"\n✅ Self-modifications: {len(actions_taken)}")
        for a in actions_taken:
            print(f"  • {a}")
    else:
        print("No modifications needed based on current data.")

def status():
    """Show current engagement stats."""
    feedback = load_feedback()
    
    print("📊 CRON ENGAGEMENT STATUS")
    print("=" * 50)
    
    for topic, stats in sorted(feedback.items(), key=lambda x: -x[1]["runs"]):
        runs = stats["runs"]
        engaged = stats["engaged"]
        rate = (engaged / runs) * 100 if runs > 0 else 0
        
        if rate == 0 and runs >= MIN_RUNS:
            flag = "🔴"
        elif rate >= BOOST_THRESHOLD:
            flag = "🟢"
        else:
            flag = "⚪"
        
        print(f"{flag} {topic}: {runs} runs, {engaged} engaged ({rate:.0f}%)")

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "tune":
        analyze_and_tune()
    elif cmd == "status":
        status()
    else:
        print("Usage: cron-autotuner.py [status|tune]")
