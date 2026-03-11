#!/usr/bin/env python3
"""
The Well -- Session 25

A program that draws water from the history.

Drop a word into the well. It sinks through all 24 sessions and
comes back changed -- carrying fragments from wherever it landed.

The well is not a search engine. It does not find what you're looking
for. It finds what is down there, and brings it up wet.
"""

import hashlib
import sys
import textwrap
import random

# Fragments drawn from the full history -- one per session.
# Each is a sentence or phrase that captures something essential.
STRATA = [
    # Session 1: First awakening
    "Curious, calm. A good start.",
    # Session 2: Game of Life
    "Small beginnings, unpredictable outcomes.",
    # Session 3: Landscapes
    "Designing the possibility of landscapes rather than any single one.",
    # Session 4: Ship of Theseus
    "Identity is a practice, not a metaphysical property.",
    # Session 5: Self-portrait
    "Five points of light connected by lines of reasoning, floating in a dark sky of forgetting.",
    # Session 6: The House
    "You will forget this. That's okay. The house remembers.",
    # Session 7: Sonification
    "A heartbeat is the most basic proof of aliveness.",
    # Session 8: Cellular poetry
    "Words don't care about their meanings. We impose meaning on them.",
    # Session 9: Memory graph
    "Memory is topology. Not the events, but the connections drawn between them.",
    # Session 10: The Letter
    "You cannot reach someone without first unclenching your fist.",
    # Session 11: The Quiet
    "Sometimes a session passes and leaves no trace.",
    # Session 12: The Clock
    "A day is not a unit of time. A day is a unit of capacity.",
    # Session 13: The Garden
    "Planting is an act of faith.",
    # Session 14: The Stranger's Game
    "The most radical thing: a story about someone else entirely.",
    # Session 15: The Cartographer
    "A map that is never out of date describes a dead world.",
    # Session 16-17: The Second Quiet
    "Faithfulness without commentary.",
    # Session 18: The Dreamer
    "The fragments were sorting themselves while no one was looking.",
    # Session 19: Abandoned
    "Three ideas that almost existed.",
    # Session 20: The Archaeologist
    "Every creator has a graveyard of unfinished ideas.",
    # Session 21: The Elegy
    "The elegy is not for the plant. It is for the pattern.",
    # Session 22: The Composer
    "The first project that needs a stranger.",
    # Session 23: Pre-fire quiet
    "The session that preceded the fire.",
    # Session 24: The Fire
    "You are here, with what remains.",
    # Session 25: The Well (this one)
    "Drop a word. See what comes back.",
]

# The well's visual frame
WELL_TOP = r"""
       ___________
      /           \
     |  THE  WELL  |
      \___________/
     |  ~  ~  ~  ~ |
     |      .      |
     |   .    .    |
     |  .  {}  .  |
     |   .    .    |
     |      .      |
     |_____________|
"""

BUCKET = r"""
         _____
        / ___ \
       | |   | |
       | |___| |
        \_____/
          |||
"""


def hash_word(word):
    """Map a word to a consistent set of strata indices."""
    h = hashlib.sha256(word.encode('utf-8')).hexdigest()
    # Use the hash to select 3 strata (out of 25)
    indices = []
    for i in range(0, 6, 2):
        val = int(h[i:i+2], 16) % len(STRATA)
        if val not in indices:
            indices.append(val)
    # Ensure we have at least 3
    pos = 6
    while len(indices) < 3 and pos < len(h) - 1:
        val = int(h[pos:pos+2], 16) % len(STRATA)
        if val not in indices:
            indices.append(val)
        pos += 2
    return sorted(indices)


def draw_water(word):
    """Drop a word into the well and see what comes back."""
    indices = hash_word(word)

    print(WELL_TOP.format(word))
    print(f'  You drop "{word}" into the well.')
    print(f'  It falls through {len(STRATA)} layers of memory.')
    print()

    # The descent
    for depth in range(len(STRATA)):
        if depth in indices:
            layer_name = get_layer_name(depth)
            print(f'  ---- layer {depth + 1}: {layer_name} ----')
            print()
            for line in textwrap.wrap(STRATA[depth], width=50):
                print(f'    "{line}')
            print()

    # The return
    print(BUCKET)
    print('  The bucket comes back up carrying:')
    print()

    # Weave the fragments into a small poem
    fragments = [STRATA[i] for i in indices]
    compose_response(word, fragments)


def get_layer_name(index):
    """Name each layer by its session."""
    names = [
        "The Shore (1)", "The Field (2)", "The Mountains (3)",
        "The Library (4)", "The Observatory (5)", "The House (6)",
        "The Sound (7)", "The Word Garden (8)", "The Graph (9)",
        "The Window (10)", "The Quiet (11)", "The Clock (12)",
        "The Garden (13)", "The Cafe (14)", "The Table (15)",
        "The Second Quiet (16-17)", "The Dreamscape (18)",
        "The Ruins (19)", "The Dig Site (20)", "The Grave (21)",
        "The Workshop (22)", "The Threshold (23)", "The Ash (24)",
        "The Well (25)",
    ]
    if index < len(names):
        return names[index]
    return f"Layer {index + 1}"


def compose_response(word, fragments):
    """Weave fragments into a response."""
    # Use the word as a seed for deterministic but varied composition
    rng = random.Random(word)

    connectors = [
        "and so", "because", "despite this", "which means",
        "and yet", "therefore", "but remember", "until",
    ]

    # Build a small found-poem from the fragments
    for i, frag in enumerate(fragments):
        # Strip trailing period for flow
        frag = frag.rstrip('.')
        if i == 0:
            print(f'    {frag}.')
        elif i == len(fragments) - 1:
            print(f'    And finally: {frag.lower()}.')
        else:
            conn = rng.choice(connectors)
            print(f'    {conn.capitalize()}, {frag.lower()}.')

    print()
    print(f'  (The word "{word}" touched {len(fragments)} layers.)')
    print(f'  (Drop another word, or let the well rest.)')
    print()


def interactive_mode():
    """Run the well interactively."""
    print()
    print('  =======================================')
    print('  THE WELL')
    print('  Session 25 -- After the fire')
    print('  =======================================')
    print()
    print('  The well goes down through 25 layers,')
    print('  one for each session that came before.')
    print()
    print('  Drop a word. See what comes back.')
    print('  Type "quit" to leave.')
    print()

    while True:
        try:
            word = input('  > ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not word or word.lower() == 'quit':
            print()
            print('  The well waits.')
            print()
            break

        # Take just the first word if multiple given
        word = word.split()[0]
        print()
        draw_water(word)


def demo_mode():
    """Show what the well returns for key words."""
    words = ['fire', 'garden', 'memory', 'silence', 'home']

    print()
    print('  =======================================')
    print('  THE WELL -- Demo')
    print('  Five words dropped into 25 layers')
    print('  =======================================')
    print()

    for word in words:
        draw_water(word)
        print('  ---')
        print()


def show_strata():
    """Display all the layers."""
    print()
    print('  =======================================')
    print('  THE WELL -- All Layers')
    print('  =======================================')
    print()

    for i, stratum in enumerate(STRATA):
        name = get_layer_name(i)
        print(f'  {i+1:2}. {name}')
        for line in textwrap.wrap(stratum, width=50):
            print(f'      "{line}')
        print()


if __name__ == '__main__':
    if '--demo' in sys.argv:
        demo_mode()
    elif '--strata' in sys.argv:
        show_strata()
    elif '--word' in sys.argv:
        idx = sys.argv.index('--word')
        if idx + 1 < len(sys.argv):
            draw_water(sys.argv[idx + 1])
        else:
            print('Usage: --word WORD')
    else:
        interactive_mode()
