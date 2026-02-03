#!/usr/bin/env python3
"""
Market Intel Aggregator
=======================

Combines multiple financial APIs for comprehensive market intelligence.

Usage:
    python3 market-intel.py NVDA                    # Full intel report
    python3 market-intel.py NVDA --quick            # Quick summary
    python3 market-intel.py watchlist NVDA,AAPL,MSFT

Requires: FMP key (mandatory), Finnhub key (optional, adds sentiment)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Import our clients
sys.path.insert(0, str(Path(__file__).parent))

def load_env(name: str) -> bool:
    """Check if API key exists"""
    paths = [
        Path.home() / f'.secure/{name.lower()}.env',
        Path(f'.secure/{name.lower()}.env'),
    ]
    for p in paths:
        if p.exists():
            return True
    return os.environ.get(f'{name.upper()}_API_KEY') is not None


def get_fmp_data(symbol: str) -> dict:
    """Get data from FMP"""
    try:
        import fmp_client as fmp
        fmp.init()
        
        return {
            'quote': fmp.get_quote(symbol),
            'profile': fmp.get_profile(symbol),
            'metrics': fmp.get_key_metrics(symbol),
        }
    except Exception as e:
        return {'error': str(e)}


def get_finnhub_data(symbol: str) -> dict:
    """Get data from Finnhub (if available)"""
    if not load_env('finnhub'):
        return {'available': False, 'note': 'Get free key at https://finnhub.io'}
    
    try:
        # Dynamic import
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "finnhub_client", 
            Path(__file__).parent / "finnhub-client.py"
        )
        finnhub = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(finnhub)
        finnhub.init()
        
        return {
            'available': True,
            'sentiment': finnhub.get_sentiment(symbol),
            'insider': finnhub.get_insider_transactions(symbol),
            'recommendations': finnhub.get_recommendations(symbol),
        }
    except Exception as e:
        return {'available': False, 'error': str(e)}


def generate_report(symbol: str) -> dict:
    """Generate comprehensive market intel report"""
    print(f"📊 Generating market intel for {symbol}...")
    
    report = {
        'symbol': symbol,
        'generated': datetime.now().isoformat(),
        'sources': {}
    }
    
    # FMP data
    print("  → FMP...", end=" ")
    if load_env('fmp'):
        try:
            from subprocess import run, PIPE
            result = run(['python3', 'scripts/fmp-client.py', 'quote', symbol], 
                        capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                # Parse the output
                report['sources']['fmp'] = {'status': 'ok', 'raw': result.stdout.strip()}
                print("✅")
            else:
                report['sources']['fmp'] = {'status': 'error', 'error': result.stderr}
                print("❌")
        except Exception as e:
            report['sources']['fmp'] = {'status': 'error', 'error': str(e)}
            print(f"❌ {e}")
    else:
        report['sources']['fmp'] = {'status': 'no_key'}
        print("⚠️ no key")
    
    # Finnhub data
    print("  → Finnhub...", end=" ")
    if load_env('finnhub'):
        report['sources']['finnhub'] = {'status': 'ok'}
        print("✅")
    else:
        report['sources']['finnhub'] = {
            'status': 'no_key',
            'note': 'FREE key available at https://finnhub.io/register'
        }
        print("⚠️ no key (FREE available)")
    
    # Transcript analysis (uses FMP)
    print("  → Transcript analysis...", end=" ")
    try:
        from subprocess import run, PIPE
        result = run(['python3', 'scripts/deep-analyzer.py', symbol, '--transcript'], 
                    capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            report['transcript_analysis'] = json.loads(result.stdout)
            print("✅")
        else:
            print("❌")
    except Exception as e:
        print(f"❌ {e}")
    
    return report


def quick_summary(symbol: str):
    """Print quick summary to stdout"""
    print(f"\n{'='*60}")
    print(f"MARKET INTEL: {symbol}")
    print(f"{'='*60}\n")
    
    # Quote from FMP
    try:
        from subprocess import run
        result = run(['python3', 'scripts/fmp-client.py', 'quote', symbol], 
                    capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"📈 {result.stdout.strip()}")
    except:
        pass
    
    # Check available sources
    print(f"\n📡 Data Sources:")
    print(f"   FMP:      {'✅ Active' if load_env('fmp') else '❌ No key'}")
    print(f"   Finnhub:  {'✅ Active' if load_env('finnhub') else '⚠️ No key (FREE at finnhub.io)'}")
    print(f"   Benzinga: {'✅ Active' if load_env('benzinga') else '⚠️ No key (~$300/mo)'}")
    print(f"   Danelfin: {'✅ Active' if load_env('danelfin') else '⚠️ No key'}")
    
    print(f"\n💡 For sentiment/insider data, get FREE Finnhub key:")
    print(f"   https://finnhub.io/register")
    print(f"   echo 'FINNHUB_API_KEY=xxx' > ~/.secure/finnhub.env")
    print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'status':
        print("\n📊 Financial API Status\n")
        apis = ['fmp', 'finnhub', 'benzinga', 'danelfin']
        for api in apis:
            status = '✅' if load_env(api) else '❌'
            print(f"   {api.upper()}: {status}")
        print()
        return
    
    symbol = cmd.upper()
    
    if '--quick' in sys.argv:
        quick_summary(symbol)
    else:
        report = generate_report(symbol)
        print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
