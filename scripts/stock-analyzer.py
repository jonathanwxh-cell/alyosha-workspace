#!/usr/bin/env python3
"""
Stock Analyzer - Comprehensive Stock Analysis Framework
========================================================

A thorough stock analysis tool using FMP API with fixed framework.
Maximizes FMP API usage for deep fundamental analysis.

Usage:
    python3 stock-analyzer.py NVDA           # Full analysis
    python3 stock-analyzer.py NVDA --quick   # Quick summary only
    python3 stock-analyzer.py NVDA --json    # Output as JSON
    python3 stock-analyzer.py NVDA --save    # Save to file

Framework:
    1. Company Profile
    2. Valuation Metrics
    3. Financial Health
    4. Profitability
    5. Growth Analysis
    6. Quality Indicators
    7. Ownership Signals
    8. Peer Comparison
    9. Recent News
    10. Risk Assessment

"""

import os
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

# =============================================================================
# API Configuration
# =============================================================================

BASE_URL = "https://financialmodelingprep.com/stable"
V3_URL = "https://financialmodelingprep.com/api/v3"
API_KEY = None

def get_api_key() -> str:
    key = os.environ.get('FMP_API_KEY')
    if key:
        return key
    env_paths = [Path.home() / '.secure/fmp.env', Path('.secure/fmp.env')]
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith('FMP_API_KEY='):
                        return line.split('=', 1)[1].strip()
    raise ValueError("FMP_API_KEY not found")

def init():
    global API_KEY
    API_KEY = get_api_key()

def _request(endpoint: str, params: dict = None, base: str = None) -> Any:
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
        return {"error": f"HTTP {e.code}"}
    except Exception as e:
        return {"error": str(e)}

# =============================================================================
# Data Fetchers
# =============================================================================

def fetch_profile(symbol: str) -> Dict:
    result = _request('profile', {'symbol': symbol})
    return result[0] if isinstance(result, list) and result else result

def fetch_quote(symbol: str) -> Dict:
    result = _request('quote', {'symbol': symbol})
    return result[0] if isinstance(result, list) and result else result

def fetch_metrics(symbol: str, limit: int = 4) -> List[Dict]:
    return _request('key-metrics', {'symbol': symbol, 'limit': limit})

def fetch_ratios(symbol: str, limit: int = 4) -> List[Dict]:
    return _request('ratios', {'symbol': symbol, 'limit': limit})

def fetch_growth(symbol: str, limit: int = 4) -> List[Dict]:
    return _request('financial-growth', {'symbol': symbol, 'limit': limit})

def fetch_income(symbol: str, limit: int = 4) -> List[Dict]:
    return _request('income-statement', {'symbol': symbol, 'limit': limit})

def fetch_balance(symbol: str, limit: int = 1) -> List[Dict]:
    return _request('balance-sheet-statement', {'symbol': symbol, 'limit': limit})

def fetch_cashflow(symbol: str, limit: int = 4) -> List[Dict]:
    return _request('cash-flow-statement', {'symbol': symbol, 'limit': limit})

def fetch_peers(symbol: str) -> List[str]:
    result = _request('stock-peers', {'symbol': symbol})
    if isinstance(result, list) and result and 'peersList' in result[0]:
        return result[0]['peersList'][:8]
    return []

def fetch_institutional(symbol: str, limit: int = 10) -> List[Dict]:
    return _request('institutional-holder', {'symbol': symbol, 'limit': limit})

def fetch_insiders(symbol: str, limit: int = 15) -> List[Dict]:
    return _request('insider-trades', {'symbol': symbol, 'limit': limit})

def fetch_news(symbol: str, limit: int = 5) -> List[Dict]:
    return _request('company-news', {'symbols': symbol, 'limit': limit})

def fetch_analyst_estimates(symbol: str) -> List[Dict]:
    return _request('analyst-estimates', {'symbol': symbol, 'limit': 1})

# =============================================================================
# Analysis Framework
# =============================================================================

def safe_get(data: Any, key: str, default: Any = None) -> Any:
    """Safely get nested values."""
    if isinstance(data, list) and data:
        data = data[0]
    if isinstance(data, dict):
        return data.get(key, default)
    return default

def fmt_pct(value: float, decimals: int = 2) -> str:
    """Format as percentage."""
    if value is None:
        return "N/A"
    return f"{value * 100:.{decimals}f}%"

def fmt_num(value: float, decimals: int = 2) -> str:
    """Format number."""
    if value is None:
        return "N/A"
    return f"{value:.{decimals}f}"

def fmt_money(value: float) -> str:
    """Format as money (B/M)."""
    if value is None:
        return "N/A"
    if abs(value) >= 1e12:
        return f"${value/1e12:.2f}T"
    if abs(value) >= 1e9:
        return f"${value/1e9:.2f}B"
    if abs(value) >= 1e6:
        return f"${value/1e6:.2f}M"
    return f"${value:,.0f}"

def score_metric(value: float, thresholds: tuple, higher_better: bool = True) -> str:
    """Score metric: 🟢 good, 🟡 neutral, 🔴 bad."""
    if value is None:
        return "⚪"
    low, high = thresholds
    if higher_better:
        if value >= high:
            return "🟢"
        elif value >= low:
            return "🟡"
        else:
            return "🔴"
    else:  # lower is better
        if value <= low:
            return "🟢"
        elif value <= high:
            return "🟡"
        else:
            return "🔴"

# =============================================================================
# Analysis Sections
# =============================================================================

def analyze_profile(profile: Dict, quote: Dict) -> Dict:
    """Section 1: Company Profile."""
    return {
        "name": profile.get('companyName', 'N/A'),
        "symbol": profile.get('symbol', 'N/A'),
        "sector": profile.get('sector', 'N/A'),
        "industry": profile.get('industry', 'N/A'),
        "country": profile.get('country', 'N/A'),
        "employees": profile.get('fullTimeEmployees', 'N/A'),
        "exchange": profile.get('exchange', 'N/A'),
        "price": quote.get('price', 0),
        "change_pct": quote.get('changePercentage', 0),
        "market_cap": profile.get('marketCap', 0),
        "range_52w": profile.get('range', 'N/A'),
        "description": (profile.get('description', '') or '')[:300],
    }

def analyze_valuation(metrics: List[Dict], quote: Dict, profile: Dict) -> Dict:
    """Section 2: Valuation Metrics."""
    m = metrics[0] if metrics else {}
    
    pe = m.get('peRatio')
    ev_ebitda = m.get('evToEBITDA')
    ev_sales = m.get('evToSales')
    pb = m.get('priceToBookRatio')
    ps = m.get('priceToSalesRatio')
    earnings_yield = m.get('earningsYield')
    fcf_yield = m.get('freeCashFlowYield')
    
    return {
        "pe_ratio": {"value": pe, "score": score_metric(pe, (15, 25), higher_better=False) if pe else "⚪"},
        "ev_ebitda": {"value": ev_ebitda, "score": score_metric(ev_ebitda, (10, 20), higher_better=False) if ev_ebitda else "⚪"},
        "ev_sales": {"value": ev_sales, "score": score_metric(ev_sales, (3, 10), higher_better=False) if ev_sales else "⚪"},
        "price_to_book": {"value": pb, "score": score_metric(pb, (1, 5), higher_better=False) if pb else "⚪"},
        "price_to_sales": {"value": ps, "score": score_metric(ps, (2, 8), higher_better=False) if ps else "⚪"},
        "earnings_yield": {"value": earnings_yield, "fmt": fmt_pct(earnings_yield)},
        "fcf_yield": {"value": fcf_yield, "fmt": fmt_pct(fcf_yield)},
    }

def analyze_financial_health(metrics: List[Dict], balance: List[Dict]) -> Dict:
    """Section 3: Financial Health."""
    m = metrics[0] if metrics else {}
    b = balance[0] if balance else {}
    
    current_ratio = m.get('currentRatio')
    net_debt_ebitda = m.get('netDebtToEBITDA')
    interest_coverage = m.get('interestCoverage')
    
    total_debt = b.get('totalDebt', 0)
    total_equity = b.get('totalStockholdersEquity', 1)
    debt_to_equity = total_debt / total_equity if total_equity else None
    
    cash = b.get('cashAndCashEquivalents', 0)
    
    return {
        "current_ratio": {"value": current_ratio, "score": score_metric(current_ratio, (1.5, 2.0))},
        "debt_to_equity": {"value": debt_to_equity, "score": score_metric(debt_to_equity, (0.5, 1.5), higher_better=False) if debt_to_equity else "⚪"},
        "net_debt_ebitda": {"value": net_debt_ebitda, "score": score_metric(net_debt_ebitda, (1, 3), higher_better=False) if net_debt_ebitda else "⚪"},
        "interest_coverage": {"value": interest_coverage, "score": score_metric(interest_coverage, (3, 8))},
        "cash_position": cash,
        "total_debt": total_debt,
    }

def analyze_profitability(metrics: List[Dict], ratios: List[Dict]) -> Dict:
    """Section 4: Profitability."""
    m = metrics[0] if metrics else {}
    r = ratios[0] if ratios else {}
    
    roe = m.get('returnOnEquity')
    roa = m.get('returnOnAssets')
    roic = m.get('returnOnInvestedCapital')
    
    gross_margin = r.get('grossProfitMargin')
    operating_margin = r.get('operatingProfitMargin')
    net_margin = r.get('netProfitMargin')
    
    return {
        "roe": {"value": roe, "fmt": fmt_pct(roe), "score": score_metric(roe, (0.10, 0.20))},
        "roa": {"value": roa, "fmt": fmt_pct(roa), "score": score_metric(roa, (0.05, 0.10))},
        "roic": {"value": roic, "fmt": fmt_pct(roic), "score": score_metric(roic, (0.10, 0.15))},
        "gross_margin": {"value": gross_margin, "fmt": fmt_pct(gross_margin), "score": score_metric(gross_margin, (0.30, 0.50))},
        "operating_margin": {"value": operating_margin, "fmt": fmt_pct(operating_margin), "score": score_metric(operating_margin, (0.10, 0.20))},
        "net_margin": {"value": net_margin, "fmt": fmt_pct(net_margin), "score": score_metric(net_margin, (0.05, 0.15))},
    }

def analyze_growth(growth: List[Dict], income: List[Dict]) -> Dict:
    """Section 5: Growth Analysis."""
    g = growth[0] if growth else {}
    
    # Calculate YoY growth from income statements if available
    rev_growth = g.get('revenueGrowth')
    eps_growth = g.get('epsgrowth')
    fcf_growth = g.get('freeCashFlowGrowth')
    
    # Historical trend
    rev_trend = []
    if income:
        for i in income[:4]:
            rev_trend.append({"period": i.get('date', '')[:4], "revenue": i.get('revenue', 0)})
    
    return {
        "revenue_growth": {"value": rev_growth, "fmt": fmt_pct(rev_growth), "score": score_metric(rev_growth, (0.05, 0.15)) if rev_growth else "⚪"},
        "eps_growth": {"value": eps_growth, "fmt": fmt_pct(eps_growth), "score": score_metric(eps_growth, (0.05, 0.20)) if eps_growth else "⚪"},
        "fcf_growth": {"value": fcf_growth, "fmt": fmt_pct(fcf_growth), "score": score_metric(fcf_growth, (0.05, 0.15)) if fcf_growth else "⚪"},
        "revenue_trend": rev_trend,
    }

def analyze_quality(metrics: List[Dict]) -> Dict:
    """Section 6: Quality Indicators."""
    m = metrics[0] if metrics else {}
    
    income_quality = m.get('incomeQuality')  # Operating CF / Net Income
    capex_to_depreciation = m.get('capexToDepreciation')
    rd_to_revenue = m.get('researchAndDevelopementToRevenue')
    sbc_to_revenue = m.get('stockBasedCompensationToRevenue')
    
    return {
        "income_quality": {"value": income_quality, "score": score_metric(income_quality, (0.8, 1.2))},
        "capex_depreciation": {"value": capex_to_depreciation, "note": ">1 = investing in growth"},
        "rd_to_revenue": {"value": rd_to_revenue, "fmt": fmt_pct(rd_to_revenue)},
        "sbc_to_revenue": {"value": sbc_to_revenue, "fmt": fmt_pct(sbc_to_revenue), "score": score_metric(sbc_to_revenue, (0.03, 0.08), higher_better=False) if sbc_to_revenue else "⚪"},
    }

def analyze_ownership(institutional: Any, insiders: Any) -> Dict:
    """Section 7: Ownership Signals."""
    top_holders = []
    
    # Handle various response formats
    if isinstance(institutional, list):
        for h in institutional[:5]:
            if isinstance(h, dict):
                top_holders.append({
                    "holder": h.get('holder', 'N/A')[:30],
                    "shares": h.get('shares', 0),
                    "weight": h.get('weight', 0),
                })
    
    insider_activity = {"buys": 0, "sells": 0, "net_shares": 0}
    recent_insiders = []
    
    # Handle various response formats
    insiders_list = insiders if isinstance(insiders, list) else []
    for t in insiders_list[:10]:
        trans = t.get('transactionType', '').lower()
        shares = t.get('securitiesTransacted', 0)
        if 'buy' in trans or 'purchase' in trans:
            insider_activity['buys'] += 1
            insider_activity['net_shares'] += shares
        elif 'sell' in trans or 'sale' in trans:
            insider_activity['sells'] += 1
            insider_activity['net_shares'] -= shares
        recent_insiders.append({
            "name": t.get('reportingName', 'N/A')[:25],
            "type": t.get('transactionType', 'N/A'),
            "shares": shares,
            "date": t.get('transactionDate', '')[:10],
        })
    
    return {
        "top_holders": top_holders,
        "insider_activity": insider_activity,
        "recent_insiders": recent_insiders[:5],
    }

def analyze_peers(symbol: str, peers: Any, metrics: Any) -> Dict:
    """Section 8: Peer Comparison."""
    peers_list = peers if isinstance(peers, list) else []
    if not peers_list:
        return {"peers": [], "comparison": []}
    
    comparison = []
    metrics_list = metrics if isinstance(metrics, list) else []
    my_metrics = metrics_list[0] if metrics_list else {}
    
    # Get peer metrics
    for peer in peers_list[:5]:
        peer_metrics = fetch_metrics(peer, limit=1)
        pm = peer_metrics[0] if peer_metrics and isinstance(peer_metrics, list) else {}
        if pm:
            comparison.append({
                "symbol": peer,
                "pe": pm.get('peRatio'),
                "ev_ebitda": pm.get('evToEBITDA'),
                "roe": pm.get('returnOnEquity'),
                "market_cap": pm.get('marketCap'),
            })
    
    return {
        "peers": peers_list,
        "comparison": comparison,
        "my_pe": my_metrics.get('peRatio'),
        "my_ev_ebitda": my_metrics.get('evToEBITDA'),
        "my_roe": my_metrics.get('returnOnEquity'),
    }

def analyze_news(news: Any) -> Dict:
    """Section 9: Recent News."""
    headlines = []
    news_list = news if isinstance(news, list) else []
    for n in news_list[:5]:
        headlines.append({
            "title": n.get('title', 'N/A')[:80],
            "date": n.get('publishedDate', '')[:10],
            "site": n.get('site', 'N/A'),
            "sentiment": n.get('sentiment', 'neutral'),
        })
    return {"headlines": headlines}

def analyze_risks(all_data: Dict) -> Dict:
    """Section 10: Risk Assessment."""
    flags = []
    warnings = []
    strengths = []
    
    valuation = all_data.get('valuation', {})
    health = all_data.get('financial_health', {})
    profitability = all_data.get('profitability', {})
    growth = all_data.get('growth', {})
    quality = all_data.get('quality', {})
    ownership = all_data.get('ownership', {})
    
    # Valuation flags
    pe = valuation.get('pe_ratio', {}).get('value')
    if pe and pe > 50:
        flags.append(f"🔴 High P/E ratio ({pe:.1f}) - expensive valuation")
    elif pe and pe > 30:
        warnings.append(f"🟡 Elevated P/E ratio ({pe:.1f})")
    elif pe and pe > 0 and pe < 15:
        strengths.append(f"🟢 Reasonable P/E ({pe:.1f})")
    
    # Health flags
    current = health.get('current_ratio', {}).get('value')
    if current and current < 1:
        flags.append(f"🔴 Current ratio below 1 ({current:.2f}) - liquidity risk")
    elif current and current > 2:
        strengths.append(f"🟢 Strong liquidity (current ratio: {current:.2f})")
    
    d_e = health.get('debt_to_equity', {}).get('value')
    if d_e and d_e > 2:
        flags.append(f"🔴 High debt/equity ({d_e:.2f}) - leverage risk")
    elif d_e and d_e < 0.5:
        strengths.append(f"🟢 Low leverage (D/E: {d_e:.2f})")
    
    # Profitability flags
    roe = profitability.get('roe', {}).get('value')
    if roe and roe > 0.20:
        strengths.append(f"🟢 Excellent ROE ({roe*100:.1f}%)")
    elif roe and roe < 0.05:
        warnings.append(f"🟡 Low ROE ({roe*100:.1f}%)")
    elif roe and roe < 0:
        flags.append(f"🔴 Negative ROE - unprofitable")
    
    # Growth flags
    rev_growth = growth.get('revenue_growth', {}).get('value')
    if rev_growth and rev_growth > 0.20:
        strengths.append(f"🟢 Strong revenue growth ({rev_growth*100:.1f}%)")
    elif rev_growth and rev_growth < 0:
        flags.append(f"🔴 Revenue declining ({rev_growth*100:.1f}%)")
    
    # Quality flags
    income_q = quality.get('income_quality', {}).get('value')
    if income_q and income_q < 0.5:
        flags.append(f"🔴 Low income quality ({income_q:.2f}) - earnings may not be cash-backed")
    elif income_q and income_q > 1:
        strengths.append(f"🟢 Strong cash generation (income quality: {income_q:.2f})")
    
    sbc = quality.get('sbc_to_revenue', {}).get('value')
    if sbc and sbc > 0.10:
        warnings.append(f"🟡 High stock compensation ({sbc*100:.1f}% of revenue)")
    
    # Insider activity
    insider = ownership.get('insider_activity', {})
    if insider.get('sells', 0) > insider.get('buys', 0) * 3:
        warnings.append(f"🟡 More insider selling than buying")
    elif insider.get('buys', 0) > insider.get('sells', 0) * 2:
        strengths.append(f"🟢 Net insider buying")
    
    return {
        "red_flags": flags,
        "warnings": warnings,
        "strengths": strengths,
        "overall_score": len(strengths) - len(flags),
    }

# =============================================================================
# Report Generation
# =============================================================================

def generate_report(symbol: str, data: Dict) -> str:
    """Generate formatted analysis report."""
    lines = []
    
    # Header
    profile = data.get('profile', {})
    lines.append(f"# 📊 Stock Analysis: {profile.get('name', symbol)} ({symbol})")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} SGT*")
    lines.append("")
    
    # Quick Stats
    lines.append("## Quick Stats")
    lines.append(f"**Price:** ${profile.get('price', 0):.2f} ({profile.get('change_pct', 0):+.2f}%)")
    lines.append(f"**Market Cap:** {fmt_money(profile.get('market_cap', 0))}")
    lines.append(f"**Sector:** {profile.get('sector', 'N/A')} | **Industry:** {profile.get('industry', 'N/A')}")
    lines.append(f"**52W Range:** {profile.get('range_52w', 'N/A')}")
    lines.append("")
    
    # Valuation
    lines.append("## 📈 Valuation")
    val = data.get('valuation', {})
    pe = val.get('pe_ratio', {})
    lines.append(f"| Metric | Value | Score |")
    lines.append(f"|--------|-------|-------|")
    lines.append(f"| P/E Ratio | {fmt_num(pe.get('value'))} | {pe.get('score', '⚪')} |")
    ev_eb = val.get('ev_ebitda', {})
    lines.append(f"| EV/EBITDA | {fmt_num(ev_eb.get('value'))} | {ev_eb.get('score', '⚪')} |")
    ev_s = val.get('ev_sales', {})
    lines.append(f"| EV/Sales | {fmt_num(ev_s.get('value'))} | {ev_s.get('score', '⚪')} |")
    lines.append(f"| Earnings Yield | {val.get('earnings_yield', {}).get('fmt', 'N/A')} | |")
    lines.append(f"| FCF Yield | {val.get('fcf_yield', {}).get('fmt', 'N/A')} | |")
    lines.append("")
    
    # Financial Health
    lines.append("## 💰 Financial Health")
    health = data.get('financial_health', {})
    lines.append(f"| Metric | Value | Score |")
    lines.append(f"|--------|-------|-------|")
    cr = health.get('current_ratio', {})
    lines.append(f"| Current Ratio | {fmt_num(cr.get('value'))} | {cr.get('score', '⚪')} |")
    de = health.get('debt_to_equity', {})
    lines.append(f"| Debt/Equity | {fmt_num(de.get('value'))} | {de.get('score', '⚪')} |")
    nd_eb = health.get('net_debt_ebitda', {})
    lines.append(f"| Net Debt/EBITDA | {fmt_num(nd_eb.get('value'))} | {nd_eb.get('score', '⚪')} |")
    lines.append(f"| Cash Position | {fmt_money(health.get('cash_position', 0))} | |")
    lines.append("")
    
    # Profitability
    lines.append("## 📊 Profitability")
    prof = data.get('profitability', {})
    lines.append(f"| Metric | Value | Score |")
    lines.append(f"|--------|-------|-------|")
    for key in ['roe', 'roa', 'roic', 'gross_margin', 'operating_margin', 'net_margin']:
        m = prof.get(key, {})
        label = key.upper().replace('_', ' ')
        lines.append(f"| {label} | {m.get('fmt', 'N/A')} | {m.get('score', '⚪')} |")
    lines.append("")
    
    # Growth
    lines.append("## 📈 Growth")
    growth = data.get('growth', {})
    lines.append(f"| Metric | Value | Score |")
    lines.append(f"|--------|-------|-------|")
    for key in ['revenue_growth', 'eps_growth', 'fcf_growth']:
        m = growth.get(key, {})
        label = key.replace('_', ' ').title()
        lines.append(f"| {label} | {m.get('fmt', 'N/A')} | {m.get('score', '⚪')} |")
    
    # Revenue trend
    trend = growth.get('revenue_trend', [])
    if trend:
        lines.append("")
        lines.append("**Revenue Trend:**")
        for t in trend:
            lines.append(f"  {t['period']}: {fmt_money(t['revenue'])}")
    lines.append("")
    
    # Quality
    lines.append("## ✅ Quality Indicators")
    quality = data.get('quality', {})
    iq = quality.get('income_quality', {})
    lines.append(f"- **Income Quality** (OCF/NI): {fmt_num(iq.get('value'))} {iq.get('score', '⚪')}")
    lines.append(f"- **Capex/Depreciation:** {fmt_num(quality.get('capex_depreciation', {}).get('value'))} (>1 = investing)")
    lines.append(f"- **R&D/Revenue:** {quality.get('rd_to_revenue', {}).get('fmt', 'N/A')}")
    sbc = quality.get('sbc_to_revenue', {})
    lines.append(f"- **SBC/Revenue:** {sbc.get('fmt', 'N/A')} {sbc.get('score', '⚪')}")
    lines.append("")
    
    # Ownership
    lines.append("## 👥 Ownership")
    ownership = data.get('ownership', {})
    
    lines.append("**Top Institutional Holders:**")
    for h in ownership.get('top_holders', [])[:3]:
        lines.append(f"  - {h['holder']}: {h['shares']:,} shares ({h['weight']*100:.1f}%)")
    
    insider = ownership.get('insider_activity', {})
    lines.append(f"\n**Insider Activity (recent):** {insider.get('buys', 0)} buys, {insider.get('sells', 0)} sells")
    lines.append("")
    
    # Peer Comparison
    lines.append("## 🔄 Peer Comparison")
    peers = data.get('peers', {})
    if peers.get('comparison'):
        lines.append(f"| Peer | P/E | EV/EBITDA | ROE |")
        lines.append(f"|------|-----|-----------|-----|")
        lines.append(f"| **{symbol}** | {fmt_num(peers.get('my_pe'))} | {fmt_num(peers.get('my_ev_ebitda'))} | {fmt_pct(peers.get('my_roe'))} |")
        for p in peers.get('comparison', []):
            lines.append(f"| {p['symbol']} | {fmt_num(p.get('pe'))} | {fmt_num(p.get('ev_ebitda'))} | {fmt_pct(p.get('roe'))} |")
    else:
        lines.append("*No peer data available*")
    lines.append("")
    
    # News
    lines.append("## 📰 Recent News")
    news = data.get('news', {})
    for h in news.get('headlines', [])[:3]:
        lines.append(f"- [{h['date']}] {h['title']}")
    lines.append("")
    
    # Risk Assessment
    lines.append("## ⚠️ Risk Assessment")
    risks = data.get('risks', {})
    
    if risks.get('red_flags'):
        lines.append("**Red Flags:**")
        for f in risks['red_flags']:
            lines.append(f"  {f}")
    
    if risks.get('warnings'):
        lines.append("**Warnings:**")
        for w in risks['warnings']:
            lines.append(f"  {w}")
    
    if risks.get('strengths'):
        lines.append("**Strengths:**")
        for s in risks['strengths']:
            lines.append(f"  {s}")
    
    score = risks.get('overall_score', 0)
    if score >= 3:
        verdict = "🟢 POSITIVE"
    elif score >= 0:
        verdict = "🟡 NEUTRAL"
    else:
        verdict = "🔴 CAUTIOUS"
    
    lines.append(f"\n**Overall Assessment:** {verdict} (score: {score})")
    lines.append("")
    
    # Description
    if profile.get('description'):
        lines.append("## 📝 Company Description")
        lines.append(profile['description'] + "...")
    
    return '\n'.join(lines)

def generate_quick_summary(symbol: str, data: Dict) -> str:
    """Generate quick one-page summary."""
    lines = []
    profile = data.get('profile', {})
    val = data.get('valuation', {})
    health = data.get('financial_health', {})
    prof = data.get('profitability', {})
    risks = data.get('risks', {})
    
    lines.append(f"**{profile.get('name', symbol)} ({symbol})**")
    lines.append(f"${profile.get('price', 0):.2f} | MCap: {fmt_money(profile.get('market_cap', 0))}")
    lines.append("")
    lines.append(f"P/E: {fmt_num(val.get('pe_ratio', {}).get('value'))} | EV/EBITDA: {fmt_num(val.get('ev_ebitda', {}).get('value'))}")
    lines.append(f"ROE: {prof.get('roe', {}).get('fmt', 'N/A')} | Debt/Equity: {fmt_num(health.get('debt_to_equity', {}).get('value'))}")
    lines.append("")
    
    # Top risk/strength
    if risks.get('red_flags'):
        lines.append(f"⚠️ {risks['red_flags'][0]}")
    if risks.get('strengths'):
        lines.append(f"✅ {risks['strengths'][0]}")
    
    score = risks.get('overall_score', 0)
    if score >= 3:
        lines.append("\n**Verdict: 🟢 POSITIVE**")
    elif score >= 0:
        lines.append("\n**Verdict: 🟡 NEUTRAL**")
    else:
        lines.append("\n**Verdict: 🔴 CAUTIOUS**")
    
    return '\n'.join(lines)

# =============================================================================
# Main Entry Point
# =============================================================================

def analyze(symbol: str, quick: bool = False, verbose: bool = True) -> Dict:
    """Run full analysis on a symbol."""
    symbol = symbol.upper()
    
    if verbose:
        print(f"Analyzing {symbol}...")
    
    # Fetch all data
    profile = fetch_profile(symbol)
    if not profile or 'error' in str(profile):
        return {"error": f"Could not fetch profile for {symbol}"}
    
    quote = fetch_quote(symbol)
    metrics = fetch_metrics(symbol)
    ratios = fetch_ratios(symbol)
    growth = fetch_growth(symbol)
    income = fetch_income(symbol)
    balance = fetch_balance(symbol)
    
    if verbose:
        print("  Fetching ownership data...")
    institutional = fetch_institutional(symbol)
    insiders = fetch_insiders(symbol)
    
    if verbose:
        print("  Fetching peers...")
    peers = fetch_peers(symbol)
    
    if verbose:
        print("  Fetching news...")
    news = fetch_news(symbol)
    
    # Run analysis
    data = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "profile": analyze_profile(profile, quote),
        "valuation": analyze_valuation(metrics, quote, profile),
        "financial_health": analyze_financial_health(metrics, balance),
        "profitability": analyze_profitability(metrics, ratios),
        "growth": analyze_growth(growth, income),
        "quality": analyze_quality(metrics),
        "ownership": analyze_ownership(institutional, insiders),
        "news": analyze_news(news),
    }
    
    if not quick:
        if verbose:
            print("  Comparing to peers...")
        data["peers"] = analyze_peers(symbol, peers, metrics)
    
    # Risk assessment (needs all data)
    data["risks"] = analyze_risks(data)
    
    return data

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    try:
        init()
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    symbol = sys.argv[1].upper()
    quick = '--quick' in sys.argv
    as_json = '--json' in sys.argv
    save = '--save' in sys.argv
    
    data = analyze(symbol, quick=quick)
    
    if 'error' in data:
        print(f"Error: {data['error']}")
        return
    
    if as_json:
        print(json.dumps(data, indent=2, default=str))
    elif quick:
        print(generate_quick_summary(symbol, data))
    else:
        report = generate_report(symbol, data)
        print(report)
        
        if save:
            path = Path.home() / '.openclaw/workspace/memory/research' / f"{symbol.lower()}-analysis-{datetime.now().strftime('%Y%m%d')}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                f.write(report)
            print(f"\n✅ Saved to {path}")

if __name__ == '__main__':
    main()
