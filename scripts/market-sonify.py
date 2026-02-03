#!/usr/bin/env python3
"""
Market Sonification - Turn stock price movements into music.
Maps price changes to musical notes, volume to trading volume.
"""

import sys
import json
import numpy as np
from scipy.io import wavfile
import subprocess
from pathlib import Path

# Musical scale (pentatonic for pleasant sound)
# C major pentatonic: C, D, E, G, A
PENTATONIC = [261.63, 293.66, 329.63, 392.00, 440.00,  # Octave 4
              523.25, 587.33, 659.25, 783.99, 880.00]  # Octave 5

def get_stock_data(symbol: str, days: int = 30):
    """Fetch historical data using yfinance."""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=f"{days}d")
        if hist.empty:
            return None
        return hist
    except Exception as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        return None

def price_to_note(price: float, min_price: float, max_price: float) -> float:
    """Map price to a note frequency."""
    if max_price == min_price:
        return PENTATONIC[len(PENTATONIC) // 2]
    
    # Normalize to 0-1 range
    normalized = (price - min_price) / (max_price - min_price)
    
    # Map to note index
    note_idx = int(normalized * (len(PENTATONIC) - 1))
    note_idx = max(0, min(note_idx, len(PENTATONIC) - 1))
    
    return PENTATONIC[note_idx]

def generate_tone(freq: float, duration: float, sample_rate: int = 44100, 
                  volume: float = 0.5, attack: float = 0.05, decay: float = 0.1) -> np.ndarray:
    """Generate a smooth tone with envelope."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate base tone with harmonics for richer sound
    tone = np.sin(2 * np.pi * freq * t) * 0.6
    tone += np.sin(2 * np.pi * freq * 2 * t) * 0.25  # First harmonic
    tone += np.sin(2 * np.pi * freq * 3 * t) * 0.15  # Second harmonic
    
    # ADSR envelope
    samples = len(t)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    
    envelope = np.ones(samples)
    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    # Decay/release at end
    if decay_samples > 0:
        envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
    
    return tone * envelope * volume

def sonify_stock(symbol: str, days: int = 20, note_duration: float = 0.3) -> str:
    """Create audio from stock data."""
    print(f"🎵 Sonifying {symbol} ({days} days)...")
    
    # Get data
    data = get_stock_data(symbol, days)
    if data is None or len(data) < 2:
        return None
    
    closes = data['Close'].values
    volumes = data['Volume'].values if 'Volume' in data.columns else np.ones(len(closes))
    
    # Normalize volumes for sound amplitude
    vol_min, vol_max = volumes.min(), volumes.max()
    if vol_max > vol_min:
        vol_normalized = 0.3 + 0.7 * (volumes - vol_min) / (vol_max - vol_min)
    else:
        vol_normalized = np.ones(len(volumes)) * 0.5
    
    price_min, price_max = closes.min(), closes.max()
    
    # Generate audio
    sample_rate = 44100
    audio_segments = []
    
    for i, (price, vol) in enumerate(zip(closes, vol_normalized)):
        freq = price_to_note(price, price_min, price_max)
        tone = generate_tone(freq, note_duration, sample_rate, volume=vol)
        audio_segments.append(tone)
        
        # Add small gap between notes
        gap = np.zeros(int(sample_rate * 0.05))
        audio_segments.append(gap)
    
    # Combine all segments
    audio = np.concatenate(audio_segments)
    
    # Normalize to 16-bit range
    audio = audio / np.max(np.abs(audio))
    audio = (audio * 32767).astype(np.int16)
    
    # Save as WAV
    output_dir = Path("/home/ubuntu/.openclaw/workspace/creative/sonification")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    wav_path = output_dir / f"{symbol.lower()}-sonified.wav"
    wavfile.write(str(wav_path), sample_rate, audio)
    
    # Convert to MP3 (better Telegram compatibility than OGG)
    mp3_path = output_dir / f"{symbol.lower()}-sonified.mp3"
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', str(wav_path), 
            '-codec:a', 'libmp3lame', '-qscale:a', '2',
            str(mp3_path)
        ], capture_output=True, check=True)
        wav_path.unlink()  # Remove WAV
        return str(mp3_path)
    except:
        return str(wav_path)  # Return WAV if ffmpeg fails

def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    output = sonify_stock(symbol, days)
    if output:
        print(f"✅ Created: {output}")
        
        # Print stats
        data = get_stock_data(symbol, days)
        if data is not None:
            start = data['Close'].iloc[0]
            end = data['Close'].iloc[-1]
            change = ((end - start) / start) * 100
            print(f"📊 {symbol}: ${start:.2f} → ${end:.2f} ({change:+.1f}%)")
            print(f"🎵 Higher notes = higher prices")
            print(f"🔊 Louder = higher volume days")
    else:
        print("❌ Failed to create audio")
        sys.exit(1)

if __name__ == "__main__":
    main()
