#!/usr/bin/env python3
"""
Fragility Signals Tracker
Tracks early warning signs of market stress/fragility
Based on Talebian principles
"""

import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import os

# FRED API (free, get key at https://fred.stlouisfed.org/docs/api/api_key.html)
FRED_KEY = os.getenv("FRED_API_KEY", "")

def get_vix_vvix():
    """VIX and VVIX - volatility of volatility"""
    try:
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="5d")
        
        # VVIX not directly on Yahoo, use proxy or calculate
        vvix = yf.Ticker("^VVIX")
        vvix_data = vvix.history(period="5d")
        
        return {
            "vix": {
                "current": round(vix_data['Close'].iloc[-1], 2) if len(vix_data) > 0 else None,
                "5d_ago": round(vix_data['Close'].iloc[0], 2) if len(vix_data) > 0 else None,
                "change_pct": round((vix_data['Close'].iloc[-1] / vix_data['Close'].iloc[0] - 1) * 100, 1) if len(vix_data) > 0 else None,
            },
            "vvix": {
                "current": round(vvix_data['Close'].iloc[-1], 2) if len(vvix_data) > 0 else None,
                "5d_ago": round(vvix_data['Close'].iloc[0], 2) if len(vvix_data) > 0 else None,
                "change_pct": round((vvix_data['Close'].iloc[-1] / vvix_data['Close'].iloc[0] - 1) * 100, 1) if len(vvix_data) > 0 else None,
            },
            "signal": "⚠️ ELEVATED" if (vvix_data['Close'].iloc[-1] if len(vvix_data) > 0 else 0) > 110 else "✅ Normal"
        }
    except Exception as e:
        return {"error": str(e)}

def get_credit_spreads():
    """High Yield - Investment Grade spread (stress indicator)"""
    try:
        # ICE BofA High Yield spread
        if FRED_KEY:
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&api_key={FRED_KEY}&file_type=json&limit=30&sort_order=desc"
            resp = requests.get(url, timeout=10)
            data = resp.json()
            obs = data.get("observations", [])
            if obs:
                current = float(obs[0]["value"]) if obs[0]["value"] != "." else None
                week_ago = float(obs[5]["value"]) if len(obs) > 5 and obs[5]["value"] != "." else None
                return {
                    "hy_spread": current,
                    "week_ago": week_ago,
                    "change": round(current - week_ago, 2) if current and week_ago else None,
                    "signal": "⚠️ WIDENING" if current and current > 4.0 else "✅ Normal"
                }
        return {"note": "Need FRED API key for credit spreads"}
    except Exception as e:
        return {"error": str(e)}

def get_sp500_concentration():
    """Top 10 concentration in S&P 500 - crowding risk"""
    try:
        # Approximation using top holdings
        top_10 = ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "TSLA", "UNH", "JPM"]
        
        spy = yf.Ticker("SPY")
        spy_price = spy.history(period="1d")['Close'].iloc[-1]
        
        total_weight = 0
        holdings = []
        
        for ticker in top_10[:7]:  # Top 7 for speed
            try:
                t = yf.Ticker(ticker)
                info = t.info
                mkt_cap = info.get("marketCap", 0)
                holdings.append({"ticker": ticker, "mkt_cap": mkt_cap})
            except:
                pass
        
        # S&P 500 total market cap ~45T
        sp500_cap = 45_000_000_000_000
        top7_pct = sum(h["mkt_cap"] for h in holdings) / sp500_cap * 100
        
        return {
            "top7_weight_pct": round(top7_pct, 1),
            "signal": "⚠️ CONCENTRATED" if top7_pct > 30 else "✅ Normal",
            "note": "Top 7 stocks as % of S&P 500"
        }
    except Exception as e:
        return {"error": str(e)}

def get_put_call_ratio():
    """Put/Call ratio - sentiment/hedging indicator"""
    try:
        # CBOE total put/call
        # This would need CBOE data or alternative source
        return {"note": "Need CBOE data source - using VIX as proxy"}
    except Exception as e:
        return {"error": str(e)}

def get_treasury_curve():
    """2Y-10Y spread - inversion = recession signal"""
    try:
        tlt = yf.Ticker("^TNX")  # 10Y
        two_y = yf.Ticker("^IRX")  # 3M (proxy for short end)
        
        tnx = tlt.history(period="5d")['Close'].iloc[-1] if len(tlt.history(period="5d")) > 0 else None
        irx = two_y.history(period="5d")['Close'].iloc[-1] if len(two_y.history(period="5d")) > 0 else None
        
        spread = round(tnx - irx, 2) if tnx and irx else None
        
        return {
            "10y_yield": round(tnx, 2) if tnx else None,
            "3m_yield": round(irx, 2) if irx else None,
            "spread": spread,
            "signal": "⚠️ INVERTED" if spread and spread < 0 else "✅ Normal"
        }
    except Exception as e:
        return {"error": str(e)}

def generate_report():
    """Generate full fragility report"""
    print("Fetching fragility signals...\n")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "signals": {}
    }
    
    print("1. VIX/VVIX...")
    report["signals"]["volatility"] = get_vix_vvix()
    
    print("2. Credit spreads...")
    report["signals"]["credit"] = get_credit_spreads()
    
    print("3. Concentration...")
    report["signals"]["concentration"] = get_sp500_concentration()
    
    print("4. Treasury curve...")
    report["signals"]["curve"] = get_treasury_curve()
    
    return report

def format_report(report):
    """Format report for display"""
    lines = []
    lines.append("=" * 50)
    lines.append("FRAGILITY SIGNALS REPORT")
    lines.append(f"Generated: {report['timestamp'][:19]} UTC")
    lines.append("=" * 50)
    
    # Volatility
    vol = report["signals"].get("volatility", {})
    lines.append(f"\n📊 VOLATILITY {vol.get('signal', '')}")
    lines.append(f"   VIX:  {vol.get('vix', {}).get('current', 'N/A')} ({vol.get('vix', {}).get('change_pct', 'N/A'):+.1f}% 5d)" if vol.get('vix', {}).get('change_pct') else f"   VIX: {vol.get('vix', {}).get('current', 'N/A')}")
    lines.append(f"   VVIX: {vol.get('vvix', {}).get('current', 'N/A')} ({vol.get('vvix', {}).get('change_pct', 'N/A'):+.1f}% 5d)" if vol.get('vvix', {}).get('change_pct') else f"   VVIX: {vol.get('vvix', {}).get('current', 'N/A')}")
    
    # Credit
    credit = report["signals"].get("credit", {})
    lines.append(f"\n💳 CREDIT SPREADS {credit.get('signal', credit.get('note', ''))}")
    if credit.get("hy_spread"):
        lines.append(f"   HY Spread: {credit['hy_spread']:.2f}% (Δ {credit.get('change', 'N/A'):+.2f}% wow)")
    
    # Concentration
    conc = report["signals"].get("concentration", {})
    lines.append(f"\n🎯 CONCENTRATION {conc.get('signal', '')}")
    lines.append(f"   Top 7 weight: {conc.get('top7_weight_pct', 'N/A')}% of S&P 500")
    
    # Curve
    curve = report["signals"].get("curve", {})
    lines.append(f"\n📈 YIELD CURVE {curve.get('signal', '')}")
    lines.append(f"   10Y: {curve.get('10y_yield', 'N/A')}% | 3M: {curve.get('3m_yield', 'N/A')}%")
    lines.append(f"   Spread: {curve.get('spread', 'N/A')}%")
    
    # Summary
    warnings = sum(1 for s in report["signals"].values() if "⚠️" in str(s.get("signal", "")))
    lines.append(f"\n{'=' * 50}")
    lines.append(f"SUMMARY: {warnings}/4 signals elevated")
    if warnings >= 2:
        lines.append("⚠️ Multiple fragility signals - increased caution warranted")
    else:
        lines.append("✅ No systemic stress detected")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "json":
        report = generate_report()
        print(json.dumps(report, indent=2))
    else:
        report = generate_report()
        print(format_report(report))
