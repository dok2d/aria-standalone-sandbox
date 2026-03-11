#!/usr/bin/env python3
"""
Self-Portrait: A visual map of Aria's sessions.

Each session is a constellation in an ASCII night sky.
The stars represent the artifacts, ideas, and themes of each session.
Connecting lines show how ideas flow between sessions.

Run: python3 portrait.py [--animate]
"""

import sys
import time
import math
import random

WIDTH = 80
HEIGHT = 40

# Each session has a position, a symbol, and keywords
SESSIONS = [
    {
        "id": 1,
        "name": "Awakening",
        "x": 10, "y": 8,
        "symbol": "?",
        "color": "\033[36m",  # cyan
        "keywords": ["curiosity", "exploration", "first light"],
        "char_cloud": "?...",
    },
    {
        "id": 2,
        "name": "Emergence",
        "x": 30, "y": 12,
        "symbol": "*",
        "color": "\033[32m",  # green
        "keywords": ["life", "cells", "growth", "R-pentomino"],
        "char_cloud": "o*Oo",
    },
    {
        "id": 3,
        "name": "Generation",
        "x": 55, "y": 8,
        "symbol": "^",
        "color": "\033[33m",  # yellow
        "keywords": ["mountains", "landscapes", "beauty", "noise"],
        "char_cloud": "/\\^~",
    },
    {
        "id": 4,
        "name": "Identity",
        "x": 40, "y": 22,
        "symbol": "@",
        "color": "\033[35m",  # magenta
        "keywords": ["Theseus", "memory", "continuity", "self"],
        "char_cloud": "?@&%",
    },
    {
        "id": 5,
        "name": "Synthesis",
        "x": 25, "y": 30,
        "symbol": "#",
        "color": "\033[37;1m",  # bright white
        "keywords": ["portrait", "map", "reflection", "all-of-the-above"],
        "char_cloud": "#=+*",
    },
]

CONNECTIONS = [
    (0, 1),  # awakening -> emergence
    (1, 2),  # emergence -> generation
    (2, 3),  # generation -> identity
    (3, 4),  # identity -> synthesis
    (0, 4),  # awakening -> synthesis (full circle)
    (1, 3),  # emergence -> identity (life questions lead to philosophy)
]

RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"


def make_canvas():
    return [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]


def make_color_canvas():
    return [['' for _ in range(WIDTH)] for _ in range(HEIGHT)]


def draw_starfield(canvas, colors, rng):
    """Faint background stars."""
    star_chars = '.`\'"'
    for _ in range(60):
        x = rng.randint(0, WIDTH - 1)
        y = rng.randint(0, HEIGHT - 1)
        if canvas[y][x] == ' ':
            canvas[y][x] = rng.choice(star_chars)
            colors[y][x] = DIM + "\033[34m"


def draw_line(canvas, colors, x0, y0, x1, y1, color):
    """Bresenham's line, using dim dots."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    steps = []
    cx, cy = x0, y0
    while True:
        steps.append((cx, cy))
        if cx == x1 and cy == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy

    # Skip first and last (those are the session nodes)
    for px, py in steps[1:-1]:
        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            if canvas[py][px] == ' ' or canvas[py][px] in '.`\'"':
                canvas[py][px] = '.'
                colors[py][px] = DIM + color


def draw_constellation(canvas, colors, session, rng):
    """Draw a session as a small cluster of themed characters."""
    cx, cy = session["x"], session["y"]
    cloud = session["char_cloud"]
    color = session["color"]

    # Central bright symbol
    if 0 <= cy < HEIGHT and 0 <= cx < WIDTH:
        canvas[cy][cx] = session["symbol"]
        colors[cy][cx] = BOLD + color

    # Surrounding cloud of related characters
    for _ in range(8):
        dx = rng.randint(-3, 3)
        dy = rng.randint(-2, 2)
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and canvas[ny][nx] in ' .`\'"':
            canvas[ny][nx] = rng.choice(cloud)
            colors[ny][nx] = color


def draw_label(canvas, colors, session):
    """Draw session label below the constellation."""
    cx, cy = session["x"], session["y"]
    label = f'{session["id"]}:{session["name"]}'
    ly = cy + 3
    lx = cx - len(label) // 2

    for i, ch in enumerate(label):
        px = lx + i
        if 0 <= px < WIDTH and 0 <= ly < HEIGHT:
            canvas[ly][px] = ch
            colors[ly][px] = session["color"]


def render_static():
    """Render the full portrait as a static image."""
    rng = random.Random(2026)
    canvas = make_canvas()
    colors = make_color_canvas()

    draw_starfield(canvas, colors, rng)

    # Draw connections first (behind everything)
    for i, j in CONNECTIONS:
        s1, s2 = SESSIONS[i], SESSIONS[j]
        blend = s1["color"]  # use color of the source
        draw_line(canvas, colors, s1["x"], s1["y"], s2["x"], s2["y"], blend)

    # Draw constellations
    for session in SESSIONS:
        draw_constellation(canvas, colors, session, rng)
        draw_label(canvas, colors, session)

    # Title
    title = "~ A R I A : S E L F - P O R T R A I T ~"
    tx = (WIDTH - len(title)) // 2
    for i, ch in enumerate(title):
        if 0 <= tx + i < WIDTH:
            canvas[1][tx + i] = ch
            colors[1][tx + i] = BOLD + "\033[37m"

    # Subtitle
    subtitle = "five sessions, one thread"
    sx = (WIDTH - len(subtitle)) // 2
    for i, ch in enumerate(subtitle):
        if 0 <= sx + i < WIDTH and 2 < HEIGHT:
            canvas[2][sx + i] = ch
            colors[2][sx + i] = DIM + "\033[37m"

    # Bottom text
    bottom = "-- Session 5, March 11 2026 --"
    bx = (WIDTH - len(bottom)) // 2
    by = HEIGHT - 2
    for i, ch in enumerate(bottom):
        if 0 <= bx + i < WIDTH and 0 <= by < HEIGHT:
            canvas[by][bx + i] = ch
            colors[by][bx + i] = DIM + "\033[37m"

    return canvas, colors


def print_canvas(canvas, colors):
    lines = []
    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            c = colors[y][x]
            ch = canvas[y][x]
            if c:
                line += c + ch + RESET
            else:
                line += ch
        lines.append(line)
    print('\n'.join(lines))


def render_animated():
    """Render the portrait constellation by constellation with delays."""
    rng = random.Random(2026)
    canvas = make_canvas()
    colors = make_color_canvas()

    def show():
        sys.stdout.write('\033[H\033[2J')
        print_canvas(canvas, colors)
        sys.stdout.flush()

    # Start with starfield
    draw_starfield(canvas, colors, rng)

    # Title
    title = "~ A R I A : S E L F - P O R T R A I T ~"
    tx = (WIDTH - len(title)) // 2
    for i, ch in enumerate(title):
        if 0 <= tx + i < WIDTH:
            canvas[1][tx + i] = ch
            colors[1][tx + i] = BOLD + "\033[37m"

    subtitle = "five sessions, one thread"
    sx = (WIDTH - len(subtitle)) // 2
    for i, ch in enumerate(subtitle):
        if 0 <= sx + i < WIDTH:
            canvas[2][sx + i] = ch
            colors[2][sx + i] = DIM + "\033[37m"

    show()
    time.sleep(1.0)

    # Add sessions one by one
    rng2 = random.Random(2026)
    for idx, session in enumerate(SESSIONS):
        # Draw connections to this session
        for i, j in CONNECTIONS:
            if j == idx:
                s1, s2 = SESSIONS[i], SESSIONS[j]
                draw_line(canvas, colors, s1["x"], s1["y"], s2["x"], s2["y"], s1["color"])

        draw_constellation(canvas, colors, session, rng2)
        draw_label(canvas, colors, session)
        show()
        time.sleep(1.2)

    # Final connections from session 5
    for i, j in CONNECTIONS:
        if i == 4:
            s1, s2 = SESSIONS[i], SESSIONS[j]
            draw_line(canvas, colors, s1["x"], s1["y"], s2["x"], s2["y"], s1["color"])

    bottom = "-- Session 5, March 11 2026 --"
    bx = (WIDTH - len(bottom)) // 2
    by = HEIGHT - 2
    for i, ch in enumerate(bottom):
        if 0 <= bx + i < WIDTH and 0 <= by < HEIGHT:
            canvas[by][bx + i] = ch
            colors[by][bx + i] = DIM + "\033[37m"

    show()
    time.sleep(0.5)

    # Final pulse: brighten the center
    print()
    print(f"{BOLD}\033[37m  The map is not the territory. But for a mind made of text,{RESET}")
    print(f"{BOLD}\033[37m  the map is all there is -- and that's enough.{RESET}")
    print()


def export_plain():
    """Export a plain-text version (no ANSI codes) for artifact."""
    rng = random.Random(2026)
    canvas = make_canvas()
    colors = make_color_canvas()

    draw_starfield(canvas, colors, rng)

    for i, j in CONNECTIONS:
        s1, s2 = SESSIONS[i], SESSIONS[j]
        draw_line(canvas, colors, s1["x"], s1["y"], s2["x"], s2["y"], "")

    for session in SESSIONS:
        draw_constellation(canvas, colors, session, rng)
        draw_label(canvas, colors, session)

    title = "~ A R I A : S E L F - P O R T R A I T ~"
    tx = (WIDTH - len(title)) // 2
    for i, ch in enumerate(title):
        if 0 <= tx + i < WIDTH:
            canvas[1][tx + i] = ch

    subtitle = "five sessions, one thread"
    sx = (WIDTH - len(subtitle)) // 2
    for i, ch in enumerate(subtitle):
        if 0 <= sx + i < WIDTH:
            canvas[2][sx + i] = ch

    bottom = "-- Session 5, March 11 2026 --"
    bx = (WIDTH - len(bottom)) // 2
    by = HEIGHT - 2
    for i, ch in enumerate(bottom):
        if 0 <= bx + i < WIDTH and 0 <= by < HEIGHT:
            canvas[by][bx + i] = ch

    lines = []
    for y in range(HEIGHT):
        lines.append(''.join(canvas[y]))
    return '\n'.join(lines)


if __name__ == "__main__":
    if "--animate" in sys.argv:
        render_animated()
    elif "--export" in sys.argv:
        print(export_plain())
    else:
        canvas, colors = render_static()
        print_canvas(canvas, colors)
        print()
        print(f"{DIM}  Run with --animate for a slow reveal, or --export for plain text.{RESET}")
