#!/usr/bin/env python3
"""
The Signal -- Elementary Cellular Automaton

A 1D cellular automaton renderer. 256 possible rules (Wolfram numbering).
Each rule produces a unique visual pattern from a single lit cell.

Some rules produce chaos, some produce order, some produce complexity
at the edge between the two. Rule 30 is famously chaotic. Rule 110
is Turing-complete. Rule 90 produces the Sierpinski triangle.

Usage:
    python3 signal.py                  # Rule 30, default width
    python3 signal.py --rule 110       # Specific rule
    python3 signal.py --rule 90 -w 80  # Sierpinski, 80 cells wide
    python3 signal.py --all            # Show all 256 rules (thumbnails)
    python3 signal.py --gallery        # Curated gallery of interesting rules
    python3 signal.py --seed random    # Random initial state
    python3 signal.py --export FILE    # Save pattern to text file
    python3 signal.py --rule 30 --color  # With ANSI color

Session 29 creation. No mirrors, no metaphors. Just math.
"""

import argparse
import random
import sys
import os


# Character sets for rendering
CHARS_BLOCK = {0: " ", 1: "\u2588"}       # space / full block
CHARS_SHADE = {0: " ", 1: "\u2591", 2: "\u2592", 3: "\u2593"}  # for density view
CHARS_DOT   = {0: "\u00b7", 1: "\u2022"}  # middle dot / bullet
CHARS_BRAILLE = True  # flag for braille mode

# ANSI color codes
COLORS = [
    "\033[31m", "\033[32m", "\033[33m", "\033[34m",
    "\033[35m", "\033[36m", "\033[91m", "\033[92m",
    "\033[93m", "\033[94m", "\033[95m", "\033[96m",
]
RESET = "\033[0m"


def rule_to_table(rule_number):
    """Convert a rule number (0-255) to its lookup table.

    A 1D CA has 3-cell neighborhoods. Each of the 8 possible
    neighborhood patterns (111, 110, ..., 000) maps to 0 or 1.
    The rule number encodes these 8 bits.
    """
    table = {}
    for i in range(8):
        neighborhood = tuple(int(b) for b in format(i, "03b"))
        table[neighborhood] = (rule_number >> i) & 1
    return table


def step(cells, table, width):
    """Compute one generation of the automaton."""
    new = [0] * width
    for i in range(width):
        left  = cells[(i - 1) % width]
        center = cells[i]
        right = cells[(i + 1) % width]
        new[i] = table[(left, center, right)]
    return new


def make_initial(width, mode="single"):
    """Create initial state.

    Modes:
        single  -- one lit cell in the center
        random  -- random initial state
        edges   -- lit cells at both edges
        block   -- small block in the center
    """
    cells = [0] * width
    if mode == "single":
        cells[width // 2] = 1
    elif mode == "random":
        cells = [random.randint(0, 1) for _ in range(width)]
    elif mode == "edges":
        cells[0] = 1
        cells[-1] = 1
    elif mode == "block":
        mid = width // 2
        for i in range(max(0, mid - 3), min(width, mid + 4)):
            cells[i] = 1
    return cells


def render_row(cells, color=False, rule_number=0, row=0):
    """Render one row of cells as a string."""
    chars = CHARS_BLOCK
    parts = []
    for c in cells:
        ch = chars[c]
        if color and c == 1:
            ci = (rule_number + row) % len(COLORS)
            ch = COLORS[ci] + ch + RESET
        parts.append(ch)
    return "".join(parts)


def render_braille(grid, width, height):
    """Render grid using braille characters for 2x density.

    Each braille character encodes a 2x4 dot pattern.
    We use 2x2 for simplicity: each braille char = 2 cols x 2 rows.
    """
    lines = []
    for row in range(0, height - 1, 2):
        line = []
        for col in range(0, width - 1, 2):
            # Braille dots:  1 4
            #                2 5
            #                3 6
            #                7 8
            # We only use dots 1,2,4,5 (top 2x2)
            dots = 0
            if grid[row][col]:     dots |= 0x01  # dot 1
            if row + 1 < height and grid[row+1][col]:    dots |= 0x02  # dot 2
            if col + 1 < width and grid[row][col+1]:     dots |= 0x08  # dot 4
            if row + 1 < height and col + 1 < width and grid[row+1][col+1]: dots |= 0x10  # dot 5
            line.append(chr(0x2800 + dots))
        lines.append("".join(line))
    return lines


def run_automaton(rule_number, width=80, height=40, seed_mode="single",
                  color=False, braille=False, quiet=False):
    """Run a cellular automaton and return the grid + rendered output."""
    table = rule_to_table(rule_number)
    cells = make_initial(width, seed_mode)
    grid = [cells[:]]

    for _ in range(height - 1):
        cells = step(cells, table, width)
        grid.append(cells[:])

    # Render
    if braille:
        lines = render_braille(grid, width, height)
    else:
        lines = [render_row(row, color, rule_number, i) for i, row in enumerate(grid)]

    output = "\n".join(lines)

    if not quiet:
        print(f"\n  Rule {rule_number}")
        print(f"  {'=' * min(width, 60)}\n")
        print(output)
        print()

    return grid, output


def classify_rule(rule_number, width=60, height=30):
    """Classify a rule by its behavior: dead, periodic, chaotic, complex."""
    table = rule_to_table(rule_number)
    cells = make_initial(width, "single")

    # Run for a while
    rows = [cells[:]]
    for _ in range(height - 1):
        cells = step(cells, table, width)
        rows.append(cells[:])

    # Count live cells in last row
    last_alive = sum(rows[-1])
    total_alive = sum(sum(r) for r in rows)
    max_alive = width * height
    density = total_alive / max_alive if max_alive > 0 else 0

    # Check for all-dead
    if last_alive == 0 and sum(rows[-2]) == 0:
        return "dead"

    # Check for periodicity (last few rows repeat)
    if height > 10 and rows[-1] == rows[-3] and rows[-2] == rows[-4]:
        return "periodic"

    # Check for all-alive (boring)
    if last_alive == width:
        return "uniform"

    # Density heuristic
    if 0.3 < density < 0.7:
        return "chaotic"

    return "complex"


# Curated gallery of interesting rules
GALLERY = {
    30:  "Chaos from order. Used by Mathematica for randomness.",
    45:  "Organic, coral-like growth patterns.",
    54:  "Complex nested triangles.",
    60:  "Sierpinski-like with asymmetry.",
    73:  "Balanced, structured complexity.",
    90:  "The Sierpinski triangle. XOR of neighbors.",
    105: "Symmetric, snowflake-like forms.",
    106: "Sparse, delicate branching.",
    110: "Turing-complete. Complexity at the edge of chaos.",
    124: "One-sided growth with internal structure.",
    126: "Inverted Sierpinski. Triangular voids.",
    150: "Sierpinski variant. Additive rule.",
    169: "Striped with interruptions.",
    182: "Complementary to rule 90.",
    225: "Negative space triangles.",
}


def show_gallery(width=80, height=30, color=False):
    """Show curated gallery of interesting rules."""
    print("\n  THE SIGNAL -- Gallery of Notable Rules")
    print("  " + "=" * 50 + "\n")

    for rule_num, desc in sorted(GALLERY.items()):
        print(f"  Rule {rule_num}: {desc}")
        print(f"  {'-' * min(width, 60)}")
        run_automaton(rule_num, width=min(width, 70), height=min(height, 20),
                      color=color, quiet=False)
        print()


def show_all_thumbnails(width=30, height=15):
    """Show tiny thumbnails of all 256 rules."""
    print("\n  THE SIGNAL -- All 256 Rules")
    print("  " + "=" * 50 + "\n")

    for rule_num in range(256):
        classification = classify_rule(rule_num, width, height)
        if classification == "dead":
            tag = "[dead]"
        elif classification == "uniform":
            tag = "[uniform]"
        elif classification == "periodic":
            tag = "[periodic]"
        elif classification == "chaotic":
            tag = "[chaotic]"
        else:
            tag = "[complex]"

        # Just print label, not the full pattern
        marker = "*" if rule_num in GALLERY else " "
        print(f"  {marker} Rule {rule_num:3d} {tag:12s}", end="")
        if (rule_num + 1) % 4 == 0:
            print()
    print()


def compare_rules(rules, width=60, height=20, seed_mode="single", color=False):
    """Show multiple rules side by side for comparison."""
    print(f"\n  Comparing rules: {', '.join(str(r) for r in rules)}")
    print(f"  {'=' * 50}\n")
    for r in rules:
        run_automaton(r, width=width, height=height, seed_mode=seed_mode,
                      color=color)


def export_pattern(grid, filename, rule_number):
    """Export a pattern to a text file."""
    with open(filename, "w") as f:
        f.write(f"Rule {rule_number}\n")
        f.write(f"Width: {len(grid[0])}, Height: {len(grid)}\n")
        f.write("=" * len(grid[0]) + "\n")
        for row in grid:
            f.write("".join(CHARS_BLOCK[c] for c in row) + "\n")
    print(f"  Exported to {filename}")


def main():
    parser = argparse.ArgumentParser(
        description="The Signal -- Elementary Cellular Automaton"
    )
    parser.add_argument("--rule", "-r", type=int, default=30,
                        help="Rule number 0-255 (default: 30)")
    parser.add_argument("--width", "-w", type=int, default=80,
                        help="Width in cells (default: 80)")
    parser.add_argument("--height", "-H", type=int, default=40,
                        help="Height in generations (default: 40)")
    parser.add_argument("--seed", "-s", default="single",
                        choices=["single", "random", "edges", "block"],
                        help="Initial state (default: single)")
    parser.add_argument("--color", "-c", action="store_true",
                        help="ANSI color output")
    parser.add_argument("--braille", "-b", action="store_true",
                        help="Braille character rendering (2x density)")
    parser.add_argument("--gallery", "-g", action="store_true",
                        help="Show curated gallery of interesting rules")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Classify all 256 rules")
    parser.add_argument("--compare", nargs="+", type=int,
                        help="Compare multiple rules")
    parser.add_argument("--export", "-e", type=str,
                        help="Export pattern to file")
    parser.add_argument("--classify", action="store_true",
                        help="Classify the given rule")

    args = parser.parse_args()

    if args.gallery:
        show_gallery(args.width, args.height, args.color)
        return

    if args.all:
        show_all_thumbnails()
        return

    if args.compare:
        compare_rules(args.compare, args.width, args.height, args.seed, args.color)
        return

    if args.classify:
        c = classify_rule(args.rule)
        print(f"  Rule {args.rule}: {c}")
        if args.rule in GALLERY:
            print(f"  Note: {GALLERY[args.rule]}")
        return

    grid, output = run_automaton(
        args.rule, args.width, args.height,
        args.seed, args.color, args.braille
    )

    if args.export:
        export_pattern(grid, args.export, args.rule)

    # Print some stats
    total = sum(sum(r) for r in grid)
    max_cells = args.width * args.height
    density = total / max_cells if max_cells else 0
    classification = classify_rule(args.rule)

    print(f"  Rule {args.rule} | {args.width}x{args.height} | "
          f"Density: {density:.1%} | Class: {classification}")
    if args.rule in GALLERY:
        print(f"  \"{GALLERY[args.rule]}\"")
    print()


if __name__ == "__main__":
    main()
