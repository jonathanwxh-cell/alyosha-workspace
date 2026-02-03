#!/usr/bin/env python3
"""
Earnings Call Transcript Analyzer
==================================

Analyzes earnings call transcripts for sentiment, tone shifts, and signals.

Usage:
    python3 transcript-analyzer.py NVDA 2025 Q3
    python3 transcript-analyzer.py NVDA --compare  # Compare last 4 quarters

Key signals extracted:
- Q&A section analysis (more revealing than prepared remarks)
- Hedging language (uncertainty indicators)
- Confidence markers
- Forward-looking statement sentiment
- Tone shifts vs prior quarter
- Management vs analyst sentiment gap

Based on research:
- FinBERT/Loughran-McDonald lexicons for finance-specific sentiment
- Focus on extremes (strong positive/negative) per Berkeley research
- Q&A section focus per Georgia Tech methodology
"""

import os
import sys
import json
import re
import urllib.request
from pathlib import Path
from collections import Counter
from typing import Dict, List, Tuple, Optional

# Loughran-McDonald finance-specific word lists (subset - key indicators)
NEGATIVE_WORDS = {
    'loss', 'losses', 'decline', 'declined', 'declining', 'decrease', 'decreased',
    'weak', 'weaker', 'weakness', 'difficult', 'difficulties', 'challenge', 'challenges',
    'risk', 'risks', 'risky', 'uncertain', 'uncertainty', 'concern', 'concerns',
    'fail', 'failed', 'failure', 'adverse', 'negative', 'negatively', 'worse',
    'worsen', 'worsening', 'slowdown', 'slowing', 'miss', 'missed', 'missing',
    'shortfall', 'downturn', 'headwind', 'headwinds', 'constraint', 'constraints',
    'pressure', 'pressures', 'volatile', 'volatility', 'impair', 'impairment',
    'litigation', 'lawsuit', 'restructuring', 'layoff', 'layoffs', 'terminate'
}

POSITIVE_WORDS = {
    'growth', 'grew', 'growing', 'increase', 'increased', 'increasing', 'gain',
    'gains', 'strong', 'stronger', 'strength', 'improve', 'improved', 'improving',
    'improvement', 'opportunity', 'opportunities', 'successful', 'success',
    'profit', 'profitable', 'profitability', 'exceed', 'exceeded', 'exceeding',
    'beat', 'outperform', 'outperformed', 'record', 'momentum', 'tailwind',
    'tailwinds', 'accelerate', 'accelerated', 'accelerating', 'robust', 'solid',
    'optimistic', 'confident', 'confidence', 'upside', 'favorable', 'benefit',
    'benefits', 'innovation', 'innovative', 'breakthrough', 'exceptional'
}

HEDGING_WORDS = {
    'may', 'might', 'could', 'possibly', 'perhaps', 'potentially', 'likely',
    'unlikely', 'uncertain', 'expect', 'expecting', 'expected', 'anticipate',
    'anticipated', 'believe', 'believes', 'think', 'thinks', 'hope', 'hopes',
    'estimate', 'estimates', 'approximately', 'around', 'roughly', 'about',
    'probably', 'possibly', 'seemingly', 'apparently', 'somewhat', 'relatively'
}

CERTAINTY_WORDS = {
    'will', 'definitely', 'certainly', 'absolutely', 'clearly', 'obviously',
    'undoubtedly', 'always', 'never', 'must', 'guaranteed', 'proven', 'confirmed',
    'committed', 'commitment', 'confident', 'sure', 'assured', 'certain'
}


def get_api_key() -> str:
    """Load FMP API key"""
    key = os.environ.get('FMP_API_KEY')
    if key:
        return key
    env_paths = [
        Path.home() / '.secure/fmp.env',
        Path('.secure/fmp.env'),
    ]
    for path in env_paths:
        if path.exists():
            with open(path) as f:
                for line in f:
                    if line.startswith('FMP_API_KEY='):
                        return line.split('=', 1)[1].strip()
    raise ValueError("FMP_API_KEY not found")


def fetch_transcript(symbol: str, year: int, quarter: int) -> Optional[Dict]:
    """Fetch earnings call transcript from FMP"""
    api_key = get_api_key()
    url = f"https://financialmodelingprep.com/stable/earning-call-transcript?symbol={symbol}&year={year}&quarter={quarter}&apikey={api_key}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                return data[0]
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
    return None


def extract_qa_section(content: str) -> str:
    """Extract Q&A section from transcript (more revealing than prepared remarks)"""
    # Common Q&A markers
    qa_markers = [
        r'question.and.answer',
        r'q\s*&\s*a',
        r'operator.*question',
        r'your first question',
        r'we will now begin.*question',
    ]
    
    for marker in qa_markers:
        match = re.search(marker, content, re.IGNORECASE)
        if match:
            return content[match.start():]
    
    # Fallback: return second half (usually Q&A)
    return content[len(content)//2:]


def analyze_sentiment(text: str) -> Dict:
    """Analyze sentiment using Loughran-McDonald word lists"""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    word_count = len(words)
    
    if word_count == 0:
        return {'positive': 0, 'negative': 0, 'net': 0}
    
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    
    pos_pct = (pos_count / word_count) * 100
    neg_pct = (neg_count / word_count) * 100
    net = pos_pct - neg_pct
    
    return {
        'positive': round(pos_pct, 2),
        'negative': round(neg_pct, 2),
        'net': round(net, 2),
        'pos_words': pos_count,
        'neg_words': neg_count,
        'total_words': word_count
    }


def analyze_certainty(text: str) -> Dict:
    """Analyze hedging vs certainty language"""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    word_count = len(words)
    
    if word_count == 0:
        return {'hedging': 0, 'certainty': 0, 'ratio': 0}
    
    hedge_count = sum(1 for w in words if w in HEDGING_WORDS)
    cert_count = sum(1 for w in words if w in CERTAINTY_WORDS)
    
    hedge_pct = (hedge_count / word_count) * 100
    cert_pct = (cert_count / word_count) * 100
    
    ratio = cert_pct / hedge_pct if hedge_pct > 0 else float('inf')
    
    return {
        'hedging': round(hedge_pct, 2),
        'certainty': round(cert_pct, 2),
        'ratio': round(ratio, 2),
        'interpretation': 'confident' if ratio > 1.5 else 'cautious' if ratio < 0.7 else 'balanced'
    }


def extract_key_phrases(text: str, n: int = 10) -> List[str]:
    """Extract most frequent meaningful bigrams"""
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Skip common stopwords
    stopwords = {'the', 'and', 'that', 'this', 'for', 'are', 'was', 'were', 'with', 
                 'have', 'has', 'had', 'been', 'will', 'would', 'could', 'should',
                 'from', 'they', 'their', 'what', 'which', 'when', 'where', 'who',
                 'our', 'your', 'you', 'about', 'into', 'also', 'just', 'can', 'more'}
    
    filtered = [w for w in words if w not in stopwords]
    bigrams = [f"{filtered[i]} {filtered[i+1]}" for i in range(len(filtered)-1)]
    
    counter = Counter(bigrams)
    return [phrase for phrase, count in counter.most_common(n)]


def analyze_transcript(symbol: str, year: int, quarter: int) -> Dict:
    """Full transcript analysis"""
    transcript = fetch_transcript(symbol, year, quarter)
    
    if not transcript:
        return {'error': f'No transcript found for {symbol} {year} Q{quarter}'}
    
    content = transcript.get('content', '')
    qa_section = extract_qa_section(content)
    
    # Analyze full transcript
    full_sentiment = analyze_sentiment(content)
    full_certainty = analyze_certainty(content)
    
    # Analyze Q&A section separately
    qa_sentiment = analyze_sentiment(qa_section)
    qa_certainty = analyze_certainty(qa_section)
    
    # Key phrases
    key_phrases = extract_key_phrases(content)
    
    # Management vs Q&A gap (prepared remarks tend to be more positive)
    prepared = content[:len(content) - len(qa_section)]
    prepared_sentiment = analyze_sentiment(prepared)
    sentiment_gap = prepared_sentiment['net'] - qa_sentiment['net']
    
    return {
        'symbol': symbol,
        'period': f'{year} Q{quarter}',
        'date': transcript.get('date'),
        'word_count': full_sentiment['total_words'],
        'overall': {
            'sentiment': full_sentiment,
            'certainty': full_certainty
        },
        'qa_section': {
            'sentiment': qa_sentiment,
            'certainty': qa_certainty
        },
        'sentiment_gap': round(sentiment_gap, 2),
        'gap_interpretation': 'management more optimistic' if sentiment_gap > 0.5 else 'analysts skeptical' if sentiment_gap < -0.5 else 'aligned',
        'key_phrases': key_phrases,
        'signals': generate_signals(full_sentiment, qa_sentiment, full_certainty, sentiment_gap)
    }


def generate_signals(full: Dict, qa: Dict, certainty: Dict, gap: float) -> List[str]:
    """Generate actionable signals from analysis"""
    signals = []
    
    # Strong sentiment signals
    if full['net'] > 1.5:
        signals.append("🟢 Strong positive sentiment overall")
    elif full['net'] < -0.5:
        signals.append("🔴 Negative sentiment detected")
    
    # Q&A reveals more than prepared
    if qa['net'] < full['net'] - 0.5:
        signals.append("⚠️ Q&A tone more cautious than prepared remarks")
    
    # Certainty signals
    if certainty['interpretation'] == 'cautious':
        signals.append("🟡 High hedging language - management uncertainty")
    elif certainty['interpretation'] == 'confident':
        signals.append("🟢 Confident language - high conviction")
    
    # Gap signals
    if gap > 1.0:
        signals.append("⚠️ Large gap: prepared remarks much more positive than Q&A")
    
    return signals if signals else ["📊 Neutral - no strong signals"]


def compare_quarters(symbol: str, quarters: int = 4) -> List[Dict]:
    """Compare sentiment across multiple quarters"""
    import datetime
    
    results = []
    current_year = datetime.datetime.now().year
    current_quarter = (datetime.datetime.now().month - 1) // 3 + 1
    
    for i in range(quarters):
        q = current_quarter - i
        y = current_year
        while q <= 0:
            q += 4
            y -= 1
        
        analysis = analyze_transcript(symbol, y, q)
        if 'error' not in analysis:
            results.append({
                'period': f'{y} Q{q}',
                'net_sentiment': analysis['overall']['sentiment']['net'],
                'qa_sentiment': analysis['qa_section']['sentiment']['net'],
                'certainty': analysis['overall']['certainty']['interpretation']
            })
    
    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 transcript-analyzer.py SYMBOL YEAR QUARTER")
        print("       python3 transcript-analyzer.py SYMBOL --compare")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    
    if len(sys.argv) > 2 and sys.argv[2] == '--compare':
        results = compare_quarters(symbol)
        print(json.dumps(results, indent=2))
    elif len(sys.argv) >= 4:
        year = int(sys.argv[2])
        quarter = int(sys.argv[3].replace('Q', '').replace('q', ''))
        analysis = analyze_transcript(symbol, year, quarter)
        print(json.dumps(analysis, indent=2))
    else:
        print("Usage: python3 transcript-analyzer.py SYMBOL YEAR QUARTER")
        sys.exit(1)


if __name__ == '__main__':
    main()
