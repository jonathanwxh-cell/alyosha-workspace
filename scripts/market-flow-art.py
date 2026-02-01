#!/usr/bin/env python3
"""
Market Flow Art Generator
Creates abstract visualizations inspired by market data patterns.
Uses numpy + pillow to generate unique procedural art.
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sys
from datetime import datetime
import os

def create_flow_field(width, height, seed=None):
    """Generate a Perlin-like noise field for flow direction."""
    if seed:
        np.random.seed(seed)
    
    # Create multi-octave noise
    field = np.zeros((height, width, 2))
    for octave in range(4):
        scale = 2 ** octave
        freq = 0.02 * scale
        noise_x = np.random.randn(height // scale + 1, width // scale + 1)
        noise_y = np.random.randn(height // scale + 1, width // scale + 1)
        
        # Upsample
        from PIL import Image as PILImage
        noise_x_img = PILImage.fromarray(noise_x.astype(np.float32))
        noise_y_img = PILImage.fromarray(noise_y.astype(np.float32))
        noise_x_up = np.array(noise_x_img.resize((width, height), PILImage.BILINEAR))
        noise_y_up = np.array(noise_y_img.resize((width, height), PILImage.BILINEAR))
        
        field[:, :, 0] += noise_x_up / scale
        field[:, :, 1] += noise_y_up / scale
    
    # Normalize to angles
    angles = np.arctan2(field[:, :, 1], field[:, :, 0])
    return angles

def trace_particle(start_x, start_y, flow_field, steps=100, step_size=2):
    """Trace a particle through the flow field."""
    height, width = flow_field.shape
    path = [(start_x, start_y)]
    x, y = float(start_x), float(start_y)
    
    for _ in range(steps):
        ix, iy = int(x) % width, int(y) % height
        angle = flow_field[iy, ix]
        
        x += np.cos(angle) * step_size
        y += np.sin(angle) * step_size
        
        if x < 0 or x >= width or y < 0 or y >= height:
            break
        path.append((x, y))
    
    return path

def generate_market_flow_art(width=1200, height=800, seed=None, theme='inference'):
    """Generate abstract art inspired by market flows."""
    
    if seed is None:
        seed = int(datetime.now().timestamp()) % 10000
    
    print(f"Generating with seed: {seed}")
    np.random.seed(seed)
    
    # Create base image
    if theme == 'inference':
        # Cool tech colors: deep blue to purple gradient
        img = Image.new('RGB', (width, height), '#0a0a1a')
        colors = [
            (0, 212, 255, 180),   # Cyan
            (123, 44, 191, 150),  # Purple
            (0, 150, 200, 120),   # Dark cyan
            (180, 80, 220, 100),  # Light purple
        ]
    else:
        img = Image.new('RGB', (width, height), '#1a0a0a')
        colors = [
            (255, 100, 50, 180),
            (200, 50, 100, 150),
        ]
    
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Generate flow field
    flow = create_flow_field(width, height, seed)
    
    # Draw flow lines
    num_particles = 800
    for i in range(num_particles):
        start_x = np.random.randint(0, width)
        start_y = np.random.randint(0, height)
        
        steps = np.random.randint(50, 200)
        path = trace_particle(start_x, start_y, flow, steps=steps)
        
        if len(path) < 10:
            continue
        
        # Choose color based on position
        color = colors[i % len(colors)]
        
        # Draw path with varying width
        for j in range(len(path) - 1):
            x1, y1 = path[j]
            x2, y2 = path[j + 1]
            
            # Fade alpha along path
            alpha = int(color[3] * (1 - j / len(path)))
            line_color = (*color[:3], alpha)
            
            # Varying line width
            width_factor = 1 + np.sin(j * 0.1) * 0.5
            
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=int(2 * width_factor))
    
    # Add some bright nodes (representing data centers / key points)
    num_nodes = 20
    for _ in range(num_nodes):
        nx = np.random.randint(50, width - 50)
        ny = np.random.randint(50, height - 50)
        radius = np.random.randint(3, 8)
        
        # Glowing effect
        for r in range(radius * 3, 0, -1):
            alpha = int(150 * (1 - r / (radius * 3)))
            glow_color = (0, 212, 255, alpha)
            draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=glow_color)
    
    # Apply slight blur for smoothness
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    
    # Add title overlay
    title_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    title_draw = ImageDraw.Draw(title_img)
    
    # Simple text (no custom font needed)
    title_draw.text((30, 30), f"Inference Economy Flow #{seed}", fill=(255, 255, 255, 200))
    title_draw.text((30, height - 50), "Data flows through electrical engineering", fill=(150, 150, 150, 150))
    
    # Composite
    img = Image.alpha_composite(img.convert('RGBA'), title_img)
    
    return img.convert('RGB'), seed

if __name__ == '__main__':
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    output = sys.argv[2] if len(sys.argv) > 2 else None
    
    img, used_seed = generate_market_flow_art(seed=seed)
    
    if output:
        filepath = output
    else:
        os.makedirs('art', exist_ok=True)
        filepath = f"art/market-flow-{used_seed}.png"
    
    img.save(filepath)
    print(f"Saved to: {filepath}")
