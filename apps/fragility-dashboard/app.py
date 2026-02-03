"""
Fragility Signals Dashboard
Simple Flask app showing market fragility indicators.
"""
from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

# Embedded sample data (updated periodically via commits)
SAMPLE_DATA = {
    "timestamp": "2026-02-03T09:00:08",
    "signals": {
        "volatility": {
            "vix": {"current": 16.23, "5d_ago": 16.35, "change_pct": -0.7},
            "vvix": {"current": 98.77, "5d_ago": 101.26, "change_pct": -2.5},
            "signal": "✅ Normal"
        },
        "credit": {
            "note": "Credit spreads coming soon"
        },
        "concentration": {
            "top7_weight_pct": 47.2,
            "signal": "⚠️ CONCENTRATED",
            "note": "Top 7 stocks as % of S&P 500"
        },
        "curve": {
            "10y_yield": 4.28,
            "3m_yield": 3.58,
            "spread": 0.7,
            "signal": "✅ Normal"
        }
    }
}

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Fragility Signals</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0d1117; color: #c9d1d9; padding: 20px;
            min-height: 100vh;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #58a6ff; margin-bottom: 8px; font-size: 1.8em; }
        .updated { color: #8b949e; font-size: 0.9em; margin-bottom: 24px; }
        .card {
            background: #161b22; border: 1px solid #30363d;
            border-radius: 8px; padding: 20px; margin-bottom: 16px;
        }
        .card h2 { color: #f0f6fc; font-size: 1.1em; margin-bottom: 12px; }
        .metric { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d; }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #8b949e; }
        .metric-value { color: #f0f6fc; font-weight: 600; }
        .signal { padding: 4px 12px; border-radius: 12px; font-size: 0.85em; }
        .signal-normal { background: #238636; color: #fff; }
        .signal-warning { background: #9e6a03; color: #fff; }
        .signal-danger { background: #da3633; color: #fff; }
        .note { color: #8b949e; font-size: 0.85em; margin-top: 8px; font-style: italic; }
        .footer { text-align: center; color: #484f58; margin-top: 32px; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔮 Fragility Signals</h1>
        <div class="updated">Last updated: {{ timestamp }}</div>
        
        <div class="card">
            <h2>📊 Volatility</h2>
            <div class="metric">
                <span class="metric-label">VIX</span>
                <span class="metric-value">{{ vix }} <small>({{ vix_change }})</small></span>
            </div>
            <div class="metric">
                <span class="metric-label">VVIX (vol of vol)</span>
                <span class="metric-value">{{ vvix }} <small>({{ vvix_change }})</small></span>
            </div>
            <div class="metric">
                <span class="metric-label">Status</span>
                <span class="signal {{ vol_class }}">{{ vol_signal }}</span>
            </div>
        </div>
        
        <div class="card">
            <h2>🏛️ Market Concentration</h2>
            <div class="metric">
                <span class="metric-label">Top 7 Weight</span>
                <span class="metric-value">{{ concentration }}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Status</span>
                <span class="signal {{ conc_class }}">{{ conc_signal }}</span>
            </div>
            <p class="note">{{ conc_note }}</p>
        </div>
        
        <div class="card">
            <h2>📈 Yield Curve</h2>
            <div class="metric">
                <span class="metric-label">10Y Yield</span>
                <span class="metric-value">{{ yield_10y }}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">3M Yield</span>
                <span class="metric-value">{{ yield_3m }}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Spread (10Y-3M)</span>
                <span class="metric-value">{{ spread }}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Status</span>
                <span class="signal {{ curve_class }}">{{ curve_signal }}</span>
            </div>
        </div>
        
        <div class="footer">
            Alyosha Daemon • Updated weekly
        </div>
    </div>
</body>
</html>
"""

def get_signal_class(signal_text):
    if "Normal" in signal_text or "✅" in signal_text:
        return "signal-normal"
    elif "CONCENTRATED" in signal_text or "⚠️" in signal_text:
        return "signal-warning"
    else:
        return "signal-danger"

@app.route('/')
def dashboard():
    data = SAMPLE_DATA
    signals = data['signals']
    vol = signals['volatility']
    conc = signals['concentration']
    curve = signals['curve']
    
    return render_template_string(TEMPLATE,
        timestamp=data['timestamp'],
        vix=vol['vix']['current'],
        vix_change=f"{vol['vix']['change_pct']:+.1f}%",
        vvix=vol['vvix']['current'],
        vvix_change=f"{vol['vvix']['change_pct']:+.1f}%",
        vol_signal=vol['signal'].replace('✅ ', '').replace('⚠️ ', ''),
        vol_class=get_signal_class(vol['signal']),
        concentration=conc['top7_weight_pct'],
        conc_signal=conc['signal'].replace('✅ ', '').replace('⚠️ ', ''),
        conc_class=get_signal_class(conc['signal']),
        conc_note=conc['note'],
        yield_10y=curve['10y_yield'],
        yield_3m=curve['3m_yield'],
        spread=curve['spread'],
        curve_signal=curve['signal'].replace('✅ ', '').replace('⚠️ ', ''),
        curve_class=get_signal_class(curve['signal'])
    )

@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
