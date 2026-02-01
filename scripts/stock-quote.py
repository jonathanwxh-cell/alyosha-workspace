#!/usr/bin/env python3
"""
Quick stock quote using yfinance (no API key needed).
Usage: python3 stock-quote.py NVDA AAPL MSFT
"""

import sys
import json
import yfinance as yf

def get_quote(ticker: str) -> dict:
    """Get basic quote data for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker.upper(),
            "name": info.get("shortName", "N/A"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "change": info.get("regularMarketChange"),
            "changePercent": info.get("regularMarketChangePercent"),
            "marketCap": info.get("marketCap"),
            "peRatio": info.get("trailingPE"),
            "52wHigh": info.get("fiftyTwoWeekHigh"),
            "52wLow": info.get("fiftyTwoWeekLow"),
            "volume": info.get("volume"),
            "avgVolume": info.get("averageVolume"),
        }
    except Exception as e:
        return {"ticker": ticker.upper(), "error": str(e)}

def format_quote(q: dict) -> str:
    """Format quote for display."""
    if "error" in q:
        return f"{q['ticker']}: Error - {q['error']}"
    
    price = q.get('price')
    if price is None:
        return f"{q['ticker']}: No price data"
    
    change = q.get('change', 0) or 0
    change_pct = q.get('changePercent', 0) or 0
    sign = "+" if change >= 0 else ""
    
    mcap = q.get('marketCap', 0) or 0
    if mcap >= 1e12:
        mcap_str = f"${mcap/1e12:.2f}T"
    elif mcap >= 1e9:
        mcap_str = f"${mcap/1e9:.1f}B"
    else:
        mcap_str = f"${mcap/1e6:.0f}M"
    
    pe = q.get('peRatio')
    pe_str = f"P/E: {pe:.1f}" if pe else "P/E: N/A"
    
    return f"{q['ticker']} ({q.get('name', 'N/A')}): ${price:.2f} ({sign}{change:.2f}, {sign}{change_pct:.2f}%) | {mcap_str} | {pe_str}"

if __name__ == "__main__":
    tickers = sys.argv[1:] if len(sys.argv) > 1 else ["NVDA"]
    
    for ticker in tickers:
        quote = get_quote(ticker)
        print(format_quote(quote))
