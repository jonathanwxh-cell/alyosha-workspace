#!/usr/bin/env python3
"""
Memory Blocks Manager
Check sizes, warn on limits, show status
"""

import os
import sys
from pathlib import Path

BLOCKS_DIR = Path.home() / ".openclaw/workspace/memory/blocks"

# Size limits in characters
LIMITS = {
    "human.md": 2000,
    "persona.md": 1000,
    "task-state.md": 1500,
    "knowledge.md": 3000,
}

def get_block_size(path):
    """Get character count of a file"""
    try:
        return len(path.read_text())
    except:
        return 0

def status():
    """Show status of all memory blocks"""
    print("Memory Blocks Status")
    print("=" * 50)
    
    total = 0
    for name, limit in LIMITS.items():
        path = BLOCKS_DIR / name
        size = get_block_size(path)
        total += size
        pct = (size / limit) * 100
        
        # Status indicator
        if pct >= 90:
            status = "🔴 FULL"
        elif pct >= 75:
            status = "🟠 HIGH"
        elif pct >= 50:
            status = "🟡 OK"
        else:
            status = "🟢 LOW"
        
        bar_len = int(pct / 5)  # 20 char bar
        bar = "█" * bar_len + "░" * (20 - bar_len)
        
        print(f"{name:15} [{bar}] {size:4}/{limit} ({pct:5.1f}%) {status}")
    
    print("-" * 50)
    total_limit = sum(LIMITS.values())
    print(f"{'Total':15} {total:4}/{total_limit} chars")

def check():
    """Check for blocks approaching limits, return warnings"""
    warnings = []
    for name, limit in LIMITS.items():
        path = BLOCKS_DIR / name
        size = get_block_size(path)
        pct = (size / limit) * 100
        
        if pct >= 90:
            warnings.append(f"🔴 {name}: {pct:.0f}% full - needs pruning!")
        elif pct >= 75:
            warnings.append(f"🟠 {name}: {pct:.0f}% full - consider pruning")
    
    if warnings:
        print("\n".join(warnings))
        return 1
    else:
        print("All blocks within limits ✓")
        return 0

def main():
    if len(sys.argv) < 2:
        status()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        status()
    elif cmd == "check":
        sys.exit(check())
    else:
        print(f"Usage: {sys.argv[0]} [status|check]")
        print("  status - Show all block sizes")
        print("  check  - Warn if any blocks near limit")

if __name__ == "__main__":
    main()
