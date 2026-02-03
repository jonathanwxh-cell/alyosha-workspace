#!/usr/bin/env python3
"""
Research Scanner - Aggregates from free sources
HackerNews, ArXiv, web search
"""

import requests
import json
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

def fetch_hackernews(query: str = None, limit: int = 10) -> list:
    """Fetch top HN stories, optionally filtered by query"""
    try:
        # Get top story IDs
        resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = resp.json()[:50]  # Get top 50, filter down
        
        stories = []
        for sid in story_ids:
            if len(stories) >= limit:
                break
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5).json()
            if item and item.get("title"):
                title = item.get("title", "").lower()
                if query is None or query.lower() in title:
                    stories.append({
                        "title": item.get("title"),
                        "score": item.get("score", 0),
                        "comments": item.get("descendants", 0),
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "hn_url": f"https://news.ycombinator.com/item?id={sid}",
                    })
        return stories
    except Exception as e:
        return [{"error": str(e)}]

def fetch_arxiv(query: str, limit: int = 10) -> list:
    """Search ArXiv for papers"""
    try:
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
        resp = requests.get(url, timeout=15)
        
        # Parse XML
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        papers = []
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns)
            summary = entry.find("atom:summary", ns)
            link = entry.find("atom:id", ns)
            published = entry.find("atom:published", ns)
            
            papers.append({
                "title": title.text.strip().replace("\n", " ") if title is not None else "",
                "abstract": summary.text.strip()[:300] if summary is not None else "",
                "url": link.text if link is not None else "",
                "published": published.text[:10] if published is not None else "",
            })
        return papers
    except Exception as e:
        return [{"error": str(e)}]

def scan_all(topics: list = None) -> dict:
    """Scan all sources for given topics"""
    if topics is None:
        topics = ["AI", "DeepSeek", "NVIDIA", "robotics"]
    
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "hackernews": [],
        "arxiv": {},
    }
    
    # HackerNews top stories
    print("Scanning HackerNews...")
    results["hackernews"] = fetch_hackernews(limit=15)
    
    # ArXiv for each topic
    for topic in topics:
        print(f"Scanning ArXiv for '{topic}'...")
        results["arxiv"][topic] = fetch_arxiv(topic, limit=5)
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  research-scan.py hn                  # HackerNews top stories")
        print("  research-scan.py hn <query>          # Filter HN by keyword")
        print("  research-scan.py arxiv <query>       # Search ArXiv")
        print("  research-scan.py scan                # Full scan of all sources")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "hn":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        stories = fetch_hackernews(query, limit=15)
        
        print(f"HackerNews{' (filtered: ' + query + ')' if query else ''}:\n")
        for s in stories:
            if "error" in s:
                print(f"Error: {s['error']}")
            else:
                print(f"[{s['score']:>4}] {s['title'][:75]}")
                print(f"       💬 {s['comments']} | {s['hn_url']}")
                print()
    
    elif cmd == "arxiv":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "machine learning"
        papers = fetch_arxiv(query, limit=10)
        
        print(f"ArXiv search: '{query}'\n")
        for p in papers:
            if "error" in p:
                print(f"Error: {p['error']}")
            else:
                print(f"📄 {p['title'][:80]}")
                print(f"   {p['published']} | {p['url']}")
                print(f"   {p['abstract'][:150]}...")
                print()
    
    elif cmd == "scan":
        topics = sys.argv[2:] if len(sys.argv) > 2 else ["AI agents", "DeepSeek", "robotics", "consciousness"]
        results = scan_all(topics)
        
        print("\n=== HACKERNEWS TOP ===\n")
        for s in results["hackernews"][:10]:
            if "error" not in s:
                print(f"[{s['score']:>4}] {s['title'][:70]}")
        
        print("\n=== ARXIV RECENT ===\n")
        for topic, papers in results["arxiv"].items():
            print(f"--- {topic} ---")
            for p in papers[:3]:
                if "error" not in p:
                    print(f"  • {p['title'][:65]}")
            print()
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
