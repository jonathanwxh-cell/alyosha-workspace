#!/usr/bin/env python3
"""
Market Symphony - Multiple stocks as instruments playing together.
Each stock gets a different instrument timbre, creating harmony or dissonance
based on how correlated their movements are.
"""

import sys
import numpy as np
from scipy.io import wavfile
import subprocess
from pathlib import Path

# Different timbres for different stocks (fundamental + harmonic ratios)
INSTRUMENTS = {
    'piano': {'harmonics': [1.0, 0.5, 0.25, 0.125], 'attack': 0.02, 'decay': 0.3},
    'strings': {'harmonics': [1.0, 0.8, 0.6, 0.4, 0.2], 'attack': 0.15, 'decay': 0.15},
    'bells': {'harmonics': [1.0, 0.0, 0.5, 0.0, 0.25], 'attack': 0.01, 'decay': 0.4},
    'brass': {'harmonics': [1.0, 0.7, 0.5, 0.3, 0.2, 0.1], 'attack': 0.05, 'decay': 0.1},
}

# Base frequencies for each stock (different octaves to avoid mud)
STOCK_CONFIG = {
    'NVDA': {'base': 261.63, 'instrument': 'piano', 'pan': -0.3},      # C4, left
    'AMD': {'base': 329.63, 'instrument': 'strings', 'pan': 0.3},      # E4, right
    'TSM': {'base': 392.00, 'instrument': 'bells', 'pan': 0.0},        # G4, center
    'SMCI': {'base': 440.00, 'instrument': 'brass', 'pan': -0.5},      # A4, far left
}

def get_stock_data(symbol: str, days: int = 20):
    """Fetch historical data using yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")
        return hist if not hist.empty else None
    except:
        return None

def generate_instrument_tone(freq: float, duration: float, instrument: dict, 
                             sample_rate: int = 44100, volume: float = 0.5) -> np.ndarray:
    """Generate tone with specific instrument timbre."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Build tone from harmonics
    tone = np.zeros_like(t)
    for i, harmonic_vol in enumerate(instrument['harmonics']):
        tone += np.sin(2 * np.pi * freq * (i + 1) * t) * harmonic_vol
    
    # Normalize
    tone = tone / np.max(np.abs(tone)) if np.max(np.abs(tone)) > 0 else tone
    
    # ADSR envelope
    samples = len(t)
    attack_samples = int(instrument['attack'] * sample_rate)
    decay_samples = int(instrument['decay'] * sample_rate)
    
    envelope = np.ones(samples)
    if attack_samples > 0 and attack_samples < samples:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0 and decay_samples < samples:
        envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
    
    return tone * envelope * volume

def price_to_freq_offset(prices: np.ndarray) -> np.ndarray:
    """Convert price movements to frequency offsets (semitones)."""
    # Calculate daily returns
    returns = np.diff(prices) / prices[:-1]
    # Prepend 0 for first day
    returns = np.concatenate([[0], returns])
    # Map returns to semitones (-12 to +12)
    semitones = np.clip(returns * 100, -12, 12)  # 1% = 1 semitone
    return semitones

def semitone_to_freq(base_freq: float, semitones: float) -> float:
    """Convert semitone offset to frequency."""
    return base_freq * (2 ** (semitones / 12))

def create_symphony(symbols: list, days: int = 20, note_duration: float = 0.4) -> str:
    """Create multi-stock symphony."""
    print(f"🎼 Creating Market Symphony...")
    print(f"   Stocks: {', '.join(symbols)}")
    
    sample_rate = 44100
    
    # Fetch all data
    stock_data = {}
    for symbol in symbols:
        data = get_stock_data(symbol, days)
        if data is not None and len(data) > 1:
            stock_data[symbol] = data['Close'].values
            print(f"   ✓ {symbol}: {len(data)} days")
    
    if not stock_data:
        print("   ❌ No data available")
        return None
    
    # Find common length
    min_len = min(len(v) for v in stock_data.values())
    for symbol in stock_data:
        stock_data[symbol] = stock_data[symbol][:min_len]
    
    # Generate each stock's track
    tracks = {}
    for symbol, prices in stock_data.items():
        config = STOCK_CONFIG.get(symbol, {'base': 440, 'instrument': 'piano', 'pan': 0})
        instrument = INSTRUMENTS[config['instrument']]
        base_freq = config['base']
        
        semitones = price_to_freq_offset(prices)
        
        audio_segments = []
        for i, st in enumerate(semitones):
            freq = semitone_to_freq(base_freq, st)
            # Volume based on absolute movement
            vol = 0.3 + 0.4 * min(abs(st) / 5, 1)
            tone = generate_instrument_tone(freq, note_duration, instrument, 
                                           sample_rate, volume=vol)
            audio_segments.append(tone)
            # Gap
            audio_segments.append(np.zeros(int(sample_rate * 0.1)))
        
        tracks[symbol] = np.concatenate(audio_segments)
    
    # Mix tracks (stereo)
    max_len = max(len(t) for t in tracks.values())
    
    left = np.zeros(max_len)
    right = np.zeros(max_len)
    
    for symbol, track in tracks.items():
        config = STOCK_CONFIG.get(symbol, {'pan': 0})
        pan = config['pan']
        
        # Pad track if needed
        if len(track) < max_len:
            track = np.concatenate([track, np.zeros(max_len - len(track))])
        
        # Pan: -1 = full left, 0 = center, 1 = full right
        left_gain = np.sqrt(0.5 * (1 - pan))
        right_gain = np.sqrt(0.5 * (1 + pan))
        
        left += track * left_gain
        right += track * right_gain
    
    # Normalize and convert to stereo
    stereo = np.column_stack([left, right])
    stereo = stereo / np.max(np.abs(stereo)) if np.max(np.abs(stereo)) > 0 else stereo
    stereo = (stereo * 32767).astype(np.int16)
    
    # Save
    output_dir = Path("/home/ubuntu/.openclaw/workspace/creative/sonification")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    wav_path = output_dir / "market-symphony.wav"
    wavfile.write(str(wav_path), sample_rate, stereo)
    
    # Convert to OGG
    ogg_path = output_dir / "market-symphony.ogg"
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(wav_path),
            '-c:a', 'libvorbis', '-q:a', '5',
            str(ogg_path)
        ], capture_output=True, check=True)
        wav_path.unlink()
        print(f"✅ Created: {ogg_path}")
        return str(ogg_path)
    except:
        print(f"✅ Created: {wav_path}")
        return str(wav_path)

def main():
    symbols = ['NVDA', 'AMD', 'TSM', 'SMCI']
    days = 20
    
    output = create_symphony(symbols, days)
    
    if output:
        print("\n🎵 Interpretation Guide:")
        print("   • NVDA (piano, left) - Lead melody")
        print("   • AMD (strings, right) - Harmony")
        print("   • TSM (bells, center) - Accents")
        print("   • SMCI (brass, far left) - Bass movement")
        print("   • Consonance = correlated movement")
        print("   • Dissonance = divergence")

if __name__ == "__main__":
    main()
