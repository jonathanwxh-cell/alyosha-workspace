#!/usr/bin/env python3
"""
Analysis Quality Tracker
========================

Tracks stock analysis quality over time and suggests framework improvements.

Usage:
    python3 scripts/analysis-quality.py log TICKER [1-7] "feedback"   # Log analysis
    python3 scripts/analysis-quality.py stats                          # Show quality trends
    python3 scripts/analysis-quality.py gaps                           # Show common gaps
    python3 scripts/analysis-quality.py improve                        # Suggest improvements
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from collections import Counter

FEEDBACK_FILE = Path.home() / '.openclaw/workspace/memory/analysis-feedback.jsonl'

def load_feedback():
    entries = []
    if FEEDBACK_FILE.exists():
        with open(FEEDBACK_FILE) as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except:
                        pass
    return entries

def log_analysis(ticker, dimensions, feedback, quality="pending"):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ticker": ticker.upper(),
        "dimensions_complete": int(dimensions),
        "feedback": feedback,
        "quality": quality
    }
    with open(FEEDBACK_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    print(f"✅ Logged: {ticker} ({dimensions}/7 dimensions)")

def show_stats():
    entries = load_feedback()
    if not entries:
        print("📭 No analysis feedback yet")
        return
    
    total = len(entries)
    avg_dimensions = sum(e.get('dimensions_complete', 0) for e in entries) / total
    full_coverage = sum(1 for e in entries if e.get('dimensions_complete', 0) == 7)
    
    print(f"📊 Analysis Quality Stats ({total} analyses)\n")
    print(f"Average dimensions covered: {avg_dimensions:.1f}/7")
    print(f"Full 7-dimension coverage: {full_coverage}/{total} ({full_coverage/total*100:.0f}%)")
    
    # Quality breakdown
    qualities = Counter(e.get('quality', 'unknown') for e in entries)
    print(f"\nQuality ratings:")
    for q, count in qualities.most_common():
        print(f"  {q}: {count}")

def show_gaps():
    entries = load_feedback()
    if not entries:
        print("📭 No feedback yet")
        return
    
    # Find common feedback themes
    all_feedback = ' '.join(e.get('feedback', '') for e in entries).lower()
    
    gap_keywords = {
        'porter': "Porter's 5 Forces (Dimension 5)",
        'industry': "Industry analysis (Dimension 5)",
        'second-order': "Second-order thinking (Dimension 7)",
        'priced in': "What's priced in (Dimension 7)",
        'scenario': "Risk/reward scenarios (Dimension 6)",
        'assumption': "Key assumptions (Dimension 6)",
        'insider': "Insider analysis depth (Dimension 3)",
        'transcript': "Transcript analysis (Dimensions 1-2)"
    }
    
    print("🔍 Common Gaps Detected:\n")
    found = False
    for keyword, description in gap_keywords.items():
        if keyword in all_feedback:
            print(f"  ⚠️  {description}")
            found = True
    
    if not found:
        print("  ✅ No systematic gaps detected")
    
    # Show incomplete analyses
    incomplete = [e for e in entries if e.get('dimensions_complete', 0) < 7]
    if incomplete:
        print(f"\n📋 Incomplete analyses ({len(incomplete)}):")
        for e in incomplete[-5:]:  # Last 5
            print(f"  {e.get('ticker')}: {e.get('dimensions_complete')}/7 — {e.get('feedback', '')[:50]}")

def suggest_improvements():
    entries = load_feedback()
    if len(entries) < 3:
        print("📭 Need more data (3+ analyses) for improvement suggestions")
        return
    
    print("💡 Framework Improvement Suggestions:\n")
    
    # Calculate coverage rates
    dim_coverage = sum(e.get('dimensions_complete', 0) for e in entries) / len(entries)
    
    if dim_coverage < 6:
        print("1. LOW DIMENSION COVERAGE")
        print("   → Update spawn task to explicitly list all 7 dimensions")
        print("   → Add dimension checklist to output template")
    
    # Check for repeated gaps
    all_feedback = ' '.join(e.get('feedback', '') for e in entries).lower()
    if 'second-order' in all_feedback or 'priced in' in all_feedback:
        print("\n2. SECOND-ORDER THINKING GAP")
        print("   → Add the 6 questions explicitly to spawn task")
        print("   → Require 'What's priced in' calculation")
    
    if 'porter' in all_feedback or 'industry' in all_feedback:
        print("\n3. INDUSTRY ANALYSIS GAP")
        print("   → Include Porter's template in spawn task")
        print("   → Require competitive positioning section")
    
    # Quality trend
    recent = entries[-5:]
    recent_quality = [e.get('quality', '') for e in recent]
    if recent_quality.count('good') >= 3:
        print("\n✅ RECENT QUALITY TREND: Good")
        print("   Framework working well, maintain current approach")
    
    print("\n📈 Continuous improvement: Run this monthly to track progress")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'log' and len(sys.argv) >= 4:
        ticker = sys.argv[2]
        dimensions = sys.argv[3]
        feedback = sys.argv[4] if len(sys.argv) > 4 else ""
        quality = sys.argv[5] if len(sys.argv) > 5 else "pending"
        log_analysis(ticker, dimensions, feedback, quality)
    
    elif cmd == 'stats':
        show_stats()
    
    elif cmd == 'gaps':
        show_gaps()
    
    elif cmd == 'improve':
        suggest_improvements()
    
    else:
        print(__doc__)

if __name__ == '__main__':
    main()
