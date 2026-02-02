#!/usr/bin/env python3
"""
Skin in the Game Tracker
========================

Talebian principle: Follow people with skin in the game.
Tracks insider buying for a watchlist and alerts on significant activity.

Usage:
    python3 insider_tracker.py                    # Check all watchlist
    python3 insider_tracker.py --symbol NVDA      # Check single stock
    python3 insider_tracker.py --alert            # Send Telegram alert if signals found

Signals:
    1. Large buy: Insider buys >$100K
    2. Cluster buying: 3+ insiders buying same stock in 30 days
    3. C-suite buying: CEO/CFO/COO personally buying
    4. Buying into weakness: Insider buys when stock down >10% in month
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configuration
WATCHLIST = [
    "NVDA",   # NVIDIA - AI/GPU leader
    "AMD",    # AMD - GPU competitor
    "SMCI",   # Super Micro - AI servers
    "TSM",    # TSMC - chip foundry
    "MSFT",   # Microsoft - AI/cloud
    "GOOGL",  # Google - AI/cloud
    "META",   # Meta - AI/social
    "AMZN",   # Amazon - AI/cloud
    "AVGO",   # Broadcom - AI networking
    "MRVL",   # Marvell - AI chips
    "ASML",   # ASML - chip equipment
    "AMAT",   # Applied Materials - chip equipment
    "MU",     # Micron - memory
    "INTC",   # Intel - turnaround play
    "QCOM",   # Qualcomm - edge AI
]

# Thresholds
MIN_PURCHASE_VALUE = 100_000  # $100K minimum for "large buy"
CLUSTER_THRESHOLD = 3         # 3+ insiders = cluster
LOOKBACK_DAYS = 30            # Look back 30 days

# C-suite titles that matter most
CSUITE_TITLES = [
    "ceo", "chief executive", 
    "cfo", "chief financial",
    "coo", "chief operating",
    "president",
    "chairman",
]


def get_api_key() -> str:
    """Load FMP API key"""
    key = os.environ.get('FMP_API_KEY')
    if key:
        return key
    
    env_paths = [
        Path.home() / '.openclaw/workspace/.secure/fmp.env',
        Path('.secure/fmp.env'),
    ]
    
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith('FMP_API_KEY='):
                        return line.split('=', 1)[1].strip()
    
    raise ValueError("FMP_API_KEY not found. Set env var or create .secure/fmp.env")


def fetch_insider_trades_sec(symbol: str) -> List[Dict]:
    """Fetch insider trades from SEC EDGAR EFTS search API"""
    import xml.etree.ElementTree as ET
    import time
    
    # SEC requires a proper User-Agent with contact info
    headers = {"User-Agent": "Alyosha-InsiderTracker/1.0 (contact: research@openclaw.ai)"}
    
    # Calculate date range (last 60 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    
    # Search SEC EFTS for Form 4 filings
    import urllib.parse
    query = urllib.parse.quote(f'"{symbol}"')
    search_url = f'https://efts.sec.gov/LATEST/search-index?q={query}&dateRange=custom&startdt={start_date}&enddt={end_date}&forms=4'
    
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            search_data = json.loads(response.read().decode())
        
        trades = []
        hits = search_data.get("hits", {}).get("hits", [])
        
        for hit in hits[:15]:  # Process up to 15 filings
            source = hit.get("_source", {})
            adsh = source.get("adsh", "").replace("-", "")
            ciks = source.get("ciks", [])
            display_names = source.get("display_names", [])
            filing_date = source.get("file_date", "")
            
            if not adsh or not ciks:
                continue
            
            # Get the primary CIK (company) and secondary (insider)
            company_cik = None
            insider_name = "Unknown"
            for i, name in enumerate(display_names):
                if symbol.upper() in name.upper():
                    company_cik = ciks[i] if i < len(ciks) else None
                else:
                    insider_name = name.split("(CIK")[0].strip() if "(CIK" in name else name
            
            if not company_cik:
                company_cik = ciks[0] if ciks else None
            
            # Construct URL to the XML filing
            # Use the reporting person's CIK (first one) for the filing path
            filer_cik = ciks[0].lstrip("0") if ciks else ""
            adsh_nodash = adsh.replace("-", "")  # Remove dashes for URL
            file_id = hit.get("_id", "").split(":")[-1] if ":" in hit.get("_id", "") else ""
            
            if not file_id:
                continue
                
            xml_url = f"https://www.sec.gov/Archives/edgar/data/{filer_cik}/{adsh_nodash}/{file_id}"
            
            try:
                time.sleep(0.2)  # Rate limit
                req2 = urllib.request.Request(xml_url, headers=headers)
                with urllib.request.urlopen(req2, timeout=10) as resp2:
                    xml_content = resp2.read().decode()
                
                # Parse Form 4 XML
                root = ET.fromstring(xml_content)
                
                # Get relationship/title
                title_elem = root.find('.//reportingOwner/reportingOwnerRelationship/officerTitle')
                title = title_elem.text if title_elem is not None else ""
                
                # Get non-derivative transactions (actual stock trades)
                for tx in root.findall('.//nonDerivativeTransaction'):
                    tx_date = tx.find('.//transactionDate/value')
                    tx_code = tx.find('.//transactionCoding/transactionCode')
                    shares = tx.find('.//transactionAmounts/transactionShares/value')
                    price = tx.find('.//transactionAmounts/transactionPricePerShare/value')
                    acq_disp = tx.find('.//transactionAmounts/transactionAcquiredDisposedCode/value')
                    
                    if tx_code is not None:
                        code = tx_code.text
                        ad_code = acq_disp.text if acq_disp is not None else ""
                        
                        # P = Purchase, S = Sale, A = Award, M = Option exercise
                        # Also check A/D code: A = Acquired, D = Disposed
                        is_buy = code == 'P' or (code in ['A', 'M'] and ad_code == 'A')
                        is_sell = code == 'S' or ad_code == 'D'
                        
                        if code in ['P', 'S']:  # Only count direct purchases/sales
                            share_count = float(shares.text) if shares is not None else 0
                            price_val = float(price.text) if price is not None and price.text else 0
                            
                            trade = {
                                "transactionDate": tx_date.text if tx_date is not None else filing_date,
                                "transactionType": "Purchase" if code == 'P' else "Sale",
                                "reportingName": insider_name,
                                "typeOfOwner": title,
                                "securitiesTransacted": share_count,
                                "price": price_val,
                            }
                            trades.append(trade)
                
            except Exception as e:
                continue  # Skip problematic filings
        
        return trades
        
    except Exception as e:
        print(f"Error fetching SEC data for {symbol}: {e}", file=sys.stderr)
        return []


def fetch_insider_trades(symbol: str, api_key: str) -> List[Dict]:
    """Fetch insider trades - try SEC EDGAR (free) first"""
    trades = fetch_insider_trades_sec(symbol)
    if trades:
        return trades
    
    # Fallback to FMP if SEC fails and we have a key
    if api_key:
        url = f"https://financialmodelingprep.com/stable/insider-trading?symbol={symbol}&apikey={api_key}"
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                return data if isinstance(data, list) else []
        except:
            pass
    
    return []


def fetch_stock_price(symbol: str, api_key: str) -> Optional[Dict]:
    """Fetch current stock quote"""
    url = f"https://financialmodelingprep.com/stable/quote/{symbol}?apikey={api_key}"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data[0] if data else None
    except:
        return None


def is_csuite(title: str) -> bool:
    """Check if title is C-suite"""
    if not title:
        return False
    title_lower = title.lower()
    return any(t in title_lower for t in CSUITE_TITLES)


def analyze_trades(trades: List[Dict], symbol: str) -> Dict[str, Any]:
    """Analyze trades for signals"""
    cutoff = datetime.now() - timedelta(days=LOOKBACK_DAYS)
    
    signals = {
        "symbol": symbol,
        "large_buys": [],
        "csuite_buys": [],
        "total_buy_value": 0,
        "total_sell_value": 0,
        "unique_buyers": set(),
        "unique_sellers": set(),
    }
    
    for trade in trades:
        # Parse date
        try:
            trade_date = datetime.strptime(trade.get("transactionDate", ""), "%Y-%m-%d")
        except:
            continue
        
        if trade_date < cutoff:
            continue
        
        # Get transaction details
        tx_type = trade.get("transactionType", "").lower()
        shares = trade.get("securitiesTransacted", 0) or 0
        price = trade.get("price", 0) or 0
        value = shares * price
        insider_name = trade.get("reportingName", "Unknown")
        title = trade.get("typeOfOwner", "")
        
        # Track buys vs sells
        if "purchase" in tx_type or "buy" in tx_type or tx_type == "p":
            signals["total_buy_value"] += value
            signals["unique_buyers"].add(insider_name)
            
            # Large buy signal
            if value >= MIN_PURCHASE_VALUE:
                signals["large_buys"].append({
                    "name": insider_name,
                    "title": title,
                    "value": value,
                    "shares": shares,
                    "price": price,
                    "date": trade.get("transactionDate"),
                })
            
            # C-suite buy signal
            if is_csuite(title):
                signals["csuite_buys"].append({
                    "name": insider_name,
                    "title": title,
                    "value": value,
                    "date": trade.get("transactionDate"),
                })
        
        elif "sale" in tx_type or "sell" in tx_type or tx_type == "s":
            signals["total_sell_value"] += value
            signals["unique_sellers"].add(insider_name)
    
    # Convert sets to counts
    signals["buyer_count"] = len(signals["unique_buyers"])
    signals["seller_count"] = len(signals["unique_sellers"])
    signals["cluster_buying"] = signals["buyer_count"] >= CLUSTER_THRESHOLD
    del signals["unique_buyers"]
    del signals["unique_sellers"]
    
    return signals


def format_currency(value: float) -> str:
    """Format large numbers nicely"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}"


def generate_report(all_signals: List[Dict]) -> str:
    """Generate human-readable report"""
    lines = ["🎯 **Skin in the Game Report**", f"*{datetime.now().strftime('%Y-%m-%d')}*", ""]
    
    # Find notable signals
    notable = []
    
    for sig in all_signals:
        score = 0
        reasons = []
        
        if sig["large_buys"]:
            score += 2
            total = sum(b["value"] for b in sig["large_buys"])
            reasons.append(f"Large buys: {format_currency(total)}")
        
        if sig["csuite_buys"]:
            score += 3
            reasons.append(f"C-suite buying ({len(sig['csuite_buys'])})")
        
        if sig["cluster_buying"]:
            score += 2
            reasons.append(f"Cluster: {sig['buyer_count']} buyers")
        
        if sig["total_buy_value"] > sig["total_sell_value"] * 2:
            score += 1
            reasons.append("Buy/sell ratio >2x")
        
        if score > 0:
            notable.append({
                "symbol": sig["symbol"],
                "score": score,
                "reasons": reasons,
                "details": sig,
            })
    
    # Sort by conviction score
    notable.sort(key=lambda x: x["score"], reverse=True)
    
    if not notable:
        lines.append("No significant insider buying signals in watchlist.")
        lines.append("")
        lines.append(f"Scanned: {', '.join(WATCHLIST)}")
        return "\n".join(lines)
    
    lines.append("**Signals Found:**")
    lines.append("")
    
    for item in notable[:5]:  # Top 5
        sym = item["symbol"]
        score = item["score"]
        stars = "🔥" * min(score, 5)
        
        lines.append(f"**{sym}** {stars}")
        for reason in item["reasons"]:
            lines.append(f"  • {reason}")
        
        # Show top large buy detail
        if item["details"]["large_buys"]:
            top_buy = max(item["details"]["large_buys"], key=lambda x: x["value"])
            lines.append(f"  → {top_buy['name']} bought {format_currency(top_buy['value'])} on {top_buy['date']}")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Skin in the Game Tracker")
    parser.add_argument("--symbol", "-s", help="Check single symbol")
    parser.add_argument("--alert", "-a", action="store_true", help="Send Telegram alert")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON")
    args = parser.parse_args()
    
    # API key optional now - SEC EDGAR is primary source
    try:
        api_key = get_api_key()
    except:
        api_key = None
    
    # Determine symbols to check
    symbols = [args.symbol.upper()] if args.symbol else WATCHLIST
    
    print(f"Scanning {len(symbols)} symbols...", file=sys.stderr)
    
    all_signals = []
    for symbol in symbols:
        trades = fetch_insider_trades(symbol, api_key)
        if trades:
            signals = analyze_trades(trades, symbol)
            all_signals.append(signals)
            
            # Progress indicator
            buy_count = signals["buyer_count"]
            if buy_count > 0:
                print(f"  {symbol}: {buy_count} buyers", file=sys.stderr)
    
    if args.json:
        print(json.dumps(all_signals, indent=2, default=str))
    else:
        report = generate_report(all_signals)
        print(report)
    
    # Return exit code based on signals found
    has_signals = any(
        s["large_buys"] or s["csuite_buys"] or s["cluster_buying"]
        for s in all_signals
    )
    
    return 0 if has_signals else 1


if __name__ == "__main__":
    sys.exit(main())
