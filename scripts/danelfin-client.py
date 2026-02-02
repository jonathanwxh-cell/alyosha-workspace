#!/usr/bin/env python3
"""
Danelfin API Client
===================

Python client for Danelfin AI Stock Scores.

Setup:
    export DANELFIN_API_KEY=your_key_here
    # OR create .secure/danelfin.env with: DANELFIN_API_KEY=your_key

Usage:
    python3 danelfin-client.py score NVDA
    python3 danelfin-client.py score NVDA --date 2024-01-15
    python3 danelfin-client.py top --aiscore-min 9
    python3 danelfin-client.py sectors
    python3 danelfin-client.py watchlist NVDA,AAPL,MSFT

API Docs: https://danelfin.com/docs/api
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime

BASE_URL = "https://apirest.danelfin.com"
API_KEY = None

def get_api_key() -> str:
    """Load Danelfin API key from environment or .secure/danelfin.env"""
    key = os.environ.get('DANELFIN_API_KEY')
    if key:
        return key
    
    env_paths = [
        Path.home() / '.secure/danelfin.env',
        Path('.secure/danelfin.env'),
        Path('danelfin.env'),
    ]
    
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith('DANELFIN_API_KEY='):
                        return line.split('=', 1)[1].strip()
    
    raise ValueError(
        "DANELFIN_API_KEY not found.\n"
        "Set it via: export DANELFIN_API_KEY=your_key\n"
        "Or create: .secure/danelfin.env with DANELFIN_API_KEY=your_key"
    )

def init():
    """Initialize client with API key"""
    global API_KEY
    API_KEY = get_api_key()

def _request(endpoint: str, params: dict = None) -> Any:
    """Make API request with authentication"""
    if API_KEY is None:
        init()
    
    # Build query string
    params = params or {}
    query = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
    url = f"{BASE_URL}/{endpoint}"
    if query:
        url = f"{url}?{query}"
    
    # Create request with API key header
    req = urllib.request.Request(url)
    req.add_header('x-api-key', API_KEY)
    req.add_header('Accept', 'application/json')
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": body}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Core Functions
# ============================================================

def get_score(ticker: str, date: str = None) -> Dict:
    """
    Get AI scores for a specific ticker.
    
    Args:
        ticker: Stock symbol (e.g., NVDA)
        date: Optional date in YYYY-MM-DD format
    
    Returns:
        Dict with aiscore, fundamental, technical, sentiment, low_risk
    """
    params = {'ticker': ticker.upper()}
    if date:
        params['date'] = date
    return _request('ranking', params)

def get_top_stocks(
    aiscore_min: int = None,
    fundamental_min: int = None,
    technical_min: int = None,
    sentiment_min: int = None,
    low_risk_min: int = None,
    sector: str = None,
    industry: str = None,
    asset: str = 'stock',
    date: str = None
) -> Dict:
    """
    Get top-ranked stocks with optional filters.
    
    Args:
        aiscore_min: Minimum AI score (1-10)
        fundamental_min: Minimum fundamental score
        technical_min: Minimum technical score
        sentiment_min: Minimum sentiment score
        low_risk_min: Minimum low risk score
        sector: Sector slug (e.g., 'information-technology')
        industry: Industry slug
        asset: 'stock' or 'etf'
        date: Date in YYYY-MM-DD (defaults to today)
    
    Returns:
        Dict of tickers with their scores
    """
    params = {
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'asset': asset,
    }
    
    if aiscore_min:
        params['aiscore_min'] = aiscore_min
    if fundamental_min:
        params['fundamental_min'] = fundamental_min
    if technical_min:
        params['technical_min'] = technical_min
    if sentiment_min:
        params['sentiment_min'] = sentiment_min
    if low_risk_min:
        params['low_risk_min'] = low_risk_min
    if sector:
        params['sector'] = sector
    if industry:
        params['industry'] = industry
    
    return _request('ranking', params)

def get_sectors() -> List[Dict]:
    """Get list of all sectors with their slugs."""
    return _request('sectors')

def get_sector_scores(sector_slug: str) -> Dict:
    """
    Get historical scores for a sector.
    
    Args:
        sector_slug: e.g., 'information-technology', 'energy'
    """
    return _request(f'sectors/{sector_slug}')

def get_industries() -> List[Dict]:
    """Get list of all industries with their slugs."""
    return _request('industries')

# ============================================================
# Composite Functions
# ============================================================

def watchlist_scores(tickers: List[str], date: str = None) -> str:
    """
    Generate a formatted score summary for a watchlist.
    
    Args:
        tickers: List of stock symbols
        date: Optional date
    
    Returns:
        Formatted string for display/Telegram
    """
    lines = ["📊 **Danelfin AI Scores**\n"]
    
    for ticker in tickers:
        result = get_score(ticker.upper(), date)
        
        if 'error' in result:
            lines.append(f"❌ **{ticker}**: {result.get('error', 'Unknown error')}")
            continue
        
        # Find the score data (could be nested by date)
        scores = None
        if isinstance(result, dict):
            # Try direct access or find first date key
            for key, value in result.items():
                if isinstance(value, dict) and 'aiscore' in value:
                    scores = value
                    break
        
        if not scores:
            lines.append(f"❓ **{ticker}**: No score data")
            continue
        
        ai = scores.get('aiscore', '?')
        fund = scores.get('fundamental', '?')
        tech = scores.get('technical', '?')
        sent = scores.get('sentiment', '?')
        risk = scores.get('low_risk', '?')
        
        # Color code AI score
        if isinstance(ai, int):
            if ai >= 8:
                emoji = "🟢"
            elif ai >= 5:
                emoji = "🟡"
            else:
                emoji = "🔴"
        else:
            emoji = "⚪"
        
        lines.append(
            f"{emoji} **{ticker}**: AI={ai} | F={fund} T={tech} S={sent} R={risk}"
        )
    
    return '\n'.join(lines)

def top_picks_summary(min_score: int = 9) -> str:
    """
    Get today's top AI-scored stocks.
    
    Args:
        min_score: Minimum AI score threshold
    
    Returns:
        Formatted summary
    """
    result = get_top_stocks(aiscore_min=min_score)
    
    if 'error' in result:
        return f"Error: {result.get('error')}"
    
    lines = [f"🏆 **Top Picks (AI Score ≥ {min_score})**\n"]
    
    # Result format varies based on query
    count = 0
    for key, value in result.items():
        if isinstance(value, dict):
            # Could be date -> {ticker -> scores} or ticker -> scores
            for ticker, scores in (value.items() if 'aiscore' not in value else [(key, value)]):
                if not isinstance(scores, dict):
                    continue
                ai = scores.get('aiscore', 0)
                if isinstance(ai, int) and ai >= min_score:
                    fund = scores.get('fundamental', '?')
                    tech = scores.get('technical', '?')
                    lines.append(f"  • **{ticker}**: AI={ai} F={fund} T={tech}")
                    count += 1
                    if count >= 20:
                        break
        if count >= 20:
            break
    
    if count == 0:
        lines.append("  No stocks found matching criteria")
    
    return '\n'.join(lines)

# ============================================================
# CLI Interface
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    try:
        init()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nTo use this client, you need a Danelfin API key.")
        print("Get one at: https://danelfin.com/pricing/api")
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if cmd == 'score' and args:
        ticker = args[0]
        date = None
        if '--date' in args:
            idx = args.index('--date')
            if idx + 1 < len(args):
                date = args[idx + 1]
        
        result = get_score(ticker, date)
        print(json.dumps(result, indent=2))
    
    elif cmd == 'top':
        min_score = 9
        if '--aiscore-min' in args:
            idx = args.index('--aiscore-min')
            if idx + 1 < len(args):
                min_score = int(args[idx + 1])
        
        print(top_picks_summary(min_score))
    
    elif cmd == 'watchlist' and args:
        tickers = args[0].split(',')
        print(watchlist_scores(tickers))
    
    elif cmd == 'sectors':
        result = get_sectors()
        print("Available sectors:")
        if isinstance(result, list):
            for s in result:
                print(f"  • {s.get('sector', s)}")
        else:
            print(json.dumps(result, indent=2))
    
    elif cmd == 'industries':
        result = get_industries()
        print("Available industries:")
        if isinstance(result, list):
            for i in result[:30]:  # Limit output
                print(f"  • {i.get('industry', i)}")
            if len(result) > 30:
                print(f"  ... and {len(result) - 30} more")
        else:
            print(json.dumps(result, indent=2))
    
    elif cmd == 'sector-scores' and args:
        result = get_sector_scores(args[0])
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
