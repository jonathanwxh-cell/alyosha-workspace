#!/usr/bin/env python3
"""
Financial Modeling Prep (FMP) API Client
=========================================

A Python client for the FMP API with useful market intelligence functions.
Supports Ultimate tier features including earnings transcripts.

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
    python3 fmp-client.py transcript NVDA 2024 Q4
    python3 fmp-client.py earnings NVDA
    python3 fmp-client.py news NVDA
    python3 fmp-client.py calendar --days 7

API Docs: https://site.financialmodelingprep.com/developer/docs
"""

import os
import sys
import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timedelta

# Load API key
def get_api_key() -> str:
    """Load FMP API key from environment or .secure/fmp.env"""
    key = os.environ.get('FMP_API_KEY')
    if key:
        return key
    
    env_paths = [
        Path.home() / '.secure/fmp.env',
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
V3_URL = "https://financialmodelingprep.com/api/v3"
V4_URL = "https://financialmodelingprep.com/api/v4"
API_KEY = None

def init():
    """Initialize the client with API key"""
    global API_KEY
    API_KEY = get_api_key()

def _request(endpoint: str, params: dict = None, base: str = None) -> Any:
    """Make API request"""
    if API_KEY is None:
        init()
    
    base = base or BASE_URL
    params = params or {}
    params['apikey'] = API_KEY
    
    query = '&'.join(f"{k}={v}" for k, v in params.items())
    url = f"{base}/{endpoint}?{query}"
    
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {e.reason}", "detail": body}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Core Functions
# ============================================================

def quote(symbols: List[str]) -> List[Dict]:
    """Get real-time quotes for multiple symbols."""
    results = []
    for symbol in symbols:
        result = _request('quote', {'symbol': symbol})
        if result and isinstance(result, list):
            results.extend(result)
        elif result and isinstance(result, dict) and 'error' not in result:
            results.append(result)
    return results

def profile(symbol: str) -> Dict:
    """Get company profile with detailed info."""
    result = _request('profile', {'symbol': symbol})
    return result[0] if result and isinstance(result, list) else result

def key_metrics(symbol: str, limit: int = 4) -> List[Dict]:
    """Get key financial metrics (P/E, EV/EBITDA, etc.)"""
    return _request('key-metrics', {'symbol': symbol, 'limit': limit})

def ratios(symbol: str, limit: int = 4) -> List[Dict]:
    """Get financial ratios (ROE, debt ratios, etc.)"""
    return _request('ratios', {'symbol': symbol, 'limit': limit})

def search(query: str, limit: int = 10) -> List[Dict]:
    """Search for companies by name or ticker."""
    return _request('search-name', {'query': query, 'limit': limit})

def gainers() -> List[Dict]:
    """Get top gainers of the day."""
    return _request('biggest-gainers')

def losers() -> List[Dict]:
    """Get top losers of the day."""
    return _request('biggest-losers')

def most_active() -> List[Dict]:
    """Get most actively traded stocks."""
    return _request('actives')

def sector_performance() -> List[Dict]:
    """Get sector performance data."""
    return _request('sector-performance')

# ============================================================
# Earnings & Transcripts (Stable API)
# ============================================================

def earnings_calendar(from_date: str = None, to_date: str = None) -> List[Dict]:
    """
    Get earnings calendar.
    
    Args:
        from_date: Start date YYYY-MM-DD (defaults to today)
        to_date: End date YYYY-MM-DD (defaults to 7 days from now)
    """
    if not from_date:
        from_date = datetime.now().strftime('%Y-%m-%d')
    if not to_date:
        to_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    return _request('earning-calendar', {'from': from_date, 'to': to_date})

def earnings_historical(symbol: str) -> List[Dict]:
    """Get historical earnings for a symbol."""
    return _request('historical-earning-calendar', {'symbol': symbol})

def earnings_transcript(symbol: str, year: int, quarter: int) -> Dict:
    """
    Get earnings call transcript (Ultimate tier).
    
    Args:
        symbol: Stock symbol
        year: Fiscal year (calendar year)
        quarter: Quarter (1-4)
    
    Returns:
        Dict with 'content' containing full transcript text
    """
    result = _request('earnings-transcript', {'symbol': symbol, 'year': year, 'quarter': quarter})
    if result and isinstance(result, list) and len(result) > 0:
        return result[0]
    return result

def earnings_transcripts_list() -> List[Dict]:
    """Get list of all companies with available transcripts."""
    return _request('earnings-transcript-list')

# ============================================================
# News (Stable API)
# ============================================================

def stock_news(symbols: str = None, limit: int = 20) -> List[Dict]:
    """
    Get stock news.
    
    Args:
        symbols: Comma-separated tickers (optional)
        limit: Number of articles
    """
    params = {'limit': limit}
    if symbols:
        params['symbols'] = symbols.upper()
    return _request('company-news', params)

def general_news(limit: int = 20) -> List[Dict]:
    """Get general financial news."""
    return _request('general-news', {'limit': limit})

def press_releases(symbol: str, limit: int = 10) -> List[Dict]:
    """Get press releases for a symbol."""
    return _request('press-releases', {'symbol': symbol, 'limit': limit})

# ============================================================
# Institutional Data (Stable API)
# ============================================================

def institutional_holders(symbol: str) -> List[Dict]:
    """Get institutional holders for a symbol."""
    return _request('institutional-holder', {'symbol': symbol})

def insider_trading(symbol: str, limit: int = 20) -> List[Dict]:
    """Get insider trading activity."""
    return _request('insider-trades', {'symbol': symbol, 'limit': limit})

def stock_peers(symbol: str) -> List[Dict]:
    """Get peer companies for comparison."""
    return _request('stock-peers', {'symbol': symbol})

# ============================================================
# Composite Functions (for market intel)
# ============================================================

def watchlist_summary(symbols: List[str]) -> str:
    """Generate a summary for a watchlist of symbols."""
    quotes = quote(symbols)
    if not quotes or 'error' in quotes:
        return f"Error fetching quotes: {quotes}"
    
    lines = ["📊 **Watchlist Summary**\n"]
    
    for q in quotes:
        symbol = q.get('symbol', '?')
        price = q.get('price', 0)
        change_pct = q.get('changePercentage', 0)
        
        if change_pct > 0:
            emoji = "🟢"
            sign = "+"
        elif change_pct < 0:
            emoji = "🔴"
            sign = ""
        else:
            emoji = "⚪"
            sign = ""
        
        lines.append(f"{emoji} **{symbol}**: ${price:.2f} ({sign}{change_pct:.2f}%)")
    
    return '\n'.join(lines)

def market_movers_summary() -> str:
    """Generate a summary of market movers."""
    lines = ["📈 **Market Movers**\n"]
    
    g = gainers()
    if g and not isinstance(g, dict):
        lines.append("**Top Gainers:**")
        for stock in g[:5]:
            lines.append(f"  🟢 {stock.get('symbol')}: +{stock.get('changePercentage', 0):.2f}%")
    
    l = losers()
    if l and not isinstance(l, dict):
        lines.append("\n**Top Losers:**")
        for stock in l[:5]:
            lines.append(f"  🔴 {stock.get('symbol')}: {stock.get('changePercentage', 0):.2f}%")
    
    return '\n'.join(lines)

def company_snapshot(symbol: str) -> str:
    """Generate a comprehensive snapshot for a single company."""
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

def upcoming_earnings_summary(symbols: str = None, days: int = 14) -> str:
    """Get upcoming earnings for watchlist or all."""
    from_date = datetime.now().strftime('%Y-%m-%d')
    to_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
    
    earnings = earnings_calendar(from_date, to_date)
    
    if not earnings or 'error' in earnings:
        return f"Error: {earnings}"
    
    # Filter to symbols if provided
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        earnings = [e for e in earnings if e.get('symbol') in symbol_list]
    
    if not earnings:
        return "No upcoming earnings found"
    
    lines = [f"📅 **Upcoming Earnings** (next {days} days)\n"]
    
    # Sort by date
    earnings.sort(key=lambda x: x.get('date', ''))
    
    for e in earnings[:20]:
        symbol = e.get('symbol', '?')
        date = e.get('date', '')[:10]
        time = e.get('time', '')
        eps_est = e.get('epsEstimated', '?')
        
        time_str = f" ({time})" if time else ""
        lines.append(f"• **{symbol}** — {date}{time_str} | EPS Est: ${eps_est}")
    
    return '\n'.join(lines)

def news_summary(tickers: str, limit: int = 10) -> str:
    """Get formatted news summary."""
    news = stock_news(tickers, limit)
    
    if not news or 'error' in news:
        return f"Error: {news}"
    
    lines = [f"📰 **News: {tickers}**\n"]
    
    for article in news[:limit]:
        title = article.get('title', 'No title')[:70]
        date = article.get('publishedDate', '')[:10]
        site = article.get('site', '?')
        lines.append(f"• [{date}] {title}... ({site})")
    
    return '\n'.join(lines)

def transcript_summary(symbol: str, year: int, quarter: int, max_chars: int = 3000) -> str:
    """Get earnings transcript with summary."""
    t = earnings_transcript(symbol, year, quarter)
    
    if not t or 'error' in t:
        return f"Error fetching transcript: {t}"
    
    content = t.get('content', '')
    if not content:
        return f"No transcript found for {symbol} {year} Q{quarter}"
    
    # Truncate for display
    if len(content) > max_chars:
        content = content[:max_chars] + "...\n\n[Truncated - full transcript available]"
    
    lines = [
        f"📞 **{symbol} Earnings Call — {year} Q{quarter}**",
        f"Date: {t.get('date', '?')}",
        "",
        content
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
        if isinstance(result, list) and result:
            for r in result[:10]:
                print(f"{r.get('symbol', '?')}: {r.get('name', '?')} ({r.get('exchangeShortName', '?')})")
        else:
            print("No results found")
    
    elif cmd == 'gainers':
        result = gainers()
        print("Top Gainers:")
        if isinstance(result, list) and result:
            for g in result[:10]:
                pct = g.get('changesPercentage') or g.get('changePercentage', 0)
                print(f"  {g.get('symbol')}: +{pct:.2f}% (${g.get('price', 0):.2f})")
        else:
            print("  No data available")
    
    elif cmd == 'losers':
        result = losers()
        print("Top Losers:")
        if isinstance(result, list) and result:
            for l in result[:10]:
                pct = l.get('changesPercentage') or l.get('changePercentage', 0)
                print(f"  {l.get('symbol')}: {pct:.2f}% (${l.get('price', 0):.2f})")
        else:
            print("  No data available")
    
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
    
    elif cmd == 'transcript' and len(args) >= 3:
        symbol = args[0].upper()
        year = int(args[1])
        quarter = int(args[2].replace('Q', '').replace('q', ''))
        print(transcript_summary(symbol, year, quarter))
    
    elif cmd == 'transcripts' and args:
        result = earnings_transcripts_available(args[0].upper())
        print(f"Available transcripts for {args[0].upper()}:")
        if isinstance(result, list):
            for t in result[:20]:
                print(f"  {t.get('year', '?')} Q{t.get('quarter', '?')} — {t.get('date', '?')}")
        else:
            print(json.dumps(result, indent=2))
    
    elif cmd == 'earnings' and args:
        print(upcoming_earnings_summary(args[0]))
    
    elif cmd == 'calendar':
        days = 7
        if '--days' in args:
            idx = args.index('--days')
            if idx + 1 < len(args):
                days = int(args[idx + 1])
        print(upcoming_earnings_summary(days=days))
    
    elif cmd == 'news':
        tickers = args[0] if args else None
        print(news_summary(tickers))
    
    elif cmd == 'insiders' and args:
        result = insider_trading(args[0].upper())
        print(f"Insider Trading — {args[0].upper()}:")
        if isinstance(result, list):
            for t in result[:15]:
                name = t.get('reportingName', '?')
                trans = t.get('transactionType', '?')
                shares = t.get('securitiesTransacted', 0)
                date = t.get('transactionDate', '')[:10]
                print(f"  [{date}] {name}: {trans} {shares:,} shares")
        else:
            print(json.dumps(result, indent=2))
    
    elif cmd == 'holders' and args:
        result = institutional_holders(args[0].upper())
        print(f"Top Institutional Holders — {args[0].upper()}:")
        if isinstance(result, list):
            for h in result[:15]:
                name = h.get('holder', '?')[:30]
                shares = h.get('shares', 0)
                pct = h.get('weight', 0) * 100
                print(f"  {name}: {shares:,} shares ({pct:.2f}%)")
        else:
            print(json.dumps(result, indent=2))
    
    elif cmd == 'test':
        # Quick API test
        result = quote(['AAPL'])
        if result and not any('error' in str(r) for r in result):
            print("✅ FMP API key is valid!")
            print(f"   AAPL: ${result[0].get('price', 0):.2f}")
        else:
            print(f"❌ API test failed: {result}")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)

if __name__ == '__main__':
    main()
