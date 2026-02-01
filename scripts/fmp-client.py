#!/usr/bin/env python3
"""
Financial Modeling Prep (FMP) API Client
=========================================

A Python client for the FMP API with useful market intelligence functions.

Setup:
    export FMP_API_KEY=your_key_here
    # OR create .secure/fmp.env with: FMP_API_KEY=your_key

Usage:
    python3 fmp-client.py quote NVDA AAPL MSFT
    python3 fmp-client.py profile NVDA
    python3 fmp-client.py metrics NVDA
    python3 fmp-client.py search nvidia
    python3 fmp-client.py gainers
    python3 fmp-client.py losers
    python3 fmp-client.py watchlist NVDA,AAPL,MSFT,GOOGL

API Docs: https://site.financialmodelingprep.com/developer/docs
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from pathlib import Path

# Load API key
def get_api_key() -> str:
    """Load FMP API key from environment or .secure/fmp.env"""
    key = os.environ.get('FMP_API_KEY')
    if key:
        return key
    
    # Try loading from file
    env_paths = [
        Path.home() / '.openclaw/workspace/.secure/fmp.env',
        Path('.secure/fmp.env'),
        Path('fmp.env'),
    ]
    
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith('FMP_API_KEY='):
                        return line.split('=', 1)[1].strip()
    
    raise ValueError("FMP_API_KEY not found in environment or .secure/fmp.env")

BASE_URL = "https://financialmodelingprep.com/stable"
API_KEY = None

def init():
    """Initialize the client with API key"""
    global API_KEY
    API_KEY = get_api_key()

def _request(endpoint: str, params: dict = None) -> Any:
    """Make API request"""
    if API_KEY is None:
        init()
    
    params = params or {}
    params['apikey'] = API_KEY
    
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE_URL}/{endpoint}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Core Functions
# ============================================================

def quote(symbols: List[str]) -> List[Dict]:
    """
    Get real-time quotes for multiple symbols.
    
    Returns: List of quote dicts with price, change, volume, etc.
    """
    # FMP free tier requires individual requests per symbol
    results = []
    for symbol in symbols:
        result = _request('quote', {'symbol': symbol})
        if result and isinstance(result, list):
            results.extend(result)
        elif result and isinstance(result, dict) and 'error' not in result:
            results.append(result)
    return results

def profile(symbol: str) -> Dict:
    """
    Get company profile with detailed info.
    
    Returns: Company description, sector, CEO, employees, etc.
    """
    result = _request('profile', {'symbol': symbol})
    return result[0] if result and isinstance(result, list) else result

def key_metrics(symbol: str, limit: int = 4) -> List[Dict]:
    """
    Get key financial metrics (P/E, EV/EBITDA, etc.)
    
    Returns: List of quarterly/annual metric snapshots
    """
    return _request('key-metrics', {'symbol': symbol, 'limit': limit})

def ratios(symbol: str, limit: int = 4) -> List[Dict]:
    """
    Get financial ratios (ROE, debt ratios, etc.)
    """
    return _request('ratios', {'symbol': symbol, 'limit': limit})

def search(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for companies by name or ticker.
    """
    return _request('search', {'query': query, 'limit': limit})

def search_ticker(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for ticker symbols.
    """
    return _request('search-ticker', {'query': query, 'limit': limit})

def gainers() -> List[Dict]:
    """Get top gainers of the day."""
    return _request('gainers')

def losers() -> List[Dict]:
    """Get top losers of the day."""
    return _request('losers')

def most_active() -> List[Dict]:
    """Get most actively traded stocks."""
    return _request('actives')

def sector_performance() -> List[Dict]:
    """Get sector performance data."""
    return _request('sector-performance')

# ============================================================
# Composite Functions (for market intel)
# ============================================================

def watchlist_summary(symbols: List[str]) -> str:
    """
    Generate a summary for a watchlist of symbols.
    Useful for daily briefings.
    """
    quotes = quote(symbols)
    if not quotes or 'error' in quotes:
        return f"Error fetching quotes: {quotes}"
    
    lines = ["📊 **Watchlist Summary**\n"]
    
    for q in quotes:
        symbol = q.get('symbol', '?')
        price = q.get('price', 0)
        change = q.get('change', 0)
        change_pct = q.get('changePercentage', 0)
        
        # Emoji based on direction
        if change > 0:
            emoji = "🟢"
            sign = "+"
        elif change < 0:
            emoji = "🔴"
            sign = ""
        else:
            emoji = "⚪"
            sign = ""
        
        lines.append(f"{emoji} **{symbol}**: ${price:.2f} ({sign}{change_pct:.2f}%)")
    
    return '\n'.join(lines)

def market_movers_summary() -> str:
    """
    Generate a summary of market movers.
    """
    lines = ["📈 **Market Movers**\n"]
    
    # Top Gainers
    g = gainers()
    if g and not isinstance(g, dict):
        lines.append("**Top Gainers:**")
        for stock in g[:5]:
            lines.append(f"  🟢 {stock.get('symbol')}: +{stock.get('changePercentage', 0):.2f}%")
    
    # Top Losers
    l = losers()
    if l and not isinstance(l, dict):
        lines.append("\n**Top Losers:**")
        for stock in l[:5]:
            lines.append(f"  🔴 {stock.get('symbol')}: {stock.get('changePercentage', 0):.2f}%")
    
    return '\n'.join(lines)

def company_snapshot(symbol: str) -> str:
    """
    Generate a comprehensive snapshot for a single company.
    """
    p = profile(symbol)
    if not p or 'error' in p:
        return f"Error: {p}"
    
    q = quote([symbol])
    q = q[0] if q else {}
    
    m = key_metrics(symbol, limit=1)
    m = m[0] if m else {}
    
    lines = [
        f"# {p.get('companyName', symbol)} ({symbol})",
        f"**Sector:** {p.get('sector', '?')} | **Industry:** {p.get('industry', '?')}",
        f"**Price:** ${q.get('price', 0):.2f} ({q.get('changePercentage', 0):+.2f}%)",
        f"**Market Cap:** ${p.get('marketCap', 0)/1e9:.1f}B",
        f"**52W Range:** {p.get('range', '?')}",
        "",
        "**Key Metrics:**",
        f"  P/E: {m.get('peRatio', '?')}",
        f"  EV/EBITDA: {m.get('evToEBITDA', '?')}",
        f"  ROE: {m.get('returnOnEquity', '?')}",
        "",
        f"**Description:** {p.get('description', 'N/A')[:300]}...",
    ]
    
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
        return
    
    cmd = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if cmd == 'quote' and args:
        result = quote(args)
        for q in result:
            symbol = q.get('symbol', '?')
            price = q.get('price', 0)
            change = q.get('change', 0)
            change_pct = q.get('changePercentage', 0)
            mcap = q.get('marketCap', 0)
            print(f"{symbol}: ${price:.2f} ({change:+.2f}, {change_pct:+.2f}%) | MCap: ${mcap/1e9:.1f}B")
    
    elif cmd == 'profile' and args:
        p = profile(args[0])
        print(json.dumps(p, indent=2))
    
    elif cmd == 'metrics' and args:
        m = key_metrics(args[0])
        print(json.dumps(m, indent=2))
    
    elif cmd == 'search' and args:
        result = search(' '.join(args))
        for r in result[:10]:
            print(f"{r.get('symbol', '?')}: {r.get('name', '?')} ({r.get('exchangeShortName', '?')})")
    
    elif cmd == 'gainers':
        result = gainers()
        print("Top Gainers:")
        for g in (result or [])[:10]:
            print(f"  {g.get('symbol')}: +{g.get('changePercentage', 0):.2f}% (${g.get('price', 0):.2f})")
    
    elif cmd == 'losers':
        result = losers()
        print("Top Losers:")
        for l in (result or [])[:10]:
            print(f"  {l.get('symbol')}: {l.get('changePercentage', 0):.2f}% (${l.get('price', 0):.2f})")
    
    elif cmd == 'watchlist' and args:
        symbols = args[0].split(',')
        print(watchlist_summary(symbols))
    
    elif cmd == 'movers':
        print(market_movers_summary())
    
    elif cmd == 'snapshot' and args:
        print(company_snapshot(args[0]))
    
    elif cmd == 'sectors':
        result = sector_performance()
        print("Sector Performance:")
        if isinstance(result, list):
            for s in result:
                if isinstance(s, dict):
                    print(f"  {s.get('sector', '?')}: {s.get('changesPercentage', '?')}")
                else:
                    print(f"  {s}")
        else:
            print(f"  Unexpected response: {result}")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
