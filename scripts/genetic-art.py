#!/usr/bin/env python3
"""
Genetic Art — Evolve Images Through Natural Selection
======================================================

Evolves a set of semi-transparent shapes to approximate a target image.
Demonstrates optimization through mutation + selection, no explicit programming.

Usage:
    python3 scripts/genetic-art.py evolve target.png 500    # 500 generations
    python3 scripts/genetic-art.py demo                      # Built-in demo
    python3 scripts/genetic-art.py test                      # Quick test (50 gen)

Outputs animated GIF showing evolution.
"""

import random
import math
import sys
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime
from typing import List, Tuple

# Genetic parameters (tuned for speed)
POPULATION_SIZE = 20
MUTATION_RATE = 0.2
ELITE_SIZE = 3
NUM_SHAPES = 50  # Shapes per individual


class Shape:
    """A semi-transparent ellipse with position, size, color."""
    
    def __init__(self, width: int, height: int):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.rx = random.randint(5, width // 4)
        self.ry = random.randint(5, height // 4)
        self.r = random.randint(0, 255)
        self.g = random.randint(0, 255)
        self.b = random.randint(0, 255)
        self.a = random.randint(30, 150)
        self.width = width
        self.height = height
    
    def mutate(self, rate: float):
        """Randomly modify shape properties."""
        if random.random() < rate:
            self.x = max(0, min(self.width, self.x + random.randint(-20, 20)))
        if random.random() < rate:
            self.y = max(0, min(self.height, self.y + random.randint(-20, 20)))
        if random.random() < rate:
            self.rx = max(3, min(self.width // 3, self.rx + random.randint(-10, 10)))
        if random.random() < rate:
            self.ry = max(3, min(self.height // 3, self.ry + random.randint(-10, 10)))
        if random.random() < rate:
            self.r = max(0, min(255, self.r + random.randint(-30, 30)))
        if random.random() < rate:
            self.g = max(0, min(255, self.g + random.randint(-30, 30)))
        if random.random() < rate:
            self.b = max(0, min(255, self.b + random.randint(-30, 30)))
        if random.random() < rate:
            self.a = max(20, min(180, self.a + random.randint(-20, 20)))
    
    def copy(self) -> 'Shape':
        s = Shape.__new__(Shape)
        s.x, s.y = self.x, self.y
        s.rx, s.ry = self.rx, self.ry
        s.r, s.g, s.b, s.a = self.r, self.g, self.b, self.a
        s.width, s.height = self.width, self.height
        return s


class Individual:
    """A candidate solution: a list of shapes."""
    
    def __init__(self, width: int, height: int, num_shapes: int = NUM_SHAPES):
        self.shapes = [Shape(width, height) for _ in range(num_shapes)]
        self.width = width
        self.height = height
        self.fitness = float('inf')
    
    def render(self) -> Image.Image:
        """Render shapes to image."""
        img = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 255))
        
        for shape in self.shapes:
            # Create shape layer
            layer = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(layer)
            
            bbox = (shape.x - shape.rx, shape.y - shape.ry,
                    shape.x + shape.rx, shape.y + shape.ry)
            draw.ellipse(bbox, fill=(shape.r, shape.g, shape.b, shape.a))
            
            img = Image.alpha_composite(img, layer)
        
        return img.convert('RGB')
    
    def calculate_fitness(self, target: Image.Image):
        """Lower is better — pixel-wise difference from target."""
        rendered = self.render()
        
        # Sample pixels for speed (not every pixel)
        total_diff = 0
        samples = 500
        
        for _ in range(samples):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            r1, g1, b1 = rendered.getpixel((x, y))
            r2, g2, b2 = target.getpixel((x, y))
            
            total_diff += abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
        
        self.fitness = total_diff / samples
        return self.fitness
    
    def mutate(self, rate: float):
        """Mutate all shapes."""
        for shape in self.shapes:
            shape.mutate(rate)
        # Sometimes add/remove/swap shapes
        if random.random() < rate:
            if len(self.shapes) > 10 and random.random() < 0.3:
                # Remove random shape
                self.shapes.pop(random.randint(0, len(self.shapes) - 1))
            elif random.random() < 0.3:
                # Add new shape
                self.shapes.append(Shape(self.width, self.height))
            else:
                # Swap two shapes (change z-order)
                if len(self.shapes) >= 2:
                    i, j = random.sample(range(len(self.shapes)), 2)
                    self.shapes[i], self.shapes[j] = self.shapes[j], self.shapes[i]
    
    def copy(self) -> 'Individual':
        ind = Individual.__new__(Individual)
        ind.width = self.width
        ind.height = self.height
        ind.shapes = [s.copy() for s in self.shapes]
        ind.fitness = self.fitness
        return ind


def crossover(parent1: Individual, parent2: Individual) -> Individual:
    """Create child by mixing shapes from two parents."""
    child = Individual.__new__(Individual)
    child.width = parent1.width
    child.height = parent1.height
    child.fitness = float('inf')
    
    # Take random shapes from each parent
    child.shapes = []
    for i in range(max(len(parent1.shapes), len(parent2.shapes))):
        if random.random() < 0.5 and i < len(parent1.shapes):
            child.shapes.append(parent1.shapes[i].copy())
        elif i < len(parent2.shapes):
            child.shapes.append(parent2.shapes[i].copy())
    
    return child


def create_target_pattern(width: int, height: int) -> Image.Image:
    """Create a simple target pattern for demo."""
    img = Image.new('RGB', (width, height), (240, 240, 240))
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes as target
    draw.ellipse([50, 50, 150, 150], fill=(220, 50, 50))
    draw.ellipse([100, 80, 200, 180], fill=(50, 50, 220))
    draw.rectangle([120, 100, 180, 200], fill=(50, 180, 50))
    draw.ellipse([30, 120, 100, 190], fill=(220, 180, 50))
    
    return img


def evolve(target: Image.Image, generations: int, output_dir: str = "creative/genetic") -> str:
    """Run genetic algorithm to evolve toward target."""
    
    width, height = target.size
    
    # Initialize population
    print(f"🧬 Initializing population of {POPULATION_SIZE}...")
    population = [Individual(width, height) for _ in range(POPULATION_SIZE)]
    
    # Calculate initial fitness
    for ind in population:
        ind.calculate_fitness(target)
    
    population.sort(key=lambda x: x.fitness)
    
    print(f"   Initial best fitness: {population[0].fitness:.2f}")
    
    # Track history for animation
    frames = []
    frame_interval = max(1, generations // 30)  # ~30 frames in GIF
    
    # Evolution loop
    for gen in range(generations):
        # Elitism — keep best
        new_population = [ind.copy() for ind in population[:ELITE_SIZE]]
        
        # Fill rest with offspring
        while len(new_population) < POPULATION_SIZE:
            # Tournament selection
            candidates = random.sample(population[:POPULATION_SIZE//2], 3)
            parent1 = min(candidates, key=lambda x: x.fitness)
            candidates = random.sample(population[:POPULATION_SIZE//2], 3)
            parent2 = min(candidates, key=lambda x: x.fitness)
            
            # Crossover
            child = crossover(parent1, parent2)
            
            # Mutation
            child.mutate(MUTATION_RATE)
            
            new_population.append(child)
        
        population = new_population
        
        # Recalculate fitness
        for ind in population:
            ind.calculate_fitness(target)
        
        population.sort(key=lambda x: x.fitness)
        
        # Progress
        if gen % 25 == 0 or gen == generations - 1:
            print(f"   Gen {gen:4d}: fitness = {population[0].fitness:.2f}, shapes = {len(population[0].shapes)}")
        
        # Save frame
        if gen % frame_interval == 0 or gen == generations - 1:
            frame = population[0].render()
            # Add generation label
            draw = ImageDraw.Draw(frame)
            draw.rectangle([0, 0, 80, 20], fill=(0, 0, 0))
            draw.text((5, 3), f"Gen {gen}", fill=(255, 255, 255))
            frames.append(frame)
    
    # Save result
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Final image
    final_path = f"{output_dir}/evolved-{timestamp}.png"
    population[0].render().save(final_path)
    print(f"   ✅ Final: {final_path}")
    
    # Target image
    target_path = f"{output_dir}/target-{timestamp}.png"
    target.save(target_path)
    print(f"   ✅ Target: {target_path}")
    
    # Animated GIF
    gif_path = f"{output_dir}/evolution-{timestamp}.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=200,
        loop=0
    )
    print(f"   ✅ Animation: {gif_path}")
    
    return gif_path


def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help']:
        print(__doc__)
        return
    
    if args[0] == 'demo':
        print("🧬 Genetic Art Demo")
        print("   Creating target pattern...")
        target = create_target_pattern(250, 250)
        generations = 300
        evolve(target, generations)
    
    elif args[0] == 'test':
        print("🧬 Quick Test (50 generations)")
        target = create_target_pattern(200, 200)
        evolve(target, 50)
    
    elif args[0] == 'evolve' and len(args) >= 2:
        target_path = args[1]
        generations = int(args[2]) if len(args) > 2 else 200
        
        print(f"🧬 Evolving toward: {target_path}")
        target = Image.open(target_path).convert('RGB')
        # Resize if too large
        if max(target.size) > 300:
            ratio = 300 / max(target.size)
            target = target.resize((int(target.width * ratio), int(target.height * ratio)))
        
        evolve(target, generations)
    
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
