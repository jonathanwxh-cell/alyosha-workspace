#!/usr/bin/env python3
"""
Memory Extraction Script
Analyzes daily logs and extracts structured memories

Run after significant sessions or nightly to:
- Extract new facts about Jon → USER.md candidates
- Extract lessons learned → MEMORY.md candidates  
- Identify patterns → insights file
- Score memory importance

Usage:
  python3 memory-extract.py              # Process today
  python3 memory-extract.py 2026-02-03   # Process specific date
  python3 memory-extract.py --week       # Process last 7 days
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / "memory"
OUTPUT_FILE = MEMORY_DIR / "extracted-memories.jsonl"

def load_daily_log(date_str: str) -> str:
    """Load a daily log file"""
    log_file = MEMORY_DIR / f"{date_str}.md"
    if log_file.exists():
        return log_file.read_text()
    return ""

def extract_patterns(content: str) -> dict:
    """Extract patterns from daily log content"""
    patterns = {
        "decisions": [],
        "lessons": [],
        "preferences": [],
        "feedback": [],
        "tools_used": [],
        "topics_discussed": []
    }
    
    # Look for explicit markers
    lines = content.split('\n')
    
    for line in lines:
        line_lower = line.lower()
        
        # Decisions
        if 'decided' in line_lower or 'decision:' in line_lower:
            patterns["decisions"].append(line.strip())
        
        # Lessons
        if 'lesson' in line_lower or 'learned' in line_lower or 'insight:' in line_lower:
            patterns["lessons"].append(line.strip())
        
        # Preferences (Jon said, Jon prefers, Jon wants)
        if 'jon' in line_lower and ('prefer' in line_lower or 'wants' in line_lower or 'said' in line_lower):
            patterns["preferences"].append(line.strip())
        
        # Feedback indicators
        if any(word in line_lower for word in ['👍', '👎', 'good', 'bad', 'wrong', 'right', 'correct']):
            patterns["feedback"].append(line.strip())
        
        # Tools/scripts mentioned
        script_match = re.findall(r'scripts/[\w-]+\.py', line)
        patterns["tools_used"].extend(script_match)
    
    # Deduplicate
    for key in patterns:
        patterns[key] = list(set(patterns[key]))
    
    return patterns

def score_importance(memory: str) -> float:
    """Score memory importance (0-1)"""
    score = 0.5  # Base score
    
    memory_lower = memory.lower()
    
    # High importance indicators
    if any(word in memory_lower for word in ['always', 'never', 'important', 'critical', 'remember']):
        score += 0.2
    
    # Jon-related = higher importance
    if 'jon' in memory_lower:
        score += 0.15
    
    # Explicit lesson = higher importance
    if 'lesson' in memory_lower or 'learned' in memory_lower:
        score += 0.1
    
    # Feedback = higher importance
    if any(word in memory_lower for word in ['feedback', 'corrected', 'mistake']):
        score += 0.15
    
    return min(score, 1.0)

def extract_memories(date_str: str) -> list:
    """Extract memories from a single day's log"""
    content = load_daily_log(date_str)
    if not content:
        return []
    
    patterns = extract_patterns(content)
    memories = []
    
    # Convert patterns to structured memories
    for decision in patterns["decisions"][:5]:  # Limit to prevent overload
        memories.append({
            "date": date_str,
            "type": "decision",
            "content": decision,
            "importance": score_importance(decision),
            "extracted_at": datetime.utcnow().isoformat()
        })
    
    for lesson in patterns["lessons"][:5]:
        memories.append({
            "date": date_str,
            "type": "lesson",
            "content": lesson,
            "importance": score_importance(lesson),
            "extracted_at": datetime.utcnow().isoformat()
        })
    
    for pref in patterns["preferences"][:5]:
        memories.append({
            "date": date_str,
            "type": "preference",
            "content": pref,
            "importance": score_importance(pref),
            "extracted_at": datetime.utcnow().isoformat()
        })
    
    return memories

def save_memories(memories: list):
    """Append memories to jsonl file"""
    with open(OUTPUT_FILE, 'a') as f:
        for memory in memories:
            f.write(json.dumps(memory) + '\n')

def summarize_extraction(memories: list):
    """Print summary of extraction"""
    if not memories:
        print("No memories extracted")
        return
    
    by_type = {}
    for m in memories:
        t = m["type"]
        by_type[t] = by_type.get(t, 0) + 1
    
    print(f"\nExtracted {len(memories)} memories:")
    for t, count in by_type.items():
        print(f"  {t}: {count}")
    
    # Show high importance ones
    high_importance = [m for m in memories if m["importance"] >= 0.7]
    if high_importance:
        print(f"\nHigh importance ({len(high_importance)}):")
        for m in high_importance[:5]:
            print(f"  [{m['type']}] {m['content'][:60]}...")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--week":
            # Process last 7 days
            dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        else:
            dates = [sys.argv[1]]
    else:
        dates = [datetime.now().strftime("%Y-%m-%d")]
    
    all_memories = []
    for date_str in dates:
        print(f"Processing {date_str}...")
        memories = extract_memories(date_str)
        all_memories.extend(memories)
    
    if all_memories:
        save_memories(all_memories)
        print(f"\nSaved to {OUTPUT_FILE}")
    
    summarize_extraction(all_memories)

if __name__ == "__main__":
    main()
