#!/usr/bin/env python3
"""
Signal Watcher - Event-driven news/signal monitoring
Catches external events, scores relevance, triggers actions.
"""

import json
import feedparser
import requests
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import sys
import os

# Paths
WORKSPACE = Path(__file__).parent.parent
TOPIC_GRAPH = WORKSPACE / "memory" / "topic-graph.json"
CURIOSITIES = WORKSPACE / "memory" / "curiosities.json"
SIGNALS_LOG = WORKSPACE / "memory" / "signals.jsonl"
SIGNAL_QUEUE = WORKSPACE / "memory" / "signal-queue.json"
SEEN_SIGNALS = WORKSPACE / "memory" / "seen-signals.json"

# RSS Feeds to monitor
RSS_FEEDS = {
    "hackernews": "https://hnrss.org/frontpage",
    "arxiv_ai": "http://export.arxiv.org/rss/cs.AI",
    "arxiv_ml": "http://export.arxiv.org/rss/cs.LG",
    "techcrunch_ai": "https://techcrunch.com/tag/artificial-intelligence/feed/",
}

# Keywords that boost relevance
BOOST_KEYWORDS = [
    "nvidia", "nvda", "deepseek", "openai", "anthropic", "claude",
    "spacex", "ipo", "starlink", "robotics", "humanoid",
    "ai capex", "hyperscaler", "datacenter", "inference",
    "world model", "embodied ai", "protein", "biotech",
    "singapore", "mas", "sgd"
]

def load_json(path, default=None):
    """Load JSON file or return default."""
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return default or {}

def save_json(path, data):
    """Save JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def append_jsonl(path, record):
    """Append to JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'a') as f:
        f.write(json.dumps(record) + '\n')

def get_signal_id(title, url):
    """Generate unique signal ID."""
    content = f"{title}:{url}"
    return hashlib.md5(content.encode()).hexdigest()[:12]

def fetch_rss_signals():
    """Fetch signals from RSS feeds."""
    signals = []
    
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:  # Latest 15 per feed
                signal = {
                    "id": get_signal_id(entry.get("title", ""), entry.get("link", "")),
                    "source": source,
                    "type": "rss",
                    "title": entry.get("title", "")[:200],
                    "url": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500] if entry.get("summary") else "",
                    "published": entry.get("published", ""),
                    "fetched_at": datetime.utcnow().isoformat() + "Z"
                }
                signals.append(signal)
        except Exception as e:
            print(f"  [!] Error fetching {source}: {e}", file=sys.stderr)
    
    return signals

def fetch_brave_signals(query, count=5):
    """Fetch recent news via Brave Search."""
    api_key = os.environ.get("BRAVE_API_KEY")
    if not api_key:
        # Try loading from config
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        if config_path.exists():
            config = load_json(config_path)
            api_key = config.get("braveApiKey")
    
    if not api_key:
        return []
    
    signals = []
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/news/search",
            params={"q": query, "count": count, "freshness": "pd"},  # past day
            headers={"X-Subscription-Token": api_key},
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            for result in data.get("results", []):
                signal = {
                    "id": get_signal_id(result.get("title", ""), result.get("url", "")),
                    "source": "brave",
                    "type": "news",
                    "title": result.get("title", "")[:200],
                    "url": result.get("url", ""),
                    "summary": result.get("description", "")[:500],
                    "published": result.get("age", ""),
                    "fetched_at": datetime.utcnow().isoformat() + "Z"
                }
                signals.append(signal)
    except Exception as e:
        print(f"  [!] Brave search error: {e}", file=sys.stderr)
    
    return signals

def score_signal(signal, topic_graph, curiosities):
    """Score signal relevance based on topic graph and curiosities."""
    title = signal.get("title", "").lower()
    summary = signal.get("summary", "").lower()
    content = f"{title} {summary}"
    
    score = 0.0
    matched_topics = []
    matched_curiosities = []
    
    # Score against topic graph
    topics = topic_graph.get("topics", {})
    for topic_name, topic_data in topics.items():
        weight = topic_data.get("engagementScore", topic_data.get("weight", 0.5))
        # Use label, related terms, and topic name as keywords
        keywords = [topic_name.replace("_", " ")]
        keywords.append(topic_data.get("label", "").lower())
        keywords.extend([r.replace("_", " ") for r in topic_data.get("related", [])])
        
        for kw in keywords:
            if kw and kw.lower() in content:
                topic_score = weight * 0.4
                score += topic_score
                if topic_name not in matched_topics:
                    matched_topics.append(topic_name)
                break
    
    # Score against curiosities
    for curiosity in curiosities.get("curiosities", []):
        thread = curiosity.get("thread", "").lower()
        notes = curiosity.get("notes", "").lower()
        
        # Check if signal relates to curiosity
        thread_words = [w for w in thread.split() if len(w) > 4]
        matches = sum(1 for w in thread_words if w in content)
        if matches >= 2:
            score += 0.3
            matched_curiosities.append(curiosity.get("id", "unknown"))
    
    # Boost for high-priority keywords
    for kw in BOOST_KEYWORDS:
        if kw in content:
            score += 0.15
    
    # Cross-topic bonus (connecting multiple domains)
    if len(matched_topics) >= 2:
        score += 0.2 * (len(matched_topics) - 1)
    
    # Cap at 1.0
    score = min(score, 1.0)
    
    return {
        "score": round(score, 3),
        "matched_topics": matched_topics,
        "matched_curiosities": matched_curiosities,
        "cross_topic": len(matched_topics) >= 2
    }

def filter_seen(signals, seen_ids):
    """Filter out already-seen signals."""
    return [s for s in signals if s["id"] not in seen_ids]

def main():
    print(f"🔍 Signal Watcher - {datetime.utcnow().isoformat()}Z")
    
    # Load context
    topic_graph = load_json(TOPIC_GRAPH, {"topics": {}})
    curiosities = load_json(CURIOSITIES, {"curiosities": []})
    seen = load_json(SEEN_SIGNALS, {"ids": [], "last_run": None})
    seen_ids = set(seen.get("ids", []))
    
    # Collect signals
    print("\n📡 Fetching signals...")
    all_signals = []
    
    # RSS feeds
    rss_signals = fetch_rss_signals()
    print(f"  RSS: {len(rss_signals)} items")
    all_signals.extend(rss_signals)
    
    # Brave search for key topics (limit to avoid rate limits)
    brave_queries = ["NVIDIA AI", "DeepSeek", "AI agents"]
    for query in brave_queries[:2]:  # Limit queries
        brave_signals = fetch_brave_signals(query, count=3)
        print(f"  Brave '{query}': {len(brave_signals)} items")
        all_signals.extend(brave_signals)
    
    # Filter seen
    new_signals = filter_seen(all_signals, seen_ids)
    print(f"\n📊 New signals: {len(new_signals)} (filtered {len(all_signals) - len(new_signals)} seen)")
    
    if not new_signals:
        print("No new signals. Done.")
        return {"high": [], "queued": 0}
    
    # Score signals
    print("\n⚖️ Scoring signals...")
    scored = []
    for signal in new_signals:
        result = score_signal(signal, topic_graph, curiosities)
        signal["relevance"] = result
        scored.append(signal)
        
        # Log all signals
        append_jsonl(SIGNALS_LOG, signal)
        
        # Mark as seen
        seen_ids.add(signal["id"])
    
    # Sort by score
    scored.sort(key=lambda x: x["relevance"]["score"], reverse=True)
    
    # Categorize
    high_priority = [s for s in scored if s["relevance"]["score"] >= 0.5]
    
    # Queue medium signals for synthesis
    queue = load_json(SIGNAL_QUEUE, {"signals": []})
    for s in scored:
        if 0.3 <= s["relevance"]["score"] < 0.5:
            queue["signals"].append({
                "id": s["id"],
                "title": s["title"],
                "url": s["url"],
                "score": s["relevance"]["score"],
                "topics": s["relevance"]["matched_topics"],
                "added_at": datetime.utcnow().isoformat() + "Z"
            })
    
    # Keep queue manageable
    queue["signals"] = queue["signals"][-50:]
    save_json(SIGNAL_QUEUE, queue)
    
    # Update seen
    seen["ids"] = list(seen_ids)[-500:]  # Keep last 500
    seen["last_run"] = datetime.utcnow().isoformat() + "Z"
    save_json(SEEN_SIGNALS, seen)
    
    # Report
    print(f"\n🎯 Results:")
    print(f"  High priority (≥0.5): {len(high_priority)}")
    print(f"  Queued for synthesis: {len([s for s in scored if 0.3 <= s['relevance']['score'] < 0.5])}")
    
    if high_priority:
        print(f"\n🔥 HIGH PRIORITY SIGNALS:")
        for s in high_priority[:5]:
            print(f"\n  [{s['relevance']['score']:.2f}] {s['title'][:80]}")
            print(f"       Topics: {', '.join(s['relevance']['matched_topics'])}")
            print(f"       URL: {s['url']}")
            if s['relevance']['cross_topic']:
                print(f"       ⚡ CROSS-TOPIC CONNECTION")
    
    return {
        "high": high_priority[:5],
        "queued": len(queue["signals"])
    }

if __name__ == "__main__":
    result = main()
    
    # Output for cron integration
    if result["high"]:
        print("\n" + "="*50)
        print("ACTION: High-priority signals detected. Consider surfacing to Jon.")
