#!/usr/bin/env python3
"""
Stock Analysis Wrapper
======================

Enforces the 7-dimension framework for ALL stock analysis.
Run this instead of ad-hoc analysis to guarantee framework adherence.

Usage:
    python3 scripts/analyze-stock.py TICKER
    python3 scripts/analyze-stock.py NVDA --quarters 6

Output: Structured data from all framework tools, ready for synthesis.
"""

import subprocess
import sys
import json
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw/workspace'
SCRIPTS = WORKSPACE / 'scripts'


def run_tool(cmd, description):
    """Run a tool and return output."""
    print(f"\n{'='*60}")
    print(f"📊 {description}")
    print('='*60)
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=60,
            cwd=WORKSPACE
        )
        if result.returncode == 0:
            print(result.stdout)
            return result.stdout
        else:
            print(f"⚠️  Error: {result.stderr[:200]}")
            return None
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout")
        return None
    except Exception as e:
        print(f"⚠️  Failed: {e}")
        return None


def analyze(ticker, quarters=4):
    """Run full 7-dimension analysis."""
    ticker = ticker.upper()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  STOCK ANALYSIS FRAMEWORK — {ticker:^6}                        ║
║  7-Dimension Qualitative Analysis                            ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    results = {}
    
    # 1. Transcript tone trends (4Q comparison)
    results['tone_trends'] = run_tool(
        ['python3', str(SCRIPTS / 'transcript-compare.py'), ticker, '--quarters', str(quarters)],
        f"Dimension 1-2: Transcript Tone Trends ({quarters}Q)"
    )
    
    # 2. Deep transcript analysis (latest quarter)
    results['deep_analysis'] = run_tool(
        ['python3', str(SCRIPTS / 'deep-analyzer.py'), ticker, '--transcript'],
        "Dimension 1: Deep Transcript Signals (Latest)"
    )
    
    # 3. Insider activity
    results['insider'] = run_tool(
        ['python3', str(SCRIPTS / 'finnhub-client.py'), 'insider', ticker],
        "Dimension 3: Insider Activity"
    )
    
    # 4. Analyst sentiment
    results['analyst'] = run_tool(
        ['python3', str(SCRIPTS / 'finnhub-client.py'), 'recommend', ticker],
        "Dimension 4: Analyst Sentiment"
    )
    
    # 5. Basic quote for context
    results['quote'] = run_tool(
        ['python3', str(SCRIPTS / 'fmp-client.py'), 'snapshot', ticker],
        "Context: Current Price & Fundamentals"
    )
    
    # Summary
    print(f"""
{'='*60}
✅ FRAMEWORK COMPLETE — {ticker}
{'='*60}

Dimensions collected:
  1. ✅ Transcript tone (deep-analyzer)
  2. ✅ Tone trends (transcript-compare, {quarters}Q)
  3. ✅ Insider activity (finnhub)
  4. ✅ Analyst sentiment (finnhub)
  5. ⏳ Industry position (manual — see references/industry-framework.md)
  6. ⏳ Risk/reward scenarios (manual — see references/risk-framework.md)  
  7. ⏳ Second-order effects (manual — see references/second-order.md)

NEXT: Synthesize above data into structured output format.
      See: skills/stock-analysis/SKILL.md for output template.
""")
    
    return results


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nExample: python3 scripts/analyze-stock.py NVDA")
        sys.exit(1)
    
    ticker = sys.argv[1]
    quarters = 4
    
    if '--quarters' in sys.argv:
        idx = sys.argv.index('--quarters')
        if idx + 1 < len(sys.argv):
            quarters = int(sys.argv[idx + 1])
    
    analyze(ticker, quarters)


if __name__ == '__main__':
    main()
