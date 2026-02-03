#!/usr/bin/env python3
"""
Queue a stock for Sonnet analysis.

Usage:
    python3 queue-analysis.py NVDA           # Add to queue
    python3 queue-analysis.py NVDA AAPL SE   # Add multiple
    python3 queue-analysis.py --list         # Show queue
    python3 queue-analysis.py --clear        # Clear queue
"""

import sys
import json
from pathlib import Path
from datetime import datetime

QUEUE_FILE = Path(__file__).parent.parent / 'memory' / 'analysis-queue.json'

def load_queue():
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text())
    return {"queue": [], "completed": []}

def save_queue(data):
    QUEUE_FILE.write_text(json.dumps(data, indent=2))

def add_ticker(ticker):
    data = load_queue()
    # Check if already in queue
    existing = [t['ticker'] for t in data['queue']]
    if ticker.upper() in existing:
        print(f"⚠️  {ticker.upper()} already in queue")
        return
    
    data['queue'].append({
        "ticker": ticker.upper(),
        "added": datetime.now().strftime("%Y-%m-%d"),
        "priority": "normal"
    })
    save_queue(data)
    print(f"✅ Added {ticker.upper()} to analysis queue")

def list_queue():
    data = load_queue()
    if not data['queue']:
        print("📭 Queue is empty")
        return
    
    print("📊 Analysis Queue:")
    for i, item in enumerate(data['queue'], 1):
        print(f"  {i}. {item['ticker']} (added {item['added']})")
    
    if data.get('completed'):
        print(f"\n✅ Recently completed: {', '.join([c['ticker'] for c in data['completed'][-5:]])}")

def clear_queue():
    data = load_queue()
    data['queue'] = []
    save_queue(data)
    print("🗑️  Queue cleared")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        list_queue()
    elif sys.argv[1] == '--clear':
        clear_queue()
    else:
        for ticker in sys.argv[1:]:
            if not ticker.startswith('-'):
                add_ticker(ticker)
        list_queue()

if __name__ == '__main__':
    main()
