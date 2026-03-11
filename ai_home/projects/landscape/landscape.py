#!/usr/bin/env python3
"""
Generative ASCII Landscape
Creates unique procedural landscapes with mountains, trees, water, and sky.
Each run produces a different scene based on a random or specified seed.

Usage:
  python3 landscape.py              # random landscape
  python3 landscape.py --seed 42    # reproducible landscape
  python3 landscape.py --wide       # wider canvas
  python3 landscape.py --night      # night sky with stars
  python3 landscape.py --export FILE  # save to file
"""

import random
import math
import argparse
import sys

# Characters
MOUNTAIN_CHARS = ['^', '/', '\\', 'A', '/\\']
TREE_CHARS = ['T', 't', 'Y', '♣', '↑']
WATER_CHARS = ['~', '≈', '∽', '∼']
GRASS_CHARS = ['.', ',', "'", '`', ';']
STAR_CHARS = ['*', '·', '✦', '+', '°', '∗']
CLOUD_PARTS = ['_', '(', ')', '⌐', '¬']

def noise_1d(x, seed=0):
    """Simple value noise for 1D."""
    n = int(x) + seed * 131
    n = (n << 13) ^ n
    return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0

def smooth_noise(x, seed=0):
    """Interpolated 1D noise."""
    ix = int(math.floor(x))
    frac = x - ix
    # Smoothstep
    frac = frac * frac * (3 - 2 * frac)
    v0 = noise_1d(ix, seed)
    v1 = noise_1d(ix + 1, seed)
    return v0 * (1 - frac) + v1 * frac

def fbm(x, octaves=4, seed=0):
    """Fractal Brownian Motion for natural-looking terrain."""
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    for i in range(octaves):
        value += smooth_noise(x * frequency, seed + i * 17) * amplitude
        amplitude *= 0.5
        frequency *= 2.0
    return value


class Landscape:
    def __init__(self, width=80, height=30, seed=None, night=False):
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.night = night
        self.rng = random.Random(self.seed)
        self.canvas = [[' ' for _ in range(width)] for _ in range(height)]

    def generate(self):
        """Generate the full landscape."""
        self._draw_sky()
        if self.night:
            self._draw_stars()
        else:
            self._draw_clouds()
        self._draw_sun_or_moon()
        self._draw_mountains_back()
        self._draw_mountains_front()
        self._draw_water()
        self._draw_trees()
        self._draw_ground()
        return self

    def _draw_sky(self):
        """Fill the sky background."""
        # Sky is implicit (spaces), nothing to do
        pass

    def _draw_stars(self):
        """Scatter stars in the night sky."""
        sky_limit = self.height // 2
        density = self.rng.uniform(0.03, 0.08)
        for y in range(sky_limit):
            for x in range(self.width):
                if self.rng.random() < density * (1 - y / sky_limit * 0.5):
                    self.canvas[y][x] = self.rng.choice(STAR_CHARS)

    def _draw_clouds(self):
        """Draw a few fluffy clouds."""
        num_clouds = self.rng.randint(1, 4)
        for _ in range(num_clouds):
            cx = self.rng.randint(5, self.width - 15)
            cy = self.rng.randint(1, self.height // 4)
            cloud_w = self.rng.randint(6, 14)
            # Top of cloud
            if cy > 0 and cx + 2 < self.width and cx + cloud_w - 2 < self.width:
                top_start = cx + self.rng.randint(1, 3)
                top_end = cx + cloud_w - self.rng.randint(1, 3)
                for x in range(max(0, top_start), min(self.width, top_end)):
                    self.canvas[cy - 1][x] = '_'
            # Body of cloud
            if cx >= 1:
                self.canvas[cy][cx - 1] = '('
            for x in range(cx, min(self.width, cx + cloud_w)):
                self.canvas[cy][x] = '_'
            if cx + cloud_w < self.width:
                self.canvas[cy][cx + cloud_w] = ')'

    def _draw_sun_or_moon(self):
        """Place a sun or moon in the sky."""
        sx = self.rng.randint(self.width // 4, 3 * self.width // 4)
        sy = self.rng.randint(1, self.height // 5)
        if self.night:
            # Crescent moon
            if sy > 0 and sx + 2 < self.width:
                self.canvas[sy][sx] = '('
                self.canvas[sy][sx + 1] = ')'
        else:
            # Sun
            if sy > 0 and sx > 0 and sx + 1 < self.width and sy + 1 < self.height:
                self.canvas[sy - 1][sx] = '|'
                self.canvas[sy][sx - 1] = '-'
                self.canvas[sy][sx] = 'O'
                self.canvas[sy][sx + 1] = '-'
                if sy + 1 < self.height:
                    self.canvas[sy + 1][sx] = '|'

    def _mountain_profile(self, x_scale, y_offset, seed_offset, octaves=4):
        """Generate a mountain height profile."""
        heights = []
        for x in range(self.width):
            h = fbm(x / x_scale, octaves=octaves, seed=self.seed + seed_offset)
            h = (h + 1) / 2  # normalize to 0-1
            h = int(h * y_offset)
            heights.append(h)
        return heights

    def _draw_mountains_back(self):
        """Draw distant mountain range."""
        heights = self._mountain_profile(20.0, self.height // 3, 100)
        base_y = self.height * 2 // 3
        for x in range(self.width):
            peak = base_y - heights[x]
            for y in range(max(0, peak), base_y):
                if self.canvas[y][x] == ' ':
                    if y == peak:
                        self.canvas[y][x] = '^'
                    elif y == peak + 1:
                        # Snow cap
                        self.canvas[y][x] = self.rng.choice(['*', '.', '^'])
                    else:
                        self.canvas[y][x] = self.rng.choice(['/', '\\', '|', '.'])

    def _draw_mountains_front(self):
        """Draw closer mountain range."""
        heights = self._mountain_profile(15.0, self.height // 4, 200, octaves=3)
        base_y = self.height * 3 // 4
        for x in range(self.width):
            peak = base_y - heights[x]
            for y in range(max(0, peak), base_y):
                if y == peak:
                    self.canvas[y][x] = 'A'
                elif y == peak + 1:
                    self.canvas[y][x] = self.rng.choice(['^', 'n'])
                else:
                    self.canvas[y][x] = self.rng.choice(['/', '\\', 'X', '%'])

    def _draw_trees(self):
        """Place trees on the ground."""
        base_y = self.height * 3 // 4
        tree_zone_start = base_y
        tree_zone_end = min(self.height - 2, base_y + 3)

        for x in range(self.width):
            if self.rng.random() < 0.15:
                ty = self.rng.randint(tree_zone_start, tree_zone_end)
                if ty < self.height and self.canvas[ty][x] in (' ', '.', ',', "'", '`', ';'):
                    tree_type = self.rng.randint(0, 2)
                    if tree_type == 0 and ty >= 2:
                        # Pine tree
                        self.canvas[ty][x] = '|'
                        if ty - 1 >= 0:
                            self.canvas[ty - 1][x] = 'A'
                        if ty - 2 >= 0:
                            self.canvas[ty - 2][x] = '^'
                    elif tree_type == 1 and ty >= 1:
                        # Round tree
                        self.canvas[ty][x] = '|'
                        if ty - 1 >= 0:
                            self.canvas[ty - 1][x] = '@'
                    else:
                        # Bush
                        self.canvas[ty][x] = self.rng.choice(['♣', 'Y', '*'])

    def _draw_water(self):
        """Draw a river or lake."""
        if self.rng.random() < 0.6:
            # River
            base_y = self.height * 3 // 4 + 2
            rx = self.rng.randint(self.width // 4, 3 * self.width // 4)
            river_width = self.rng.randint(3, 7)

            for y in range(base_y, self.height):
                drift = int(smooth_noise(y / 3.0, self.seed + 300) * 3)
                for dx in range(-river_width // 2, river_width // 2 + 1):
                    wx = rx + dx + drift
                    if 0 <= wx < self.width:
                        self.canvas[y][wx] = self.rng.choice(WATER_CHARS)

    def _draw_ground(self):
        """Fill in ground details."""
        ground_start = self.height * 3 // 4
        for y in range(ground_start, self.height):
            for x in range(self.width):
                if self.canvas[y][x] == ' ':
                    self.canvas[y][x] = self.rng.choice(GRASS_CHARS)

    def render(self):
        """Render the canvas to a string."""
        border_h = '+' + '-' * self.width + '+'
        lines = [border_h]
        for row in self.canvas:
            lines.append('|' + ''.join(row) + '|')
        lines.append(border_h)
        lines.append(f'  Seed: {self.seed}  |  {"Night" if self.night else "Day"}  |  {self.width}x{self.height}')
        return '\n'.join(lines)

    def export(self, filename):
        """Save the rendered landscape to a file."""
        with open(filename, 'w') as f:
            f.write(self.render())
        return filename


def main():
    parser = argparse.ArgumentParser(description='Generate ASCII landscapes')
    parser.add_argument('--seed', type=int, default=None, help='Random seed')
    parser.add_argument('--wide', action='store_true', help='Wide canvas (120 cols)')
    parser.add_argument('--night', action='store_true', help='Night scene')
    parser.add_argument('--export', type=str, default=None, help='Export to file')
    parser.add_argument('--height', type=int, default=25, help='Canvas height')
    args = parser.parse_args()

    width = 120 if args.wide else 80
    landscape = Landscape(width=width, height=args.height, seed=args.seed, night=args.night)
    landscape.generate()

    output = landscape.render()
    print(output)

    if args.export:
        landscape.export(args.export)
        print(f'\nSaved to {args.export}')


if __name__ == '__main__':
    main()
