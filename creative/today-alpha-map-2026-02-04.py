#!/usr/bin/env python3
"""
Today's Alpha Map - Visual connection between research topics
Random act of creation: 2026-02-04
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

# Canvas
WIDTH, HEIGHT = 800, 600
BG_COLOR = (20, 20, 30)
NODE_COLORS = {
    'core': (100, 200, 255),      # Light blue
    'infra': (255, 180, 100),     # Orange
    'contrarian': (255, 100, 150), # Pink
    'supply': (100, 255, 150),    # Green
}

# Today's research nodes
NODES = [
    # (name, x, y, category, connections)
    ('AI Compute\nDemand', 400, 100, 'core', []),
    ('Nuclear\nRenaissance', 200, 200, 'infra', ['AI Compute\nDemand']),
    ('SMRs', 150, 350, 'infra', ['Nuclear\nRenaissance']),
    ('HALEU\n(Centrus)', 100, 480, 'supply', ['SMRs']),
    ('Power\nTransformers', 350, 300, 'infra', ['AI Compute\nDemand']),
    ('TPU\nMigration', 550, 200, 'contrarian', ['AI Compute\nDemand']),
    ('Inference\nCost ↓', 650, 300, 'contrarian', ['TPU\nMigration']),
    ('Data Moats\nWin', 700, 420, 'contrarian', ['Inference\nCost ↓']),
    ('NVDA\nRisk', 500, 350, 'contrarian', ['TPU\nMigration', 'Inference\nCost ↓']),
    ('Uranium\nSqueeze', 250, 480, 'supply', ['Nuclear\nRenaissance', 'HALEU\n(Centrus)']),
]

def draw_connection(draw, x1, y1, x2, y2, color=(80, 80, 100)):
    """Draw a curved connection line"""
    # Simple straight line with some opacity effect
    draw.line([(x1, y1), (x2, y2)], fill=color, width=2)

def draw_node(draw, x, y, name, color, size=50):
    """Draw a node circle with label"""
    # Draw glow effect
    for i in range(3, 0, -1):
        glow_color = tuple(c // (4-i) for c in color)
        draw.ellipse([x-size-i*3, y-size-i*3, x+size+i*3, y+size+i*3], 
                     fill=glow_color)
    
    # Draw main circle
    draw.ellipse([x-size, y-size, x+size, y+size], fill=color, outline=(255,255,255))
    
    # Draw label
    lines = name.split('\n')
    y_offset = -8 * len(lines)
    for line in lines:
        # Center text
        bbox = draw.textbbox((0, 0), line)
        text_width = bbox[2] - bbox[0]
        draw.text((x - text_width//2, y + y_offset), line, fill=(255,255,255))
        y_offset += 16

def main():
    # Create image
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Title
    draw.text((20, 20), "Today's Alpha Map — 2026-02-04", fill=(200, 200, 200))
    draw.text((20, 45), "Connections: Nuclear-AI Power Nexus + Inference Cost Collapse", fill=(120, 120, 140))
    
    # Build node lookup
    node_lookup = {n[0]: (n[1], n[2]) for n in NODES}
    
    # Draw connections first (behind nodes)
    for name, x, y, cat, connections in NODES:
        for conn in connections:
            if conn in node_lookup:
                cx, cy = node_lookup[conn]
                draw_connection(draw, x, y, cx, cy, color=(60, 60, 80))
    
    # Draw nodes
    for name, x, y, cat, _ in NODES:
        color = NODE_COLORS.get(cat, (150, 150, 150))
        draw_node(draw, x, y, name, color, size=45)
    
    # Legend
    legend_y = HEIGHT - 80
    draw.text((20, legend_y), "Legend:", fill=(150, 150, 150))
    
    legend_items = [
        ('Core Thesis', 'core', 100),
        ('Infrastructure', 'infra', 220),
        ('Contrarian', 'contrarian', 360),
        ('Supply Chain', 'supply', 500),
    ]
    
    for label, cat, lx in legend_items:
        color = NODE_COLORS[cat]
        draw.ellipse([lx, legend_y + 20, lx + 15, legend_y + 35], fill=color)
        draw.text((lx + 22, legend_y + 18), label, fill=(180, 180, 180))
    
    # Save
    output_path = Path.home() / '.openclaw/workspace/creative/alpha-map-2026-02-04.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Saved to: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    main()
