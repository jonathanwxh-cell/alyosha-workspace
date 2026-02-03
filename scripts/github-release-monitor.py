#!/usr/bin/env python3
"""
GitHub Release Monitor - Event-driven trigger for new releases

Monitors repos for new releases and triggers alerts.
Designed for DeepSeek V4 watch but works for any repo.

Usage:
    python3 scripts/github-release-monitor.py                    # Check all watched repos
    python3 scripts/github-release-monitor.py deepseek-ai/DeepSeek-V3  # Check specific repo
    python3 scripts/github-release-monitor.py --add owner/repo   # Add repo to watchlist
    python3 scripts/github-release-monitor.py --list             # List watched repos
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path

STATE_FILE = Path.home() / ".openclaw/workspace/memory/github-watch-state.json"
WATCHLIST_FILE = Path.home() / ".openclaw/workspace/memory/github-watchlist.json"

# Default watchlist for AI model releases
DEFAULT_WATCHLIST = [
    {"repo": "deepseek-ai/DeepSeek-V3", "name": "DeepSeek", "priority": "high"},
    {"repo": "meta-llama/llama", "name": "Llama", "priority": "medium"},
    {"repo": "mistralai/mistral-src", "name": "Mistral", "priority": "medium"},
]

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_check": None, "known_releases": {}}

def save_state(state):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def load_watchlist():
    if WATCHLIST_FILE.exists():
        return json.loads(WATCHLIST_FILE.read_text())
    # Initialize with defaults
    WATCHLIST_FILE.parent.mkdir(parents=True, exist_ok=True)
    WATCHLIST_FILE.write_text(json.dumps(DEFAULT_WATCHLIST, indent=2))
    return DEFAULT_WATCHLIST

def save_watchlist(watchlist):
    WATCHLIST_FILE.write_text(json.dumps(watchlist, indent=2))

def check_github_releases(repo):
    """Check GitHub API for latest release."""
    try:
        result = subprocess.run(
            ["curl", "-s", f"https://api.github.com/repos/{repo}/releases?per_page=3"],
            capture_output=True, text=True, timeout=15
        )
        releases = json.loads(result.stdout)
        
        if isinstance(releases, list) and len(releases) > 0:
            latest = releases[0]
            return {
                "tag": latest.get("tag_name", ""),
                "name": latest.get("name", ""),
                "published": latest.get("published_at", ""),
                "url": latest.get("html_url", ""),
                "body": latest.get("body", "")[:500]  # First 500 chars of release notes
            }
        elif isinstance(releases, dict) and "message" in releases:
            return {"error": releases["message"]}
    except Exception as e:
        return {"error": str(e)}
    return None

def check_for_new_releases():
    """Check all watched repos for new releases."""
    state = load_state()
    watchlist = load_watchlist()
    known = state.get("known_releases", {})
    
    new_releases = []
    
    for item in watchlist:
        repo = item["repo"]
        name = item.get("name", repo)
        priority = item.get("priority", "medium")
        
        print(f"Checking {name} ({repo})...")
        release = check_github_releases(repo)
        
        if release and not release.get("error"):
            tag = release.get("tag", "")
            known_tag = known.get(repo, {}).get("tag", "")
            
            if tag and tag != known_tag:
                print(f"  🆕 NEW RELEASE: {tag}")
                new_releases.append({
                    "repo": repo,
                    "name": name,
                    "priority": priority,
                    "release": release
                })
                known[repo] = release
            else:
                print(f"  ✓ No change (latest: {tag})")
        elif release and release.get("error"):
            print(f"  ⚠️ Error: {release['error']}")
        else:
            print(f"  ⚠️ No releases found")
    
    # Update state
    state["last_check"] = datetime.now().isoformat()
    state["known_releases"] = known
    save_state(state)
    
    return new_releases

def format_alert(new_releases):
    """Format new releases as alert message."""
    if not new_releases:
        return None
    
    lines = ["🚨 **GitHub Release Alert**\n"]
    
    for item in new_releases:
        priority_emoji = "🔴" if item["priority"] == "high" else "🟡"
        release = item["release"]
        
        lines.append(f"{priority_emoji} **{item['name']}** — `{release['tag']}`")
        if release.get("name"):
            lines.append(f"   {release['name']}")
        lines.append(f"   📅 {release['published'][:10]}")
        lines.append(f"   🔗 {release['url']}")
        if release.get("body"):
            # First line of release notes
            first_line = release["body"].split('\n')[0][:100]
            lines.append(f"   📝 {first_line}...")
        lines.append("")
    
    return "\n".join(lines)

def add_repo(repo):
    """Add a repo to the watchlist."""
    watchlist = load_watchlist()
    
    # Check if already exists
    for item in watchlist:
        if item["repo"] == repo:
            print(f"Already watching: {repo}")
            return
    
    # Validate repo exists
    release = check_github_releases(repo)
    if release and release.get("error"):
        print(f"Warning: Could not access repo: {release['error']}")
    
    watchlist.append({
        "repo": repo,
        "name": repo.split("/")[-1],
        "priority": "medium"
    })
    save_watchlist(watchlist)
    print(f"Added to watchlist: {repo}")

def list_repos():
    """List all watched repos."""
    watchlist = load_watchlist()
    state = load_state()
    known = state.get("known_releases", {})
    
    print("📋 GitHub Watchlist\n")
    print(f"Last check: {state.get('last_check', 'never')}\n")
    
    for item in watchlist:
        repo = item["repo"]
        priority = item.get("priority", "medium")
        emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "⚪"
        
        known_release = known.get(repo, {})
        tag = known_release.get("tag", "unknown")
        
        print(f"{emoji} {item.get('name', repo)}")
        print(f"   Repo: {repo}")
        print(f"   Latest: {tag}")
        print()

def main():
    args = sys.argv[1:]
    
    if "--help" in args or "-h" in args:
        print(__doc__)
        return
    
    if "--list" in args:
        list_repos()
        return
    
    if "--add" in args:
        idx = args.index("--add")
        if idx + 1 < len(args):
            add_repo(args[idx + 1])
        else:
            print("Usage: --add owner/repo")
        return
    
    # Check specific repo or all
    if args and not args[0].startswith("-"):
        repo = args[0]
        print(f"Checking {repo}...")
        release = check_github_releases(repo)
        print(json.dumps(release, indent=2))
        return
    
    # Check all and report
    print("=" * 50)
    print("GitHub Release Monitor")
    print("=" * 50 + "\n")
    
    new_releases = check_for_new_releases()
    
    print("\n" + "=" * 50)
    if new_releases:
        alert = format_alert(new_releases)
        print("\n" + alert)
        print("ACTION: Send alert to Jon!")
    else:
        print("\n✓ No new releases detected")

if __name__ == "__main__":
    main()
