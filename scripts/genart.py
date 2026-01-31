#!/usr/bin/env python3
"""
genart.py - Generative visual art
Creates algorithmic images using mathematical patterns
"""

import numpy as np
from PIL import Image
import colorsys
import sys
import os

def hsv_to_rgb(h, s, v):
    """Convert HSV to RGB (0-255)"""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def create_flow_field(width=800, height=800, scale=0.02, seed=None):
    """Create a flow field visualization"""
    if seed:
        np.random.seed(seed)
    
    img = Image.new('RGB', (width, height), (10, 10, 20))
    pixels = img.load()
    
    # Create noise-based flow field
    num_particles = 5000
    steps_per_particle = 100
    
    for _ in range(num_particles):
        # Random starting position
        x = np.random.uniform(0, width)
        y = np.random.uniform(0, height)
        
        # Random hue for this particle trail
        hue = np.random.uniform(0.5, 0.7)  # Blue-purple range
        
        for step in range(steps_per_particle):
            if 0 <= x < width and 0 <= y < height:
                # Calculate flow angle using Perlin-like noise
                angle = (np.sin(x * scale) * np.cos(y * scale) + 
                        np.sin((x + y) * scale * 0.5)) * np.pi * 2
                
                # Color fades with steps
                brightness = 0.3 + 0.5 * (1 - step / steps_per_particle)
                saturation = 0.6 + 0.4 * np.sin(step * 0.1)
                
                r, g, b = hsv_to_rgb(hue + step * 0.001, saturation, brightness)
                
                # Blend with existing pixel
                px, py = int(x), int(y)
                old = pixels[px, py]
                pixels[px, py] = (
                    min(255, old[0] + r // 4),
                    min(255, old[1] + g // 4),
                    min(255, old[2] + b // 4)
                )
                
                # Move along flow
                x += np.cos(angle) * 1.5
                y += np.sin(angle) * 1.5
            else:
                break
    
    return img

def create_mandelbrot_variant(width=800, height=800, max_iter=100):
    """Create a colorful Mandelbrot-like fractal"""
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Viewport
    x_min, x_max = -2.5, 1.0
    y_min, y_max = -1.5, 1.5
    
    for px in range(width):
        for py in range(height):
            # Map pixel to complex plane
            x0 = x_min + (x_max - x_min) * px / width
            y0 = y_min + (y_max - y_min) * py / height
            
            x, y = 0.0, 0.0
            iteration = 0
            
            while x*x + y*y <= 4 and iteration < max_iter:
                x_new = x*x - y*y + x0
                y = 2*x*y + y0
                x = x_new
                iteration += 1
            
            if iteration == max_iter:
                pixels[px, py] = (0, 0, 0)
            else:
                # Smooth coloring
                hue = (iteration / max_iter) ** 0.5
                sat = 0.8
                val = 0.9 if iteration < max_iter else 0
                pixels[px, py] = hsv_to_rgb(hue * 0.8 + 0.5, sat, val)
    
    return img

def create_wave_interference(width=800, height=800, num_sources=5, seed=None):
    """Create wave interference pattern"""
    if seed:
        np.random.seed(seed)
    
    img = Image.new('RGB', (width, height))
    pixels = img.load()
    
    # Random wave sources
    sources = [(np.random.randint(0, width), np.random.randint(0, height)) 
               for _ in range(num_sources)]
    frequencies = [np.random.uniform(0.02, 0.05) for _ in range(num_sources)]
    phases = [np.random.uniform(0, 2 * np.pi) for _ in range(num_sources)]
    
    for px in range(width):
        for py in range(height):
            # Sum waves from all sources
            wave_sum = 0
            for i, (sx, sy) in enumerate(sources):
                dist = np.sqrt((px - sx)**2 + (py - sy)**2)
                wave_sum += np.sin(dist * frequencies[i] + phases[i])
            
            # Normalize and colorize
            normalized = (wave_sum / num_sources + 1) / 2  # 0 to 1
            
            # Create color gradient
            hue = 0.55 + normalized * 0.15  # Cyan to blue range
            sat = 0.7 + normalized * 0.3
            val = 0.3 + normalized * 0.6
            
            pixels[px, py] = hsv_to_rgb(hue, sat, val)
    
    return img

def create_recursive_circles(width=800, height=800, depth=6):
    """Create recursive circle pattern"""
    from PIL import ImageDraw
    
    img = Image.new('RGB', (width, height), (5, 5, 15))
    draw = ImageDraw.Draw(img)
    
    def draw_circle(cx, cy, radius, d):
        if d <= 0 or radius < 2:
            return
        
        # Color based on depth
        hue = 0.6 + d * 0.05
        sat = 0.7
        val = 0.4 + d * 0.08
        color = hsv_to_rgb(hue, sat, val)
        
        # Draw circle
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                    outline=color, width=1)
        
        # Recursive circles
        new_radius = radius * 0.5
        offsets = [(0, -radius * 0.6), (0, radius * 0.6), 
                   (-radius * 0.6, 0), (radius * 0.6, 0)]
        
        for ox, oy in offsets:
            draw_circle(cx + ox, cy + oy, new_radius, d - 1)
    
    draw_circle(width // 2, height // 2, min(width, height) * 0.4, depth)
    return img

if __name__ == "__main__":
    style = sys.argv[1] if len(sys.argv) > 1 else "flow"
    output = sys.argv[2] if len(sys.argv) > 2 else f"/tmp/genart-{style}.png"
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 2026
    
    print(f"🎨 Generating '{style}' art (seed={seed})...")
    
    if style == "flow":
        img = create_flow_field(seed=seed)
    elif style == "fractal":
        img = create_mandelbrot_variant()
    elif style == "waves":
        img = create_wave_interference(seed=seed)
    elif style == "circles":
        img = create_recursive_circles()
    else:
        print(f"Unknown style: {style}")
        print("Available: flow, fractal, waves, circles")
        sys.exit(1)
    
    img.save(output)
    print(f"✅ Saved: {output}")
    print(f"MEDIA:{output}")
