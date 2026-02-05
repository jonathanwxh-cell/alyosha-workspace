#!/usr/bin/env python3
"""
Message Source Logger

Logs incoming messages with metadata to help trace origins.
Call at start of main session interactions to track what triggered them.

Usage:
    python3 scripts/message-logger.py log "<message_preview>" "<source>" [metadata]
    python3 scripts/message-logger.py recent [count]
    python3 scripts/message-logger.py analyze
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path.home() / ".openclaw/workspace/memory/message-sources.jsonl"
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

def log_message(preview: str, source: str, metadata: dict = None):
    """Log a message with its source."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "preview": preview[:200],  # First 200 chars
        "source": source,  # telegram, cron, systemEvent, wake, unknown
        "metadata": metadata or {},
        "has_telegram_header": "[Telegram" in preview or "[message_id:" in preview,
        "has_cron_marker": "Cron:" in preview or "[Cron]" in preview,
        "raw_injection": not ("[Telegram" in preview or "Cron:" in preview)
    }
    
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')
    
    return entry

def recent(count: int = 10):
    """Show recent logged messages."""
    if not LOG_FILE.exists():
        return []
    
    entries = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    return entries[-count:]

def analyze():
    """Analyze message source patterns."""
    if not LOG_FILE.exists():
        return {"total": 0, "message": "No logs yet"}
    
    entries = []
    with open(LOG_FILE, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except:
                    pass
    
    sources = {}
    raw_injections = 0
    telegram_count = 0
    
    for e in entries:
        src = e.get('source', 'unknown')
        sources[src] = sources.get(src, 0) + 1
        if e.get('raw_injection'):
            raw_injections += 1
        if e.get('has_telegram_header'):
            telegram_count += 1
    
    return {
        "total": len(entries),
        "sources": sources,
        "raw_injections": raw_injections,
        "telegram_messages": telegram_count,
        "mystery_ratio": f"{raw_injections}/{len(entries)}" if entries else "0/0"
    }

def classify_source(message: str) -> str:
    """Auto-classify message source based on content."""
    if "[Telegram" in message and "id:" in message:
        return "telegram"
    if "Cron:" in message or "[Cron]" in message:
        return "cron_ack"
    if message.startswith("System:") or message.startswith("[System"):
        return "system"
    if "HEARTBEAT" in message.upper() or "heartbeat" in message.lower():
        return "heartbeat"
    if any(marker in message for marker in ["[EXPLORATION]", "[RESEARCH]", "AGENT PATTERNS", "[TRADING]"]):
        return "systemEvent_prompt"
    return "unknown"

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'log':
        if len(sys.argv) < 3:
            print("Usage: message-logger.py log '<preview>' [source] [metadata_json]")
            return
        
        preview = sys.argv[2]
        source = sys.argv[3] if len(sys.argv) > 3 else classify_source(preview)
        metadata = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
        
        entry = log_message(preview, source, metadata)
        print(json.dumps(entry, indent=2))
    
    elif cmd == 'recent':
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        entries = recent(count)
        for e in entries:
            ts = e.get('timestamp', '')[:19]
            src = e.get('source', '?')
            prev = e.get('preview', '')[:60]
            raw = "⚠️" if e.get('raw_injection') else "✓"
            print(f"[{ts}] {raw} {src:15} | {prev}...")
    
    elif cmd == 'analyze':
        result = analyze()
        print(json.dumps(result, indent=2))
    
    elif cmd == 'classify':
        if len(sys.argv) < 3:
            print("Usage: message-logger.py classify '<message>'")
            return
        print(classify_source(sys.argv[2]))
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
