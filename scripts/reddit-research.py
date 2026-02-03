#!/usr/bin/env python3
"""
Reddit Research Tool - Free, no API key needed
Uses Reddit's public JSON endpoints
"""

import requests
import json
import sys
from datetime import datetime, timezone

SUBREDDITS = {
    # AI/Tech
    "singularity": "AGI, superintelligence discussions",
    "MachineLearning": "ML research, papers",
    "LocalLLaMA": "Open source LLMs, self-hosting",
    "artificial": "AI news and discussion",
    
    # Markets
    "wallstreetbets": "Retail sentiment, meme stocks",
    "stocks": "General stock discussion",
    "options": "Options trading",
    "semiconductors": "Chip industry news",
    
    # Tech/Science
    "technology": "Tech news",
    "science": "Scientific discoveries",
    "Futurology": "Future tech, trends",
    
    # Geo
    "geopolitics": "Global politics analysis",
    "worldnews": "Breaking news",
    
    # Singapore
    "singapore": "Local news, discussion",
}

HEADERS = {"User-Agent": "AlyoshaResearch/1.0"}

def fetch_subreddit(sub: str, limit: int = 10, sort: str = "hot") -> list:
    """Fetch posts from a subreddit"""
    url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit={limit}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            p = child.get("data", {})
            posts.append({
                "title": p.get("title", ""),
                "score": p.get("score", 0),
                "comments": p.get("num_comments", 0),
                "url": f"https://reddit.com{p.get('permalink', '')}",
                "created": datetime.fromtimestamp(p.get("created_utc", 0), tz=timezone.utc).isoformat(),
                "selftext": p.get("selftext", "")[:500],  # First 500 chars
            })
        return posts
    except Exception as e:
        return [{"error": str(e)}]

def search_reddit(query: str, limit: int = 10) -> list:
    """Search across Reddit"""
    url = f"https://www.reddit.com/search.json?q={query}&limit={limit}&sort=relevance&t=week"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        posts = []
        for child in data.get("data", {}).get("children", []):
            p = child.get("data", {})
            posts.append({
                "subreddit": p.get("subreddit", ""),
                "title": p.get("title", ""),
                "score": p.get("score", 0),
                "url": f"https://reddit.com{p.get('permalink', '')}",
            })
        return posts
    except Exception as e:
        return [{"error": str(e)}]

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  reddit-research.py <subreddit>          # Fetch hot posts")
        print("  reddit-research.py <subreddit> new      # Fetch new posts")
        print("  reddit-research.py search <query>       # Search Reddit")
        print("  reddit-research.py list                 # List tracked subs")
        print("  reddit-research.py scan                 # Scan all tracked subs")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "list":
        print("Tracked subreddits:")
        for sub, desc in SUBREDDITS.items():
            print(f"  r/{sub}: {desc}")
    
    elif cmd == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "AI"
        posts = search_reddit(query)
        print(f"Search results for '{query}':\n")
        for p in posts[:10]:
            title = p.get('title', '') or ''
            print(f"[{p.get('score', 0):>5}] r/{p.get('subreddit')}: {title[:80]}")
            print(f"        {p.get('url')}\n")
    
    elif cmd == "scan":
        print("Scanning tracked subreddits...\n")
        for sub in SUBREDDITS:
            posts = fetch_subreddit(sub, limit=3)
            if posts and "error" not in posts[0]:
                print(f"=== r/{sub} ===")
                for p in posts:
                    print(f"  [{p['score']:>5}] {p['title'][:70]}")
                print()
    
    else:
        # Treat as subreddit name
        sub = cmd.replace("r/", "")
        sort = sys.argv[2] if len(sys.argv) > 2 else "hot"
        posts = fetch_subreddit(sub, limit=10, sort=sort)
        
        print(f"r/{sub} ({sort}):\n")
        for p in posts:
            if "error" in p:
                print(f"Error: {p['error']}")
            else:
                print(f"[{p['score']:>5}] {p['title'][:75]}")
                print(f"        💬 {p['comments']} comments | {p['url']}")
                if p['selftext']:
                    print(f"        {p['selftext'][:150]}...")
                print()

if __name__ == "__main__":
    main()
