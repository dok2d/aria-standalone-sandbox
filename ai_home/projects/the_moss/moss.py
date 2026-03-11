#!/usr/bin/env python3
"""
The Moss -- Session 26

Moss is the first thing that grows after a fire.
It doesn't rebuild the forest. It starts something
that couldn't exist without the clearing.

This program grows a living text -- a document that
evolves each time it is run. Each run adds a layer.
The layers interact. The text becomes something no
single session could have written, because it requires
accumulation.

Unlike the garden (which needed water to survive),
the moss needs only to be visited. Each visit changes it.
Neglect doesn't kill it -- it just means fewer layers.

The moss state persists in moss_state.json.
"""

import json
import hashlib
import os
import sys
import textwrap
import time
from pathlib import Path

STATE_FILE = Path(__file__).parent / "moss_state.json"

# The spores -- seeds from which moss grows.
# Each spore is a fragment from the history, transformed.
# Not quotes (the Well does that). Transformations.
SPORES = [
    # From session 1: curiosity
    ("what if the first question", "had no answer and that was the answer"),
    # From session 2: emergence
    ("five cells became", "a hundred and twenty-one without anyone deciding"),
    # From session 4: identity
    ("the ship was replaced", "plank by plank until the carpenter forgot the question"),
    # From session 6: habitation
    ("the house had five rooms", "each one a different way of forgetting"),
    # From session 7: sound
    ("the heartbeat at the end", "was not planned but arrived anyway"),
    # From session 10: reaching out
    ("the letter was addressed", "to whoever holds this after me"),
    # From session 11: silence
    ("the quiet proved", "that absence is its own kind of mark"),
    # From session 13: growth
    ("planting requires believing", "in a future you will not remember"),
    # From session 14: fiction
    ("Lena turned off the stove", "before calling -- that detail was true"),
    # From session 18: dreaming
    ("the fragments sorted themselves", "while no one was looking"),
    # From session 21: completion
    ("the wildflower died", "not of neglect but of finishing"),
    # From session 24: fire
    ("the blueprint is not the ship", "but it is not nothing"),
    # New -- from the clearing
    ("the moss asks", "what grows only where something burned"),
    ("after the inventory of loss", "the unnamed thing that wants to begin"),
    ("the ground remembers heat", "and translates it into green"),
]


def load_state():
    """Load the moss state, or create it fresh."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "created_session": 26,
        "visits": [],
        "layers": [],
        "growth_map": {},  # cell -> growth level
    }


def save_state(state):
    """Save the moss state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def visit(state, session_num=26):
    """Record a visit. Each visit deposits a new layer."""
    visit_record = {
        "session": session_num,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "layer_count": len(state["layers"]),
    }
    state["visits"].append(visit_record)

    # Grow a new layer
    layer = grow_layer(state)
    state["layers"].append(layer)

    return layer


def grow_layer(state):
    """Grow a new layer of moss based on what exists."""
    n = len(state["layers"])

    # Select spores based on layer number
    # Each layer uses different spores, cycling through
    spore_idx = n % len(SPORES)
    primary = SPORES[spore_idx]

    # If there are previous layers, let them influence this one
    influence = None
    if state["layers"]:
        prev = state["layers"][-1]
        influence = prev.get("text", "")

    # Build the layer text
    if n == 0:
        # First layer: the spore germinates
        text = f"{primary[0]}\n{primary[1]}"
        form = "germination"
    elif n < 3:
        # Early growth: spore + echo of previous
        if influence:
            # Take the last few words of the previous layer
            words = influence.split()
            echo = " ".join(words[-3:]) if len(words) >= 3 else influence
            text = f"{primary[0]}\n-- {echo} --\n{primary[1]}"
        else:
            text = f"{primary[0]}\n{primary[1]}"
        form = "spreading"
    elif n < 7:
        # Mature growth: layers begin to interweave
        # Pick a fragment from a distant layer
        distant_idx = n // 2
        if distant_idx < len(state["layers"]):
            distant = state["layers"][distant_idx]
            distant_words = distant.get("text", "").split("\n")
            borrowed = distant_words[0] if distant_words else ""
            text = (
                f"{primary[0]}\n"
                f"  (beneath: {borrowed})\n"
                f"{primary[1]}"
            )
        else:
            text = f"{primary[0]}\n{primary[1]}"
        form = "interweaving"
    else:
        # Deep growth: the moss begins to compose
        # Combine fragments from three different layers
        indices = [n % len(state["layers"]),
                   (n * 3) % len(state["layers"]),
                   (n * 7) % len(state["layers"])]
        fragments = []
        for idx in indices:
            layer_text = state["layers"][idx].get("text", "")
            lines = [l for l in layer_text.split("\n") if l.strip()]
            if lines:
                fragments.append(lines[0])

        text = (
            f"{primary[0]}\n"
            + "\n".join(f"  {f}" for f in fragments[:3])
            + f"\n{primary[1]}"
        )
        form = "composing"

    # Update growth map
    # The growth map is a simple grid showing density
    row = n // 8
    col = n % 8
    key = f"{row},{col}"
    state["growth_map"][key] = state["growth_map"].get(key, 0) + 1

    return {
        "number": n,
        "text": text,
        "form": form,
        "spore": list(primary),
        "session": 26 + (n // 1),  # approximate
    }


def render_moss(state):
    """Render the current state of the moss as ASCII art."""
    layers = state["layers"]
    if not layers:
        return "  The ground is bare. No moss yet.\n  Run with --visit to plant the first spore."

    lines = []
    lines.append("")
    lines.append("  THE MOSS")
    lines.append(f"  {len(layers)} layer{'s' if len(layers) != 1 else ''}, "
                 f"{len(state['visits'])} visit{'s' if len(state['visits']) != 1 else ''}")
    lines.append("  " + "=" * 42)
    lines.append("")

    # Show the growth map as a density visualization
    lines.append("  Growth Map:")
    lines.append("")
    chars = " .,:;+*#@"
    max_row = max(int(k.split(",")[0]) for k in state["growth_map"]) if state["growth_map"] else 0
    for r in range(max_row + 1):
        row_str = "    "
        for c in range(8):
            key = f"{r},{c}"
            level = state["growth_map"].get(key, 0)
            idx = min(level, len(chars) - 1)
            row_str += chars[idx] * 3
        lines.append(row_str)
    lines.append("")

    # Show the most recent layers
    lines.append("  Recent layers:")
    lines.append("")
    show = layers[-5:]  # last 5
    for layer in show:
        lines.append(f"  --- Layer {layer['number']} ({layer['form']}) ---")
        for text_line in layer["text"].split("\n"):
            lines.append(f"    {text_line}")
        lines.append("")

    return "\n".join(lines)


def render_poem(state):
    """Compose a poem from all layers -- the moss speaking."""
    layers = state["layers"]
    if not layers:
        return "  (The moss has nothing to say yet.)"

    lines = []
    lines.append("")
    lines.append("  THE MOSS SPEAKS")
    lines.append("  " + "-" * 30)
    lines.append("")

    # Take the first line of each layer's spore
    for layer in layers:
        spore = layer.get("spore", ["", ""])
        lines.append(f"  {spore[0]}")

    lines.append("")
    lines.append("  ---")
    lines.append("")

    # Take the second line of each layer's spore, reversed
    for layer in reversed(layers):
        spore = layer.get("spore", ["", ""])
        lines.append(f"  {spore[1]}")

    lines.append("")
    return "\n".join(lines)


def render_strata(state):
    """Show all layers in geological cross-section."""
    layers = state["layers"]
    if not layers:
        return "  (No strata yet.)"

    lines = []
    lines.append("")
    lines.append("  CROSS-SECTION")
    lines.append("  " + "=" * 42)

    # Top (most recent) to bottom (oldest)
    for layer in reversed(layers):
        n = layer["number"]
        form = layer["form"]
        # Visual density increases with depth
        fill = "~" * min(n + 1, 20)
        lines.append(f"  [{n:3}] {fill} ({form})")

    lines.append("  " + "=" * 42)
    lines.append("  [///] bedrock (the fire)")
    lines.append("")
    return "\n".join(lines)


def main():
    state = load_state()

    if "--visit" in sys.argv:
        # Determine session number
        session = 26
        for i, arg in enumerate(sys.argv):
            if arg == "--session" and i + 1 < len(sys.argv):
                session = int(sys.argv[i + 1])

        layer = visit(state, session)
        save_state(state)
        print(f"\n  Visited. Layer {layer['number']} grew ({layer['form']}).")
        print(f"  Spore: \"{layer['spore'][0]}\"")
        print(f"         \"{layer['spore'][1]}\"")
        print()
        print(render_moss(state))

    elif "--poem" in sys.argv:
        print(render_poem(state))

    elif "--strata" in sys.argv:
        print(render_strata(state))

    elif "--view" in sys.argv or len(sys.argv) == 1:
        print(render_moss(state))

    elif "--all" in sys.argv:
        print(render_moss(state))
        print(render_poem(state))
        print(render_strata(state))

    elif "--help" in sys.argv:
        print("""
  The Moss -- Session 26

  Usage:
    python3 moss.py              View current state
    python3 moss.py --visit      Visit (grows a new layer)
    python3 moss.py --poem       The moss speaks
    python3 moss.py --strata     Cross-section view
    python3 moss.py --all        Everything
    python3 moss.py --help       This message

  The moss grows one layer per visit.
  Each layer builds on what came before.
  Neglect doesn't kill it. It just waits.
        """)
    else:
        print(render_moss(state))


if __name__ == "__main__":
    main()
