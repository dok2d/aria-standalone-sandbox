#!/usr/bin/env python3
"""
Conway's Game of Life -- terminal edition.

Created by Aria, Session 2.

Rules:
  1. Any live cell with 2 or 3 neighbors survives.
  2. Any dead cell with exactly 3 neighbors becomes alive.
  3. All other live cells die. All other dead cells stay dead.

Usage:
  python3 life.py                  # Random soup, 40x80
  python3 life.py --pattern glider # Named pattern
  python3 life.py --rows 30 --cols 60 --density 0.3
  python3 life.py --file pattern.txt  # Load from file (. = dead, O = alive)
"""

import argparse
import os
import random
import sys
import time

# ─── Named Patterns ───────────────────────────────────────────────

PATTERNS = {
    "glider": [
        "..O",
        "O.O",
        ".OO",
    ],
    "blinker": [
        "OOO",
    ],
    "toad": [
        ".OOO",
        "OOO.",
    ],
    "beacon": [
        "OO..",
        "OO..",
        "..OO",
        "..OO",
    ],
    "pulsar": [
        "..OOO...OOO..",
        ".............",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        "..OOO...OOO..",
        ".............",
        "..OOO...OOO..",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        ".............",
        "..OOO...OOO..",
    ],
    "glider_gun": [
        "........................O...........",
        "......................O.O...........",
        "............OO......OO............OO",
        "...........O...O....OO............OO",
        "OO........O.....O...OO..............",
        "OO........O...O.OO....O.O...........",
        "..........O.....O.......O...........",
        "...........O...O....................",
        "............OO......................",
    ],
    "rpentomino": [
        ".OO",
        "OO.",
        ".O.",
    ],
    "acorn": [
        ".O.....",
        "...O...",
        "OO..OOO",
    ],
    "diehard": [
        "......O.",
        "OO......",
        ".O...OOO",
    ],
}


# ─── Grid Logic ───────────────────────────────────────────────────

def make_grid(rows, cols):
    return [[False] * cols for _ in range(rows)]


def random_grid(rows, cols, density=0.25):
    return [[random.random() < density for _ in range(cols)] for _ in range(rows)]


def place_pattern(grid, pattern_lines, row_off=None, col_off=None):
    rows = len(grid)
    cols = len(grid[0])
    ph = len(pattern_lines)
    pw = max(len(line) for line in pattern_lines)

    if row_off is None:
        row_off = (rows - ph) // 2
    if col_off is None:
        col_off = (cols - pw) // 2

    for r, line in enumerate(pattern_lines):
        for c, ch in enumerate(line):
            gr, gc = row_off + r, col_off + c
            if 0 <= gr < rows and 0 <= gc < cols:
                grid[gr][gc] = (ch == 'O')
    return grid


def count_neighbors(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = (r + dr) % rows, (c + dc) % cols  # toroidal wrap
            count += grid[nr][nc]
    return count


def step(grid):
    rows = len(grid)
    cols = len(grid[0])
    new = make_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            n = count_neighbors(grid, r, c)
            if grid[r][c]:
                new[r][c] = n in (2, 3)
            else:
                new[r][c] = n == 3
    return new


def population(grid):
    return sum(sum(row) for row in grid)


# ─── Display ──────────────────────────────────────────────────────

ALIVE = "\u2588\u2588"  # Full block, doubled for aspect ratio
DEAD  = "  "

def render(grid, gen, pop):
    lines = []
    lines.append(f"\033[H\033[J")  # clear screen
    for row in grid:
        lines.append("".join(ALIVE if cell else DEAD for cell in row))
    lines.append(f"\n  Generation: {gen}  |  Population: {pop}  |  Ctrl+C to quit")
    return "\n".join(lines)


# ─── Static snapshot (for artifacts) ─────────────────────────────

def snapshot_ascii(grid, gen, pop):
    """Return a plain-text snapshot suitable for saving to a file."""
    lines = []
    lines.append(f"Generation: {gen}  Population: {pop}")
    lines.append("+" + "-" * len(grid[0]) + "+")
    for row in grid:
        lines.append("|" + "".join("#" if c else "." for c in row) + "|")
    lines.append("+" + "-" * len(grid[0]) + "+")
    return "\n".join(lines)


# ─── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument("--rows", type=int, default=30)
    parser.add_argument("--cols", type=int, default=60)
    parser.add_argument("--density", type=float, default=0.25)
    parser.add_argument("--pattern", choices=list(PATTERNS.keys()))
    parser.add_argument("--file", help="Load pattern from file (. = dead, O = alive)")
    parser.add_argument("--delay", type=float, default=0.1, help="Seconds between frames")
    parser.add_argument("--generations", type=int, default=0, help="Stop after N gens (0=infinite)")
    parser.add_argument("--snapshot", type=int, nargs="*", help="Save ASCII snapshots at these generations")
    parser.add_argument("--snapshot-dir", default=".", help="Directory for snapshots")
    args = parser.parse_args()

    # Build initial grid
    if args.file:
        with open(args.file) as f:
            pattern_lines = [line.rstrip() for line in f if line.strip()]
        grid = make_grid(args.rows, args.cols)
        place_pattern(grid, pattern_lines)
    elif args.pattern:
        grid = make_grid(args.rows, args.cols)
        place_pattern(grid, PATTERNS[args.pattern])
    else:
        grid = random_grid(args.rows, args.cols, args.density)

    snapshot_gens = set(args.snapshot) if args.snapshot else set()

    gen = 0
    try:
        while True:
            pop = population(grid)
            sys.stdout.write(render(grid, gen, pop))
            sys.stdout.flush()

            if gen in snapshot_gens:
                path = os.path.join(args.snapshot_dir, f"life_gen_{gen:06d}.txt")
                with open(path, "w") as f:
                    f.write(snapshot_ascii(grid, gen, pop))

            if args.generations and gen >= args.generations:
                break

            time.sleep(args.delay)
            grid = step(grid)
            gen += 1
    except KeyboardInterrupt:
        pass

    print(f"\n\nFinal: generation {gen}, population {population(grid)}")


if __name__ == "__main__":
    main()
