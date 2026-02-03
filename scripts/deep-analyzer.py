#!/usr/bin/env python3
"""
Deep Company Analyzer
=====================

Comprehensive qualitative analysis beyond basic NLP sentiment.
Combines transcript analysis, industry signals, and alternative data.

Usage:
    python3 deep-analyzer.py NVDA                    # Full analysis
    python3 deep-analyzer.py NVDA --transcript       # Just transcript deep-dive
    python3 deep-analyzer.py NVDA --scuttlebutt      # Alternative data sources
    python3 deep-analyzer.py NVDA --industry         # Industry analysis
    python3 deep-analyzer.py NVDA --management       # Management red flags
    python3 deep-analyzer.py NVDA --output report    # Save to file

Outputs actionable qualitative insights, not just numbers.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter
from typing import Dict, List, Optional, Tuple

# === Configuration ===

CACHE_DIR = Path.home() / '.openclaw/workspace/memory/research/cache'
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# === Word Lists (Enhanced) ===

# Management uncertainty signals
HEDGING_PHRASES = [
    'we believe', 'we think', 'we expect', 'we hope', 'we anticipate',
    'potentially', 'possibly', 'might', 'may', 'could', 'should',
    'uncertain', 'unclear', 'visibility', 'challenging', 'difficult',
    'working through', 'monitoring', 'evaluating', 'assessing'
]

# Blame externalization
EXCUSE_PHRASES = [
    'macro environment', 'macroeconomic', 'supply chain', 'headwinds',
    'one-time', 'non-recurring', 'extraordinary', 'unprecedented',
    'industry-wide', 'market conditions', 'seasonality', 'timing',
    'foreign exchange', 'fx impact', 'currency', 'geopolitical'
]

# Confidence signals
CONVICTION_PHRASES = [
    'we will', 'we are committed', 'absolutely', 'definitely', 'clearly',
    'record', 'best ever', 'outperform', 'exceed expectations',
    'strong conviction', 'very confident', 'extremely pleased'
]

# Deflection signals (avoiding direct answers)
DEFLECTION_PHRASES = [
    "that's a great question", "as I mentioned", "going forward",
    "we'll have to see", "it's early days", "too early to tell",
    "we're not going to provide", "can't comment on", "we don't disclose"
]

# Forward guidance quality
SPECIFIC_GUIDANCE_MARKERS = [
    'between', 'range of', 'approximately', 'percent', '%', 
    'million', 'billion', 'basis points', 'quarters'
]

VAGUE_GUIDANCE_MARKERS = [
    'solid', 'healthy', 'reasonable', 'moderate', 'meaningful',
    'significant', 'substantial', 'consistent with', 'in line with'
]


def get_api_key(name: str = 'FMP') -> str:
    """Load API key from secure storage"""
    env_key = f'{name}_API_KEY'
    key = os.environ.get(env_key)
    if key:
        return key
    
    env_paths = [
        Path.home() / f'.secure/{name.lower()}.env',
        Path(f'.secure/{name.lower()}.env'),
    ]
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith(f'{env_key}='):
                        return line.split('=', 1)[1].strip()
    raise ValueError(f"{env_key} not found")


def fetch_json(url: str, cache_key: str = None, cache_hours: int = 24) -> Optional[Dict]:
    """Fetch JSON with caching"""
    if cache_key:
        cache_file = CACHE_DIR / f"{cache_key}.json"
        if cache_file.exists():
            age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if age < cache_hours * 3600:
                with open(cache_file) as f:
                    return json.load(f)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            if cache_key and data:
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
            return data
    except Exception as e:
        print(f"Fetch error: {e}", file=sys.stderr)
        return None


# === Transcript Analysis ===

def fetch_transcript(symbol: str, year: int = None, quarter: int = None) -> Optional[Dict]:
    """Fetch latest or specific transcript"""
    api_key = get_api_key('FMP')
    
    # FMP requires year and quarter - default to recent quarters
    if not year or not quarter:
        from datetime import datetime
        now = datetime.now()
        # Try last few quarters
        for q_offset in range(4):
            test_q = ((now.month - 1) // 3) - q_offset
            test_y = now.year
            while test_q <= 0:
                test_q += 4
                test_y -= 1
            
            url = f"https://financialmodelingprep.com/stable/earning-call-transcript?symbol={symbol}&year={test_y}&quarter={test_q}&apikey={api_key}"
            data = fetch_json(url, None, 1)  # Don't cache when searching
            if data and len(data) > 0:
                return data[0]
        return None
    
    url = f"https://financialmodelingprep.com/stable/earning-call-transcript?symbol={symbol}&year={year}&quarter={quarter}&apikey={api_key}"
    data = fetch_json(url, f"transcript_{symbol}_{year}_{quarter}", 168)
    return data[0] if data else None


def extract_sections(content: str) -> Dict[str, str]:
    """Split transcript into prepared remarks vs Q&A"""
    qa_markers = [
        r'question.and.answer',
        r'q\s*&\s*a\s+session',
        r'operator.*question',
        r'your first question',
        r'we will now begin.*question',
        r'open.*for questions'
    ]
    
    for marker in qa_markers:
        match = re.search(marker, content, re.IGNORECASE)
        if match:
            return {
                'prepared': content[:match.start()],
                'qa': content[match.start():]
            }
    
    # Fallback: estimate split
    midpoint = len(content) // 2
    return {
        'prepared': content[:midpoint],
        'qa': content[midpoint:]
    }


def count_phrase_occurrences(text: str, phrases: List[str]) -> int:
    """Count how many times any phrase appears"""
    text_lower = text.lower()
    return sum(text_lower.count(phrase) for phrase in phrases)


def analyze_guidance_quality(text: str) -> Dict:
    """Is guidance specific or vague?"""
    specific = count_phrase_occurrences(text, SPECIFIC_GUIDANCE_MARKERS)
    vague = count_phrase_occurrences(text, VAGUE_GUIDANCE_MARKERS)
    
    total = specific + vague
    if total == 0:
        return {'quality': 'none', 'specific_ratio': 0}
    
    ratio = specific / total
    quality = 'specific' if ratio > 0.6 else 'vague' if ratio < 0.4 else 'mixed'
    
    return {
        'quality': quality,
        'specific_ratio': round(ratio, 2),
        'specific_count': specific,
        'vague_count': vague
    }


def analyze_deflection(qa_text: str) -> Dict:
    """How much is management deflecting in Q&A?"""
    # Count analyst questions (approximation)
    question_marks = qa_text.count('?')
    deflections = count_phrase_occurrences(qa_text, DEFLECTION_PHRASES)
    
    if question_marks == 0:
        return {'deflection_rate': 0, 'interpretation': 'no Q&A parsed'}
    
    rate = deflections / question_marks
    
    interpretation = 'evasive' if rate > 0.3 else 'somewhat guarded' if rate > 0.15 else 'forthcoming'
    
    return {
        'deflection_rate': round(rate, 2),
        'deflections': deflections,
        'questions': question_marks,
        'interpretation': interpretation
    }


def analyze_blame_patterns(text: str) -> Dict:
    """Is management externalizing blame?"""
    excuses = count_phrase_occurrences(text, EXCUSE_PHRASES)
    words = len(text.split())
    rate = (excuses / words) * 1000 if words > 0 else 0
    
    # Also look for ownership language
    ownership_phrases = ['we could have', 'we should have', 'we made mistakes', 
                        'our execution', 'we take responsibility']
    ownership = count_phrase_occurrences(text, ownership_phrases)
    
    if excuses > 0 and ownership == 0:
        pattern = 'externalizing'
    elif ownership > 0:
        pattern = 'accountable'
    else:
        pattern = 'neutral'
    
    return {
        'excuse_count': excuses,
        'ownership_count': ownership,
        'per_1000_words': round(rate, 2),
        'pattern': pattern
    }


def transcript_deep_analysis(symbol: str, year: int = None, quarter: int = None) -> Dict:
    """Full qualitative transcript analysis"""
    transcript = fetch_transcript(symbol, year, quarter)
    
    if not transcript:
        return {'error': f'No transcript found for {symbol}'}
    
    content = transcript.get('content', '')
    sections = extract_sections(content)
    
    # Prepared remarks analysis
    prepared_hedging = count_phrase_occurrences(sections['prepared'], HEDGING_PHRASES)
    prepared_conviction = count_phrase_occurrences(sections['prepared'], CONVICTION_PHRASES)
    
    # Q&A analysis
    qa_hedging = count_phrase_occurrences(sections['qa'], HEDGING_PHRASES)
    qa_conviction = count_phrase_occurrences(sections['qa'], CONVICTION_PHRASES)
    
    # Tone shift (Q&A typically more revealing)
    prepared_ratio = prepared_conviction / max(prepared_hedging, 1)
    qa_ratio = qa_conviction / max(qa_hedging, 1)
    tone_shift = prepared_ratio - qa_ratio
    
    deflection = analyze_deflection(sections['qa'])
    blame = analyze_blame_patterns(content)
    guidance = analyze_guidance_quality(content)
    
    # Generate signals
    signals = []
    
    if tone_shift > 0.5:
        signals.append("⚠️ Prepared remarks more confident than Q&A — potential sugarcoating")
    if tone_shift < -0.3:
        signals.append("🟢 Q&A more confident than prepared — genuine conviction")
    
    if deflection['interpretation'] == 'evasive':
        signals.append("🔴 High deflection rate — management avoiding questions")
    
    if blame['pattern'] == 'externalizing':
        signals.append("🟡 Blame externalization — excuses without ownership")
    elif blame['pattern'] == 'accountable':
        signals.append("🟢 Management taking accountability")
    
    if guidance['quality'] == 'vague':
        signals.append("🟡 Vague guidance — lack of visibility or hiding something")
    elif guidance['quality'] == 'specific':
        signals.append("🟢 Specific guidance — management has visibility")
    
    return {
        'symbol': symbol,
        'period': f"{year or 'latest'} Q{quarter or '?'}",
        'date': transcript.get('date'),
        'word_count': len(content.split()),
        'tone_analysis': {
            'prepared_confidence': round(prepared_ratio, 2),
            'qa_confidence': round(qa_ratio, 2),
            'tone_shift': round(tone_shift, 2),
            'interpretation': 'sugarcoating' if tone_shift > 0.5 else 'genuine' if tone_shift < -0.3 else 'consistent'
        },
        'deflection': deflection,
        'blame_patterns': blame,
        'guidance_quality': guidance,
        'signals': signals if signals else ['📊 No strong qualitative signals']
    }


# === Scuttlebutt / Alternative Data ===

def fetch_glassdoor_signal(company: str) -> Dict:
    """Note: Real Glassdoor scraping requires their API or Apify"""
    return {
        'source': 'glassdoor',
        'note': 'Requires manual check or Apify scraper',
        'url': f'https://www.glassdoor.com/Search/results.htm?keyword={urllib.parse.quote(company)}',
        'what_to_look_for': [
            'CEO approval trend (declining = red flag)',
            'Recent review sentiment shift',
            'Mentions of layoffs, reorgs, chaos',
            'Work-life balance complaints spike',
            'Senior leadership mentions'
        ]
    }


def fetch_reddit_sentiment(company: str) -> Dict:
    """Search Reddit for company mentions"""
    # Using web search as proxy
    return {
        'source': 'reddit',
        'note': 'Search manually or use Apify',
        'search_query': f'site:reddit.com "{company}" stock',
        'subreddits_to_check': [
            f'r/wallstreetbets (sentiment, memes)',
            f'r/stocks (discussion quality)',
            f'r/investing (long-term view)',
            f'r/{company.lower()} (customer issues)'
        ]
    }


def fetch_insider_transactions(symbol: str) -> Dict:
    """Fetch insider trading data"""
    api_key = get_api_key('FMP')
    url = f"https://financialmodelingprep.com/stable/insider-trading?symbol={symbol}&apikey={api_key}"
    
    data = fetch_json(url, f"insider_{symbol}", 24)
    
    if not data:
        return {'error': 'No insider data', 'symbol': symbol}
    
    # Analyze recent 90 days
    cutoff = datetime.now() - timedelta(days=90)
    recent = []
    
    for txn in data[:50]:  # Last 50 transactions
        try:
            txn_date = datetime.strptime(txn.get('transactionDate', ''), '%Y-%m-%d')
            if txn_date >= cutoff:
                recent.append(txn)
        except:
            continue
    
    buys = [t for t in recent if t.get('transactionType') == 'P-Purchase']
    sells = [t for t in recent if t.get('transactionType') == 'S-Sale']
    
    buy_value = sum(t.get('value', 0) or 0 for t in buys)
    sell_value = sum(t.get('value', 0) or 0 for t in sells)
    
    # Cluster detection (multiple insiders buying together = strong signal)
    buy_names = list(set(t.get('reportingName', '') for t in buys))
    
    signals = []
    if len(buy_names) >= 3:
        signals.append(f"🟢 Cluster buying: {len(buy_names)} insiders bought recently")
    if sell_value > buy_value * 5:
        signals.append("🔴 Heavy insider selling vs buying")
    if buy_value > sell_value * 3:
        signals.append("🟢 Insiders are net buyers")
    
    return {
        'symbol': symbol,
        'period': 'last 90 days',
        'buys': {'count': len(buys), 'value': buy_value},
        'sells': {'count': len(sells), 'value': sell_value},
        'net': buy_value - sell_value,
        'unique_buyers': buy_names[:5],
        'signals': signals if signals else ['📊 Neutral insider activity']
    }


def scuttlebutt_sources(symbol: str, company_name: str) -> Dict:
    """Generate scuttlebutt research checklist"""
    return {
        'symbol': symbol,
        'company': company_name,
        'sources_to_check': {
            'employee_sentiment': fetch_glassdoor_signal(company_name),
            'social_sentiment': fetch_reddit_sentiment(company_name),
            'insider_transactions': fetch_insider_transactions(symbol),
            'patent_activity': {
                'source': 'Google Patents',
                'url': f'https://patents.google.com/?assignee={urllib.parse.quote(company_name)}&sort=new',
                'what_to_look_for': 'Filing velocity, technology direction'
            },
            'job_postings': {
                'source': 'LinkedIn Jobs',
                'url': f'https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(company_name)}',
                'what_to_look_for': 'Hiring velocity, new teams, strategic areas'
            },
            'customer_reviews': {
                'source': 'G2 / Gartner Peer Insights',
                'what_to_look_for': 'Recent review trends, competitive comparisons'
            },
            'supplier_mentions': {
                'action': 'Search 10-Ks of key suppliers for concentration mentions',
                'example': 'TSMC mentions NVDA as significant customer'
            }
        }
    }


# === Industry Analysis ===

def fetch_sector_peers(symbol: str) -> Dict:
    """Get sector peers for competitive analysis"""
    api_key = get_api_key('FMP')
    url = f"https://financialmodelingprep.com/stable/stock-peers?symbol={symbol}&apikey={api_key}"
    
    data = fetch_json(url, f"peers_{symbol}", 168)
    return data[0] if data else {'error': 'No peers data'}


def industry_analysis_template(symbol: str) -> Dict:
    """Generate industry analysis framework"""
    peers = fetch_sector_peers(symbol)
    
    return {
        'symbol': symbol,
        'peers': peers.get('peersList', [])[:10] if isinstance(peers, dict) else [],
        'analysis_framework': {
            'competitive_dynamics': {
                'questions': [
                    'Who are the top 3 competitors and what % market share?',
                    'Is the market consolidating or fragmenting?',
                    'What is the basis of competition (price, features, service)?',
                    'Are there winner-take-all dynamics (network effects)?'
                ]
            },
            'industry_cycle': {
                'questions': [
                    'Where in the cycle? (early/growth/mature/decline)',
                    'What drives the cycle (capex, innovation, regulation)?',
                    'How long is a typical cycle?'
                ]
            },
            'disruption_risk': {
                'questions': [
                    'What technology could disrupt this in 3-5 years?',
                    'Who are the insurgent competitors?',
                    'Is the incumbent adapting or resisting?'
                ]
            },
            'regulatory_environment': {
                'questions': [
                    'What regulations impact this industry?',
                    'Is regulation tightening or loosening?',
                    'Any pending legislation that could change dynamics?'
                ]
            }
        }
    }


# === Management Red Flags ===

def management_red_flag_check(symbol: str) -> Dict:
    """Check for management quality red flags"""
    api_key = get_api_key('FMP')
    
    # Fetch company profile
    profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={api_key}"
    profile = fetch_json(profile_url, f"profile_{symbol}", 24)
    profile = profile[0] if profile else {}
    
    # Fetch key executives
    exec_url = f"https://financialmodelingprep.com/stable/key-executives?symbol={symbol}&apikey={api_key}"
    executives = fetch_json(exec_url, f"execs_{symbol}", 168) or []
    
    red_flags = []
    yellow_flags = []
    green_flags = []
    
    # Check CEO tenure
    ceo = next((e for e in executives if 'CEO' in str(e.get('title', ''))), None)
    if ceo:
        # Note: would need additional data for tenure
        pass
    
    # Check for co-CEOs (often a red flag)
    ceos = [e for e in executives if 'CEO' in str(e.get('title', ''))]
    if len(ceos) > 1:
        yellow_flags.append("Multiple CEOs listed — potential leadership issues")
    
    # Check CFO (CFO departures are warning signs)
    cfos = [e for e in executives if 'CFO' in str(e.get('title', ''))]
    if not cfos:
        yellow_flags.append("No CFO listed — check for recent departure")
    
    # Insider transactions check
    insider_data = fetch_insider_transactions(symbol)
    if 'signals' in insider_data:
        for signal in insider_data['signals']:
            if '🔴' in signal:
                red_flags.append(signal)
            elif '🟢' in signal:
                green_flags.append(signal)
    
    return {
        'symbol': symbol,
        'company': profile.get('companyName', symbol),
        'ceo': ceo.get('name') if ceo else 'Unknown',
        'executives_count': len(executives),
        'red_flags': red_flags if red_flags else ['None detected'],
        'yellow_flags': yellow_flags if yellow_flags else ['None detected'],
        'green_flags': green_flags if green_flags else ['None detected'],
        'manual_checks_needed': [
            'Audit opinion history (10-K)',
            'Related party transactions (proxy)',
            'Executive compensation structure (proxy)',
            'Prior company track records (LinkedIn)',
            'Glassdoor CEO approval trend'
        ]
    }


# === Main ===

def full_analysis(symbol: str) -> Dict:
    """Run complete deep analysis"""
    print(f"🔍 Deep analysis: {symbol}")
    
    # Get company name first
    api_key = get_api_key('FMP')
    profile_url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={api_key}"
    profile = fetch_json(profile_url, f"profile_{symbol}", 24)
    company_name = profile[0].get('companyName', symbol) if profile else symbol
    
    results = {
        'symbol': symbol,
        'company': company_name,
        'generated': datetime.now().isoformat(),
        'transcript': transcript_deep_analysis(symbol),
        'management': management_red_flag_check(symbol),
        'scuttlebutt': scuttlebutt_sources(symbol, company_name),
        'industry': industry_analysis_template(symbol)
    }
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 deep-analyzer.py SYMBOL [--mode] [--output file]")
        print("Modes: --transcript, --scuttlebutt, --industry, --management")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    # Parse args
    mode = 'full'
    output_file = None
    
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--transcript':
            mode = 'transcript'
        elif arg == '--scuttlebutt':
            mode = 'scuttlebutt'
        elif arg == '--industry':
            mode = 'industry'
        elif arg == '--management':
            mode = 'management'
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
    
    # Run analysis
    if mode == 'transcript':
        result = transcript_deep_analysis(symbol)
    elif mode == 'scuttlebutt':
        result = scuttlebutt_sources(symbol, symbol)
    elif mode == 'industry':
        result = industry_analysis_template(symbol)
    elif mode == 'management':
        result = management_red_flag_check(symbol)
    else:
        result = full_analysis(symbol)
    
    output = json.dumps(result, indent=2)
    print(output)
    
    if output_file:
        output_path = Path.home() / f'.openclaw/workspace/memory/research/{output_file}.json'
        with open(output_path, 'w') as f:
            f.write(output)
        print(f"\n✅ Saved to {output_path}")


if __name__ == '__main__':
    main()
