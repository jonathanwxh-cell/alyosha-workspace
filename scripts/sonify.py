#!/usr/bin/env python3
"""
sonify.py - Turn data into sound
Attempt #1: Algorithmic music generation
"""

import numpy as np
from scipy.io import wavfile
import sys
import os

def generate_tone(freq, duration, sample_rate=44100, amplitude=0.3):
    """Generate a sine wave tone"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = amplitude * np.sin(2 * np.pi * freq * t)
    # Apply envelope to avoid clicks
    envelope = np.ones_like(tone)
    attack = int(0.01 * sample_rate)
    release = int(0.05 * sample_rate)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    return tone * envelope

def note_to_freq(note):
    """Convert MIDI note number to frequency"""
    return 440 * (2 ** ((note - 69) / 12))

def generate_chord(notes, duration, sample_rate=44100):
    """Generate a chord from multiple notes"""
    chord = np.zeros(int(sample_rate * duration))
    for note in notes:
        chord += generate_tone(note_to_freq(note), duration, sample_rate, 0.2)
    return chord / len(notes)

def create_ambient_piece(duration_seconds=30):
    """Create an ambient generative piece"""
    sample_rate = 44100
    
    # Pentatonic scale in C (peaceful, no dissonance)
    # C4=60, D4=62, E4=64, G4=67, A4=69, C5=72
    scale = [60, 62, 64, 67, 69, 72, 74, 76]
    
    # Initialize output
    total_samples = int(sample_rate * duration_seconds)
    audio = np.zeros(total_samples)
    
    # Layer 1: Slow evolving pad chords
    chord_duration = 4.0
    chords = [
        [60, 64, 67],  # C major
        [62, 67, 71],  # D minor 7 (no 3rd)
        [64, 67, 72],  # E minor
        [60, 64, 69],  # C add 9
    ]
    
    pos = 0
    chord_idx = 0
    while pos < total_samples:
        chord = chords[chord_idx % len(chords)]
        chord_audio = generate_chord(chord, chord_duration, sample_rate)
        end_pos = min(pos + len(chord_audio), total_samples)
        audio[pos:end_pos] += chord_audio[:end_pos-pos] * 0.4
        pos += int(chord_duration * sample_rate * 0.75)  # Overlap
        chord_idx += 1
    
    # Layer 2: Random melodic notes
    np.random.seed(42)  # Reproducible randomness
    num_notes = int(duration_seconds * 1.5)  # ~1.5 notes per second
    
    for _ in range(num_notes):
        note = np.random.choice(scale)
        note_duration = np.random.uniform(0.3, 1.2)
        start_time = np.random.uniform(0, duration_seconds - note_duration)
        start_sample = int(start_time * sample_rate)
        
        tone = generate_tone(note_to_freq(note), note_duration, sample_rate, 0.25)
        end_sample = min(start_sample + len(tone), total_samples)
        audio[start_sample:end_sample] += tone[:end_sample-start_sample]
    
    # Layer 3: High sparkles
    for _ in range(int(duration_seconds * 0.5)):
        note = np.random.choice(scale) + 12  # Octave up
        note_duration = np.random.uniform(0.1, 0.3)
        start_time = np.random.uniform(0, duration_seconds - note_duration)
        start_sample = int(start_time * sample_rate)
        
        tone = generate_tone(note_to_freq(note), note_duration, sample_rate, 0.15)
        end_sample = min(start_sample + len(tone), total_samples)
        audio[start_sample:end_sample] += tone[:end_sample-start_sample]
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    return audio, sample_rate

def data_to_melody(data, duration_per_point=0.2):
    """Convert a list of numbers to a melody"""
    sample_rate = 44100
    
    # Normalize data to MIDI note range (C3 to C6)
    data = np.array(data)
    min_val, max_val = data.min(), data.max()
    if max_val == min_val:
        normalized = np.full_like(data, 0.5)
    else:
        normalized = (data - min_val) / (max_val - min_val)
    
    # Map to pentatonic scale
    scale = [48, 50, 52, 55, 57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84]
    notes = [scale[int(v * (len(scale) - 1))] for v in normalized]
    
    # Generate audio
    audio = np.array([])
    for note in notes:
        tone = generate_tone(note_to_freq(note), duration_per_point, sample_rate)
        audio = np.concatenate([audio, tone])
    
    return audio, sample_rate

if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/generative-ambient.wav"
    
    print("🎵 Generating ambient piece...")
    audio, sr = create_ambient_piece(20)  # 20 seconds
    
    # Convert to 16-bit PCM
    audio_int = (audio * 32767).astype(np.int16)
    
    wavfile.write(output_path, sr, audio_int)
    print(f"✅ Saved to: {output_path}")
    print(f"MEDIA:{output_path}")
