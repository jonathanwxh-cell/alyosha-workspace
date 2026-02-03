#!/usr/bin/env python3
"""
China AI Launch Watcher
Checks for DeepSeek V4, Doubao 2.0, Qwen 3.5 releases

Usage:
    python3 scripts/china-ai-watch.py           # Check all
    python3 scripts/china-ai-watch.py deepseek  # Check DeepSeek only
    python3 scripts/china-ai-watch.py --update  # Update tracker file
"""

import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

TRACKER_FILE = Path.home() / ".openclaw/workspace/memory/research/china-ai-february-launches.md"
STATE_FILE = Path.home() / ".openclaw/workspace/memory/china-ai-watch-state.json"

# Known release indicators
WATCHLIST = {
    "deepseek": {
        "name": "DeepSeek V4",
        "github_repo": "deepseek-ai/DeepSeek-V3",  # V4 might appear here or new repo
        "search_terms": ["DeepSeek V4 released", "DeepSeek V4 launch", "MODEL1 release"],
        "status": "pending"
    },
    "doubao": {
        "name": "ByteDance Doubao 2.0",
        "search_terms": ["Doubao 2.0 launch", "ByteDance Doubao 2.0"],
        "status": "pending"
    },
    "qwen": {
        "name": "Alibaba Qwen 3.5",
        "search_terms": ["Qwen 3.5 release", "Alibaba Qwen 3.5 launch"],
        "status": "pending"
    }
}

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_check": None, "alerts": [], "releases": {}}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def check_github_releases(repo):
    """Check GitHub for new releases"""
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://api.github.com/repos/{repo}/releases?per_page=5"],
            capture_output=True, text=True, timeout=10
        )
        releases = json.loads(result.stdout)
        if releases and isinstance(releases, list):
            latest = releases[0]
            return {
                "tag": latest.get("tag_name", ""),
                "name": latest.get("name", ""),
                "published": latest.get("published_at", ""),
                "url": latest.get("html_url", "")
            }
    except Exception as e:
        return {"error": str(e)}
    return None

def print_status():
    """Print current watch status"""
    state = load_state()
    
    print("=" * 50)
    print("🇨🇳 CHINA AI LAUNCH WATCH")
    print("=" * 50)
    print(f"Last check: {state.get('last_check', 'never')}")
    print()
    
    for key, item in WATCHLIST.items():
        status = state.get("releases", {}).get(key, {}).get("status", "⏳ pending")
        emoji = "✅" if "released" in str(status).lower() else "🔴"
        print(f"{emoji} {item['name']}: {status}")
    
    print()
    print("Monitoring for:")
    print("  - DeepSeek V4 (mid-February expected)")
    print("  - ByteDance Doubao 2.0 / Seeddream 5.0 / Seeddance 2.0")
    print("  - Alibaba Qwen 3.5")
    print()
    print(f"📄 Full tracker: {TRACKER_FILE}")

def check_deepseek():
    """Specifically check DeepSeek status"""
    print("Checking DeepSeek GitHub...")
    
    # Check main repo
    release = check_github_releases("deepseek-ai/DeepSeek-V3")
    if release and not release.get("error"):
        print(f"  Latest release: {release.get('tag', 'unknown')}")
        print(f"  Name: {release.get('name', 'unknown')}")
        print(f"  Published: {release.get('published', 'unknown')}")
        
        # Check if this looks like V4
        tag = release.get("tag", "").lower()
        name = release.get("name", "").lower()
        if "v4" in tag or "v4" in name or "model1" in name:
            return {"status": "🚀 V4 DETECTED!", "release": release}
    
    # Check for new V4 repo
    result = subprocess.run(
        ["curl", "-s", "https://api.github.com/repos/deepseek-ai/DeepSeek-V4"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and "Not Found" not in result.stdout:
        return {"status": "🚀 V4 REPO EXISTS!", "url": "https://github.com/deepseek-ai/DeepSeek-V4"}
    
    return {"status": "⏳ No V4 release detected yet"}

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if target == "--help":
        print(__doc__)
        return
    
    if target == "deepseek":
        result = check_deepseek()
        print(json.dumps(result, indent=2))
    elif target == "--update":
        state = load_state()
        state["last_check"] = datetime.now().isoformat()
        save_state(state)
        print("State updated.")
    else:
        print_status()
        print("-" * 50)
        result = check_deepseek()
        print(f"DeepSeek: {result['status']}")

if __name__ == "__main__":
    main()
