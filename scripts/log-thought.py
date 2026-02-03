#!/usr/bin/env python3
"""
Log structured thoughts to memory/thoughts/YYYY-MM.jsonl

Usage:
  log-thought.py conversation --topic "vector db" --summary "Discussed when to add vector DB" --entities "jon,memory-system" --decision "improve logging first"
  log-thought.py thought --content "Barbell applies to time allocation too" --tags "framework,meta"
  log-thought.py connection --from "AI-capex" --to "nuclear" --relationship "power demand driver"
  log-thought.py decision --what "Use Chroma when ready" --why "free, local, simple" --entities "vector-db"
  log-thought.py question --question "When does retrieval feel inadequate?" --context "vector db timing" --status "open"
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

THOUGHTS_DIR = Path.home() / ".openclaw/workspace/memory/thoughts"

def ensure_dir():
    THOUGHTS_DIR.mkdir(parents=True, exist_ok=True)

def get_log_path():
    return THOUGHTS_DIR / f"{datetime.utcnow().strftime('%Y-%m')}.jsonl"

def log_entry(entry: dict):
    ensure_dir()
    entry["ts"] = datetime.utcnow().isoformat() + "Z"
    
    with open(get_log_path(), "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Logged {entry['type']} to {get_log_path().name}")
    return entry

def parse_list(s: str) -> list:
    if not s:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]

def main():
    parser = argparse.ArgumentParser(description="Log structured thoughts")
    subparsers = parser.add_subparsers(dest="type", required=True)
    
    # conversation
    conv = subparsers.add_parser("conversation")
    conv.add_argument("--topic", required=True)
    conv.add_argument("--summary", required=True)
    conv.add_argument("--entities", default="")
    conv.add_argument("--tags", default="")
    conv.add_argument("--decision", default="")
    conv.add_argument("--insight", default="")
    conv.add_argument("--sentiment", default="neutral", 
                      choices=["positive", "neutral", "negative", "curious"])
    
    # thought
    thought = subparsers.add_parser("thought")
    thought.add_argument("--content", required=True)
    thought.add_argument("--sparked-by", dest="sparked_by", default="")
    thought.add_argument("--entities", default="")
    thought.add_argument("--tags", default="")
    thought.add_argument("--confidence", type=float, default=0.7)
    thought.add_argument("--actionable", action="store_true")
    
    # connection
    conn = subparsers.add_parser("connection")
    conn.add_argument("--from", dest="from_entity", required=True)
    conn.add_argument("--to", required=True)
    conn.add_argument("--relationship", required=True)
    conn.add_argument("--strength", type=float, default=0.5)
    conn.add_argument("--novel", action="store_true")
    
    # decision
    dec = subparsers.add_parser("decision")
    dec.add_argument("--what", required=True)
    dec.add_argument("--why", required=True)
    dec.add_argument("--alternatives", default="")
    dec.add_argument("--entities", default="")
    dec.add_argument("--reversible", action="store_true", default=True)
    
    # question
    q = subparsers.add_parser("question")
    q.add_argument("--question", required=True)
    q.add_argument("--context", default="")
    q.add_argument("--entities", default="")
    q.add_argument("--status", default="open", choices=["open", "answered", "dropped"])
    q.add_argument("--answer", default="")
    
    args = parser.parse_args()
    
    entry = {"type": args.type}
    
    if args.type == "conversation":
        entry.update({
            "topic": args.topic,
            "summary": args.summary,
            "entities": parse_list(args.entities),
            "tags": parse_list(args.tags),
            "sentiment": args.sentiment
        })
        if args.decision: entry["decision"] = args.decision
        if args.insight: entry["insight"] = args.insight
        
    elif args.type == "thought":
        entry.update({
            "content": args.content,
            "entities": parse_list(args.entities),
            "tags": parse_list(args.tags),
            "confidence": args.confidence,
            "actionable": args.actionable
        })
        if args.sparked_by: entry["sparked_by"] = args.sparked_by
        
    elif args.type == "connection":
        entry.update({
            "from": args.from_entity,
            "to": args.to,
            "relationship": args.relationship,
            "strength": args.strength,
            "novel": args.novel
        })
        
    elif args.type == "decision":
        entry.update({
            "what": args.what,
            "why": args.why,
            "alternatives": parse_list(args.alternatives),
            "entities": parse_list(args.entities),
            "reversible": args.reversible
        })
        
    elif args.type == "question":
        entry.update({
            "question": args.question,
            "context": args.context,
            "entities": parse_list(args.entities),
            "status": args.status
        })
        if args.answer: entry["answer"] = args.answer
    
    log_entry(entry)

if __name__ == "__main__":
    main()
