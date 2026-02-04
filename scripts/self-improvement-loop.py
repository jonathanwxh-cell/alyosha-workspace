#!/usr/bin/env python3
"""
Self-Improvement Loop for Alyosha
Systematically research, propose, implement, and measure improvements.

Runs weekly (or on-demand) to:
1. Review recent performance (corrections, feedback, failures)
2. Research agent best practices (web search)
3. Generate improvement proposals with success criteria
4. Track experiments and outcomes

Usage: python3 scripts/self-improvement-loop.py [review|propose|status]
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Paths
WORKSPACE = Path(__file__).parent.parent
IMPROVEMENTS_FILE = WORKSPACE / "memory" / "improvement-proposals.json"
EXPERIMENTS_FILE = WORKSPACE / "memory" / "experiments.jsonl"
CORRECTIONS_FILE = WORKSPACE / "memory" / "corrections-log.jsonl"
REFLECTIONS_FILE = WORKSPACE / "memory" / "reflections.jsonl"
FEEDBACK_FILE = WORKSPACE / "memory" / "feedback-log.jsonl"

def load_json(path, default=None):
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except:
            pass
    return default if default is not None else {}

def load_jsonl(path, days=7):
    """Load JSONL entries from last N days."""
    entries = []
    if not path.exists():
        return entries
    cutoff = datetime.now() - timedelta(days=days)
    try:
        with open(path) as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # Try to parse timestamp
                    ts = entry.get("timestamp") or entry.get("ts") or entry.get("date")
                    if ts:
                        try:
                            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                            if dt.replace(tzinfo=None) > cutoff:
                                entries.append(entry)
                        except:
                            entries.append(entry)  # Include if can't parse
                    else:
                        entries.append(entry)
    except:
        pass
    return entries

def review_performance():
    """Review recent corrections, reflections, and feedback."""
    corrections = load_jsonl(CORRECTIONS_FILE, days=7)
    reflections = load_jsonl(REFLECTIONS_FILE, days=7)
    feedback = load_jsonl(FEEDBACK_FILE, days=7)
    
    # Categorize corrections
    correction_types = {}
    for c in corrections:
        ctype = c.get("type", "unknown")
        correction_types[ctype] = correction_types.get(ctype, 0) + 1
    
    # Extract lessons from reflections
    lessons = [r.get("lesson") for r in reflections if r.get("lesson")]
    
    # Count feedback
    positive = sum(1 for f in feedback if f.get("signal") in ["👍", "positive", "engaged"])
    negative = sum(1 for f in feedback if f.get("signal") in ["👎", "negative", "stop"])
    
    return {
        "period": "last 7 days",
        "corrections": {
            "total": len(corrections),
            "by_type": correction_types
        },
        "reflections": {
            "total": len(reflections),
            "lessons": lessons[-5:]  # Last 5
        },
        "feedback": {
            "positive": positive,
            "negative": negative,
            "ratio": positive / max(positive + negative, 1)
        }
    }

def load_proposals():
    """Load existing improvement proposals."""
    return load_json(IMPROVEMENTS_FILE, {"proposals": [], "implemented": [], "rejected": []})

def save_proposals(data):
    """Save improvement proposals."""
    IMPROVEMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(IMPROVEMENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_proposal(title, description, success_criteria, priority="medium", source="self"):
    """Add a new improvement proposal."""
    data = load_proposals()
    proposal = {
        "id": f"imp-{len(data['proposals']) + len(data['implemented']) + 1:03d}",
        "title": title,
        "description": description,
        "success_criteria": success_criteria,
        "priority": priority,
        "source": source,
        "status": "proposed",
        "created": datetime.now().isoformat(),
        "outcome": None
    }
    data["proposals"].append(proposal)
    save_proposals(data)
    return proposal

def format_review(review):
    """Format performance review for output."""
    lines = ["## 📊 Performance Review (Last 7 Days)", ""]
    
    # Corrections
    lines.append(f"**Corrections:** {review['corrections']['total']}")
    if review['corrections']['by_type']:
        for ctype, count in review['corrections']['by_type'].items():
            lines.append(f"  - {ctype}: {count}")
    
    # Feedback
    fb = review['feedback']
    lines.append(f"\n**Feedback:** +{fb['positive']} / -{fb['negative']} ({fb['ratio']:.0%} positive)")
    
    # Lessons
    if review['reflections']['lessons']:
        lines.append("\n**Recent Lessons:**")
        for lesson in review['reflections']['lessons']:
            lines.append(f"  - {lesson}")
    
    return "\n".join(lines)

def format_proposals(data):
    """Format proposals for output."""
    lines = ["## 🔧 Improvement Proposals", ""]
    
    if not data['proposals']:
        lines.append("*No pending proposals.*")
    else:
        for p in data['proposals']:
            lines.append(f"**[{p['id']}] {p['title']}** ({p['priority']})")
            lines.append(f"  {p['description']}")
            lines.append(f"  Success: {p['success_criteria']}")
            lines.append("")
    
    if data['implemented']:
        lines.append(f"\n**Implemented:** {len(data['implemented'])}")
    
    return "\n".join(lines)

def generate_research_queries(review):
    """Generate research queries based on performance gaps."""
    queries = []
    
    # Based on correction types
    correction_types = review['corrections']['by_type']
    if correction_types.get('permission_asking', 0) > 0:
        queries.append("LLM agent autonomy best practices 2025")
    if correction_types.get('verbose', 0) > 0:
        queries.append("concise AI assistant response techniques")
    if correction_types.get('sycophancy', 0) > 0:
        queries.append("reducing sycophancy in language models")
    
    # Default queries for general improvement
    queries.extend([
        "AI agent self-improvement techniques 2025",
        "autonomous agent memory management",
        "LLM agent behavioral consistency"
    ])
    
    return queries[:3]  # Limit to 3

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if action == "review":
        review = review_performance()
        print(format_review(review))
        print("\n**Research queries to explore:**")
        for q in generate_research_queries(review):
            print(f"  - {q}")
    
    elif action == "propose":
        # This would be called by the agent with specific proposal
        if len(sys.argv) < 5:
            print("Usage: propose <title> <description> <success_criteria> [priority]")
            sys.exit(1)
        title = sys.argv[2]
        description = sys.argv[3]
        criteria = sys.argv[4]
        priority = sys.argv[5] if len(sys.argv) > 5 else "medium"
        proposal = add_proposal(title, description, criteria, priority)
        print(f"Added proposal: {proposal['id']}")
        print(json.dumps(proposal, indent=2))
    
    elif action == "status":
        review = review_performance()
        proposals = load_proposals()
        print(format_review(review))
        print("\n" + "-" * 40 + "\n")
        print(format_proposals(proposals))
    
    elif action == "json":
        review = review_performance()
        proposals = load_proposals()
        print(json.dumps({
            "review": review,
            "proposals": proposals,
            "research_queries": generate_research_queries(review)
        }, indent=2))
    
    else:
        print(f"Unknown action: {action}")
        print("Usage: self-improvement-loop.py [review|propose|status|json]")
        sys.exit(1)

if __name__ == "__main__":
    main()
