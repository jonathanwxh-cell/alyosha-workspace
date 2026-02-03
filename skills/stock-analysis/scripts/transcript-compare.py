#!/usr/bin/env python3
"""
Transcript Quarter Comparison
=============================

Compares earnings call tone across quarters to detect shifts.

Usage:
    python3 transcript-compare.py NVDA           # Last 4 quarters
    python3 transcript-compare.py NVDA --quarters 6

Detects:
- Hedging language trends (increasing = losing confidence)
- Deflection patterns over time
- Blame externalization changes
- Guidance specificity evolution
"""

import os
import sys
import json
import re
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Word lists
HEDGING_PHRASES = [
    'we believe', 'we think', 'we expect', 'we hope', 'we anticipate',
    'potentially', 'possibly', 'might', 'may', 'could', 'should',
    'uncertain', 'unclear', 'visibility', 'challenging', 'difficult'
]

EXCUSE_PHRASES = [
    'macro environment', 'macroeconomic', 'supply chain', 'headwinds',
    'one-time', 'non-recurring', 'extraordinary', 'unprecedented',
    'industry-wide', 'market conditions', 'seasonality', 'timing'
]

CONVICTION_PHRASES = [
    'we will', 'we are committed', 'absolutely', 'definitely', 'clearly',
    'record', 'best ever', 'outperform', 'exceed expectations',
    'strong conviction', 'very confident', 'extremely pleased'
]

DEFLECTION_PHRASES = [
    "that's a great question", "as I mentioned", "going forward",
    "we'll have to see", "it's early days", "too early to tell",
    "we're not going to provide", "can't comment on", "we don't disclose"
]


def get_api_key() -> str:
    env = Path.home() / '.secure/fmp.env'
    with open(env) as f:
        for line in f:
            if line.startswith('FMP_API_KEY='):
                return line.split('=', 1)[1].strip()
    raise ValueError("FMP_API_KEY not found")


def fetch_transcript(symbol: str, year: int, quarter: int) -> Optional[Dict]:
    api_key = get_api_key()
    url = f"https://financialmodelingprep.com/stable/earning-call-transcript?symbol={symbol}&year={year}&quarter={quarter}&apikey={api_key}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = json.loads(r.read())
            return data[0] if data else None
    except:
        return None


def count_phrases(text: str, phrases: List[str]) -> int:
    text_lower = text.lower()
    return sum(text_lower.count(p) for p in phrases)


def extract_qa(content: str) -> str:
    markers = [r'question.and.answer', r'q\s*&\s*a', r'your first question']
    for m in markers:
        match = re.search(m, content, re.IGNORECASE)
        if match:
            return content[match.start():]
    return content[len(content)//2:]


def analyze_quarter(symbol: str, year: int, quarter: int) -> Optional[Dict]:
    t = fetch_transcript(symbol, year, quarter)
    if not t:
        return None
    
    content = t.get('content', '')
    qa = extract_qa(content)
    words = len(content.split())
    
    hedging = count_phrases(content, HEDGING_PHRASES)
    conviction = count_phrases(content, CONVICTION_PHRASES)
    excuses = count_phrases(content, EXCUSE_PHRASES)
    deflections = count_phrases(qa, DEFLECTION_PHRASES)
    questions = qa.count('?')
    
    return {
        'period': f"{year} Q{quarter}",
        'date': t.get('date'),
        'words': words,
        'hedging_per_1k': round((hedging / words) * 1000, 2) if words else 0,
        'conviction_per_1k': round((conviction / words) * 1000, 2) if words else 0,
        'excuse_per_1k': round((excuses / words) * 1000, 2) if words else 0,
        'deflection_rate': round(deflections / max(questions, 1), 2),
        'confidence_ratio': round(conviction / max(hedging, 1), 2)
    }


def compare_quarters(symbol: str, num_quarters: int = 4) -> Dict:
    print(f"📊 Analyzing {symbol} last {num_quarters} quarters...\n")
    
    now = datetime.now()
    results = []
    
    # Generate quarter list (going backwards)
    q = (now.month - 1) // 3 + 1
    y = now.year
    
    for _ in range(num_quarters + 2):  # Try extra in case some missing
        if len(results) >= num_quarters:
            break
        
        print(f"  Fetching {y} Q{q}...", end=" ")
        analysis = analyze_quarter(symbol, y, q)
        
        if analysis:
            print(f"✅ {analysis['date']}")
            results.append(analysis)
        else:
            print("❌ not found")
        
        q -= 1
        if q <= 0:
            q = 4
            y -= 1
    
    if len(results) < 2:
        return {'error': 'Not enough transcripts found', 'symbol': symbol}
    
    # Sort by date (oldest first for trend analysis)
    results.sort(key=lambda x: x['date'])
    
    # Calculate trends
    hedging_trend = results[-1]['hedging_per_1k'] - results[0]['hedging_per_1k']
    conviction_trend = results[-1]['conviction_per_1k'] - results[0]['conviction_per_1k']
    confidence_trend = results[-1]['confidence_ratio'] - results[0]['confidence_ratio']
    deflection_trend = results[-1]['deflection_rate'] - results[0]['deflection_rate']
    
    # Generate signals
    signals = []
    
    if hedging_trend > 1.0:
        signals.append(f"🔴 Hedging language UP {hedging_trend:+.1f}/1k words — management losing confidence")
    elif hedging_trend < -1.0:
        signals.append(f"🟢 Hedging language DOWN {hedging_trend:+.1f}/1k words — growing confidence")
    
    if conviction_trend < -0.5:
        signals.append(f"🟡 Conviction language DOWN {conviction_trend:+.1f}/1k words")
    elif conviction_trend > 0.5:
        signals.append(f"🟢 Conviction language UP {conviction_trend:+.1f}/1k words")
    
    if deflection_trend > 0.1:
        signals.append(f"🔴 Deflection rate UP {deflection_trend:+.2f} — becoming more evasive")
    elif deflection_trend < -0.1:
        signals.append(f"🟢 Deflection rate DOWN {deflection_trend:+.2f} — more forthcoming")
    
    if confidence_trend < -0.3:
        signals.append(f"⚠️ Confidence ratio declining — tone shifting cautious")
    elif confidence_trend > 0.3:
        signals.append(f"🟢 Confidence ratio rising — tone more bullish")
    
    return {
        'symbol': symbol,
        'quarters_analyzed': len(results),
        'period_range': f"{results[0]['period']} to {results[-1]['period']}",
        'quarterly_data': results,
        'trends': {
            'hedging': round(hedging_trend, 2),
            'conviction': round(conviction_trend, 2),
            'confidence_ratio': round(confidence_trend, 2),
            'deflection': round(deflection_trend, 2)
        },
        'signals': signals if signals else ['📊 Tone relatively stable across quarters']
    }


def print_comparison_table(data: Dict):
    """Pretty print the comparison"""
    print("\n" + "="*80)
    print(f"TRANSCRIPT TONE COMPARISON: {data['symbol']}")
    print(f"Period: {data['period_range']}")
    print("="*80)
    
    # Header
    print(f"\n{'Quarter':<12} {'Date':<12} {'Hedge/1k':<10} {'Conv/1k':<10} {'Conf.Ratio':<12} {'Deflect':<10}")
    print("-"*70)
    
    for q in data['quarterly_data']:
        print(f"{q['period']:<12} {q['date']:<12} {q['hedging_per_1k']:<10.2f} {q['conviction_per_1k']:<10.2f} {q['confidence_ratio']:<12.2f} {q['deflection_rate']:<10.2f}")
    
    print("-"*70)
    
    # Trends
    t = data['trends']
    print(f"\n📈 TRENDS (oldest → newest):")
    print(f"   Hedging:    {t['hedging']:+.2f}/1k words")
    print(f"   Conviction: {t['conviction']:+.2f}/1k words")
    print(f"   Confidence: {t['confidence_ratio']:+.2f} ratio")
    print(f"   Deflection: {t['deflection']:+.2f} rate")
    
    # Signals
    print(f"\n🚦 SIGNALS:")
    for s in data['signals']:
        print(f"   {s}")
    
    print("\n" + "="*80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcript-compare.py SYMBOL [--quarters N]")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    quarters = 4
    
    for i, arg in enumerate(sys.argv):
        if arg == '--quarters' and i + 1 < len(sys.argv):
            quarters = int(sys.argv[i + 1])
    
    result = compare_quarters(symbol, quarters)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    
    print_comparison_table(result)
    
    # Also output JSON for programmatic use
    print("\n📄 JSON output:")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
