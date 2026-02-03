#!/usr/bin/env python3
"""
Animated L-System Evolution
===========================

Creates animated GIF showing L-system growing through iterations.
Demonstrates emergent complexity from simple rules.

Usage:
    python3 scripts/lsystem-animate.py dragon 12
    python3 scripts/lsystem-animate.py tree 6
"""

import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime

# Import from lsystem.py
from lsystem import PRESETS, apply_rules, interpret_lsystem


def render_frame(lines: list, width: int, height: int, iteration: int,
                 max_iter: int, preset_name: str) -> Image.Image:
    """Render a single frame."""
    img = Image.new('RGB', (width, height), '#0a0a0a')
    draw = ImageDraw.Draw(img)
    
    if not lines:
        draw.text((10, 10), f"{preset_name.upper()} - Iteration {iteration}", fill="#ffffff")
        return img
    
    # Find bounds across ALL iterations (for consistent framing)
    all_x = [p[0] for line in lines for p in line]
    all_y = [p[1] for line in lines for p in line]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Add padding
    margin = 80
    data_width = max_x - min_x or 1
    data_height = max_y - min_y or 1
    
    scale = min((width - 2*margin) / data_width, 
                (height - 2*margin) / data_height)
    
    offset_x = margin + (width - 2*margin - data_width * scale) / 2
    offset_y = margin + (height - 2*margin - data_height * scale) / 2
    
    # Draw lines with color gradient
    for i, ((x1, y1), (x2, y2)) in enumerate(lines):
        nx1 = (x1 - min_x) * scale + offset_x
        ny1 = (y1 - min_y) * scale + offset_y
        nx2 = (x2 - min_x) * scale + offset_x
        ny2 = (y2 - min_y) * scale + offset_y
        
        progress = i / max(len(lines), 1)
        r = int(0 + progress * 100)
        g = int(255 - progress * 100)
        b = int(136 + progress * 50)
        draw.line([(nx1, ny1), (nx2, ny2)], fill=(r, g, b), width=2)
    
    # Title
    draw.text((10, 10), f"{preset_name.upper()} - Iteration {iteration}/{max_iter}", 
              fill="#ffffff")
    draw.text((10, height - 30), f"Lines: {len(lines):,}", fill="#666666")
    
    return img


def create_animation(preset_name: str, max_iterations: int, 
                     output_dir: str = "creative/lsystems") -> str:
    """Generate animated GIF of L-system evolution."""
    
    if preset_name not in PRESETS:
        print(f"Unknown preset: {preset_name}")
        return None
    
    preset = PRESETS[preset_name]
    frames = []
    
    print(f"🎬 Creating animated L-System: {preset_name}")
    print(f"   Iterations: 1 → {max_iterations}")
    
    # Generate frame for each iteration
    for i in range(1, max_iterations + 1):
        result = apply_rules(preset['axiom'], preset['rules'], i)
        lines = interpret_lsystem(result, preset['angle'])
        
        print(f"   Frame {i}: {len(lines):,} lines")
        
        frame = render_frame(lines, 600, 600, i, max_iterations, preset_name)
        frames.append(frame)
    
    # Add pause on final frame
    for _ in range(3):
        frames.append(frames[-1].copy())
    
    # Save as GIF
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{output_dir}/{preset_name}-evolution-{timestamp}.gif"
    
    frames[0].save(
        filename,
        save_all=True,
        append_images=frames[1:],
        duration=500,  # ms per frame
        loop=0
    )
    
    print(f"   ✅ Saved: {filename}")
    print(f"   Frames: {len(frames)}, Duration: {len(frames) * 0.5:.1f}s")
    
    return filename


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help']:
        print(__doc__)
        print("\nAvailable presets:", ', '.join(PRESETS.keys()))
        return
    
    preset = args[0]
    iterations = int(args[1]) if len(args) > 1 else 6
    
    create_animation(preset, iterations)


if __name__ == "__main__":
    main()
