#!/usr/bin/env python3
"""
search-history.py - Search past conversation history

Searches through OpenClaw session transcripts for keywords or phrases.

Usage:
  python3 scripts/search-history.py "vector database"
  python3 scripts/search-history.py "fmp" --limit 5
  python3 scripts/search-history.py "nvidia" --user-only
  python3 scripts/search-history.py "pricing" --questions
  
Options:
  --limit N       Max results (default: 10)
  --user-only     Only search user messages (Jon's questions)
  --assistant-only Only search assistant messages  
  --questions     Only find questions (ends with ?)
  --days N        Only search last N days
  --context       Show surrounding context
"""

import json
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta

SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
SESSIONS_INDEX = SESSIONS_DIR / "sessions.json"

def load_sessions_index():
    """Load the sessions index (key-value format)."""
    if not SESSIONS_INDEX.exists():
        return {}
    with open(SESSIONS_INDEX) as f:
        content = f.read()
        # Handle potential trailing commas (JSON5-ish)
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse sessions.json: {e}", file=sys.stderr)
            return {}
    return data

def extract_text_from_content(content) -> str:
    """Extract readable text from message content."""
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict):
                if part.get("type") == "text":
                    texts.append(part.get("text", ""))
            elif isinstance(part, str):
                texts.append(part)
        return " ".join(texts)
    
    return ""

def load_transcript(session_id: str) -> list:
    """Load messages from a transcript JSONL file."""
    transcript_file = SESSIONS_DIR / f"{session_id}.jsonl"
    if not transcript_file.exists():
        return []
    
    messages = []
    with open(transcript_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                
                # Handle message events
                if event.get("type") == "message":
                    msg_data = event.get("message", {})
                    role = msg_data.get("role", "")
                    content = msg_data.get("content", "")
                    timestamp = event.get("timestamp", "")
                    
                    # Skip tool results
                    if role == "toolResult":
                        continue
                    
                    text = extract_text_from_content(content)
                    if text and role in ("user", "assistant"):
                        messages.append({
                            "role": role,
                            "content": text,
                            "timestamp": timestamp
                        })
            except json.JSONDecodeError:
                continue
    return messages

def search_sessions(query: str, limit: int = 10, user_only: bool = False, 
                   assistant_only: bool = False, questions_only: bool = False,
                   days: int = None, show_context: bool = False) -> list:
    """Search through all sessions for matching messages."""
    
    sessions = load_sessions_index()
    results = []
    query_lower = query.lower()
    
    # Filter by date if specified
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_ts = cutoff.timestamp() * 1000
    else:
        cutoff_ts = 0
    
    # Iterate through sessions (dict format)
    for session_key, session_data in sessions.items():
        if not isinstance(session_data, dict):
            continue
            
        # Skip if too old
        updated_at = session_data.get("updatedAt", 0)
        if updated_at < cutoff_ts:
            continue
        
        session_id = session_data.get("sessionId")
        if not session_id:
            continue
        
        messages = load_transcript(session_id)
        
        for i, msg in enumerate(messages):
            role = msg.get("role", "")
            
            # Filter by role
            if user_only and role != "user":
                continue
            if assistant_only and role != "assistant":
                continue
            
            text = msg.get("content", "")
            if not text:
                continue
            
            # Filter for questions
            if questions_only and "?" not in text:
                continue
            
            # Search
            if query_lower in text.lower():
                timestamp = msg.get("timestamp", "")
                if isinstance(timestamp, str) and timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        date_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        date_str = timestamp[:16] if timestamp else "unknown"
                else:
                    date_str = "unknown"
                
                # Truncate session key for display
                short_key = session_key
                if len(short_key) > 30:
                    short_key = short_key[:27] + "..."
                
                result = {
                    "session": short_key,
                    "role": role,
                    "text": text[:500] + ("..." if len(text) > 500 else ""),
                    "timestamp": timestamp,
                    "date": date_str
                }
                
                # Add context if requested
                if show_context and len(messages) > 1:
                    if i > 0:
                        result["context_before"] = messages[i-1].get("content", "")[:200]
                    if i < len(messages) - 1:
                        result["context_after"] = messages[i+1].get("content", "")[:200]
                
                results.append(result)
                
                if len(results) >= limit:
                    return results
    
    return results

def format_results(results: list, show_context: bool = False) -> str:
    """Format search results for display."""
    if not results:
        return "No matches found."
    
    output = [f"🔍 Found {len(results)} match(es):\n"]
    
    for i, r in enumerate(results, 1):
        role_emoji = "👤" if r["role"] == "user" else "🤖"
        output.append(f"{'─' * 60}")
        output.append(f"{i}. {role_emoji} [{r['date']}]")
        output.append(f"   {r['text'][:400]}{'...' if len(r['text']) > 400 else ''}")
        
        if show_context:
            if r.get("context_before"):
                output.append(f"   ↑ Before: {r['context_before'][:150]}...")
            if r.get("context_after"):
                output.append(f"   ↓ After: {r['context_after'][:150]}...")
    
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Search conversation history")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", "-l", type=int, default=10, help="Max results")
    parser.add_argument("--user-only", "-u", action="store_true", help="Only user messages")
    parser.add_argument("--assistant-only", "-a", action="store_true", help="Only assistant messages")
    parser.add_argument("--questions", "-q", action="store_true", help="Only questions")
    parser.add_argument("--days", "-d", type=int, help="Only last N days")
    parser.add_argument("--context", "-c", action="store_true", help="Show context")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    
    args = parser.parse_args()
    
    results = search_sessions(
        args.query,
        limit=args.limit,
        user_only=args.user_only,
        assistant_only=args.assistant_only,
        questions_only=args.questions,
        days=args.days,
        show_context=args.context
    )
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print(format_results(results, args.context))

if __name__ == "__main__":
    main()
