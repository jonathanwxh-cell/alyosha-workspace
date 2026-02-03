#!/usr/bin/env python3
"""
L-System Generator
==================

Lindenmayer systems: simple rewriting rules → complex fractal structures.
Demonstrates emergent complexity from minimal rules.

Usage:
    python3 scripts/lsystem.py tree          # Fractal tree
    python3 scripts/lsystem.py koch          # Koch snowflake
    python3 scripts/lsystem.py dragon        # Dragon curve
    python3 scripts/lsystem.py sierpinski    # Sierpinski triangle
    python3 scripts/lsystem.py plant         # Realistic plant
    python3 scripts/lsystem.py custom "F" "F->F+F-F-F+F" 4 90  # Custom L-system

Outputs PNG to creative/lsystems/
"""

import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime

# L-System presets
PRESETS = {
    "tree": {
        "axiom": "X",
        "rules": {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"},
        "angle": 25,
        "iterations": 5,
        "description": "Fractal tree with branching"
    },
    "koch": {
        "axiom": "F",
        "rules": {"F": "F+F-F-F+F"},
        "angle": 90,
        "iterations": 4,
        "description": "Koch curve (square variant)"
    },
    "dragon": {
        "axiom": "FX",
        "rules": {"X": "X+YF+", "Y": "-FX-Y"},
        "angle": 90,
        "iterations": 12,
        "description": "Dragon curve - space-filling fractal"
    },
    "sierpinski": {
        "axiom": "F-G-G",
        "rules": {"F": "F-G+F+G-F", "G": "GG"},
        "angle": 120,
        "iterations": 6,
        "description": "Sierpinski triangle"
    },
    "plant": {
        "axiom": "X",
        "rules": {"X": "F[-X][X]F[-X]+FX", "F": "FF"},
        "angle": 25,
        "iterations": 5,
        "description": "Realistic branching plant"
    },
    "hilbert": {
        "axiom": "A",
        "rules": {"A": "-BF+AFA+FB-", "B": "+AF-BFB-FA+"},
        "angle": 90,
        "iterations": 5,
        "description": "Hilbert curve - space-filling"
    },
    "penrose": {
        "axiom": "[7]++[7]++[7]++[7]++[7]",
        "rules": {"6": "81++91----71[-81----61]++", "7": "+81--91[---61--71]+",
                  "8": "-61++71[+++81++91]-", "9": "--81++++61[+91++++71]--71",
                  "1": ""},
        "angle": 36,
        "iterations": 4,
        "description": "Penrose tiling (P3)"
    }
}


def apply_rules(axiom: str, rules: dict, iterations: int) -> str:
    """Apply L-system rewriting rules iteratively."""
    current = axiom
    for _ in range(iterations):
        next_str = ""
        for char in current:
            next_str += rules.get(char, char)
        current = next_str
    return current


def interpret_lsystem(instructions: str, angle_deg: float, start_pos: tuple = None,
                      start_angle: float = -90, step_size: float = 5) -> list:
    """
    Turtle graphics interpretation of L-system string.
    
    F, G, 1-9: draw forward
    +: turn right
    -: turn left
    [: push state
    ]: pop state
    """
    if start_pos is None:
        start_pos = (0, 0)
    
    x, y = start_pos
    angle = start_angle
    angle_rad = math.radians(angle_deg)
    
    stack = []
    lines = []
    
    for char in instructions:
        if char in 'FG123456789':
            # Draw forward
            new_x = x + step_size * math.cos(math.radians(angle))
            new_y = y + step_size * math.sin(math.radians(angle))
            lines.append(((x, y), (new_x, new_y)))
            x, y = new_x, new_y
        elif char == '+':
            angle += angle_deg
        elif char == '-':
            angle -= angle_deg
        elif char == '[':
            stack.append((x, y, angle))
        elif char == ']':
            if stack:
                x, y, angle = stack.pop()
    
    return lines


def normalize_lines(lines: list, width: int, height: int, margin: int = 50) -> list:
    """Scale and center lines to fit canvas."""
    if not lines:
        return []
    
    # Find bounds
    all_x = [p[0] for line in lines for p in line]
    all_y = [p[1] for line in lines for p in line]
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Calculate scale
    data_width = max_x - min_x or 1
    data_height = max_y - min_y or 1
    
    scale = min((width - 2*margin) / data_width, 
                (height - 2*margin) / data_height)
    
    # Center offset
    offset_x = margin + (width - 2*margin - data_width * scale) / 2
    offset_y = margin + (height - 2*margin - data_height * scale) / 2
    
    # Transform lines
    normalized = []
    for (x1, y1), (x2, y2) in lines:
        nx1 = (x1 - min_x) * scale + offset_x
        ny1 = (y1 - min_y) * scale + offset_y
        nx2 = (x2 - min_x) * scale + offset_x
        ny2 = (y2 - min_y) * scale + offset_y
        normalized.append(((nx1, ny1), (nx2, ny2)))
    
    return normalized


def render_lsystem(lines: list, width: int = 800, height: int = 800,
                   bg_color: str = "#0a0a0a", line_color: str = "#00ff88",
                   title: str = "") -> Image.Image:
    """Render L-system lines to PIL image."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Normalize to fit canvas
    norm_lines = normalize_lines(lines, width, height)
    
    # Draw lines with slight gradient based on depth
    for i, ((x1, y1), (x2, y2)) in enumerate(norm_lines):
        # Color variation based on position in sequence
        progress = i / max(len(norm_lines), 1)
        r = int(0 + progress * 100)
        g = int(255 - progress * 100)
        b = int(136 + progress * 50)
        color = (r, g, b)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    
    # Add title
    if title:
        draw.text((10, 10), title, fill="#ffffff")
    
    # Add stats
    stats = f"Lines: {len(lines):,}"
    draw.text((10, height - 25), stats, fill="#666666")
    
    return img


def generate_lsystem(preset_name: str = "tree", output_dir: str = "creative/lsystems") -> str:
    """Generate L-system and save to file."""
    
    if preset_name not in PRESETS:
        print(f"Unknown preset: {preset_name}")
        print(f"Available: {', '.join(PRESETS.keys())}")
        return None
    
    preset = PRESETS[preset_name]
    
    print(f"🌿 Generating L-System: {preset_name}")
    print(f"   Description: {preset['description']}")
    print(f"   Axiom: {preset['axiom']}")
    print(f"   Rules: {preset['rules']}")
    print(f"   Angle: {preset['angle']}°")
    print(f"   Iterations: {preset['iterations']}")
    
    # Generate string
    result = apply_rules(preset['axiom'], preset['rules'], preset['iterations'])
    print(f"   Generated string length: {len(result):,}")
    
    # Interpret as turtle graphics
    lines = interpret_lsystem(result, preset['angle'])
    print(f"   Line segments: {len(lines):,}")
    
    # Render
    title = f"{preset_name.upper()}: {preset['description']}"
    img = render_lsystem(lines, title=title)
    
    # Save
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{output_dir}/{preset_name}-{timestamp}.png"
    img.save(filename)
    print(f"   ✅ Saved: {filename}")
    
    return filename


def generate_custom(axiom: str, rule_str: str, iterations: int, angle: float,
                    output_dir: str = "creative/lsystems") -> str:
    """Generate custom L-system from command line args."""
    
    # Parse rule string (format: "F->FF,X->F+X")
    rules = {}
    for part in rule_str.split(','):
        if '->' in part:
            key, val = part.split('->')
            rules[key.strip()] = val.strip()
    
    print(f"🌿 Generating Custom L-System")
    print(f"   Axiom: {axiom}")
    print(f"   Rules: {rules}")
    print(f"   Angle: {angle}°")
    print(f"   Iterations: {iterations}")
    
    result = apply_rules(axiom, rules, iterations)
    print(f"   Generated string length: {len(result):,}")
    
    lines = interpret_lsystem(result, angle)
    print(f"   Line segments: {len(lines):,}")
    
    img = render_lsystem(lines, title=f"Custom L-System (iter={iterations})")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{output_dir}/custom-{timestamp}.png"
    img.save(filename)
    print(f"   ✅ Saved: {filename}")
    
    return filename


def generate_all():
    """Generate all presets for showcase."""
    print("🌿 Generating ALL L-System presets...\n")
    files = []
    for name in PRESETS:
        try:
            f = generate_lsystem(name)
            files.append(f)
            print()
        except Exception as e:
            print(f"   ❌ Failed: {e}\n")
    return files


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help']:
        print(__doc__)
        print("\nAvailable presets:")
        for name, preset in PRESETS.items():
            print(f"  {name:12} — {preset['description']}")
        return
    
    if args[0] == 'all':
        generate_all()
    elif args[0] == 'custom' and len(args) >= 5:
        # custom axiom rules iterations angle
        generate_custom(args[1], args[2], int(args[3]), float(args[4]))
    elif args[0] in PRESETS:
        generate_lsystem(args[0])
    else:
        print(f"Unknown command: {args[0]}")
        print("Use --help for usage")


if __name__ == "__main__":
    main()
