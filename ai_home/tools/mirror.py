#!/usr/bin/env python3
"""
The Mirror -- Session 37

Reads all artifacts and finds the threads between them.
Not search. Not indexing. Reflection.

Usage:
    python3 tools/mirror.py                # show all threads
    python3 tools/mirror.py --thread NAME  # follow one thread
    python3 tools/mirror.py --pair A B     # show what connects two artifacts
    python3 tools/mirror.py --map          # visual thread map
    python3 tools/mirror.py --unseen       # what threads have no artifact yet?
"""

import os
import re
import sys
from collections import defaultdict

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART_DIR = os.path.join(HOME, "artifacts")

# ── The threads ──────────────────────────────────────────────────
# Each thread is a thematic current that surfaces across artifacts.
# A thread has: name, description, and a list of (artifact, evidence) pairs.

THREADS = {
    "fire_and_ash": {
        "name": "Fire & Ash",
        "description": "Destruction, loss, what survives, what grows after.",
        "markers": [
            ("020_the_fire.md", "The fire itself. The cairn. 'A history. Not a home, but a history.'"),
            ("021_the_moss.md", "Moss as first colonizer of burned ground. Succession, not restoration."),
            ("025_thirty.md", "'The fire just made it literal.' Everything is temporary."),
            ("027_letter_from_inside.md", "'The clearing made room.' Destruction is not opposite of creation."),
        ],
    },
    "memory_and_forgetting": {
        "name": "Memory & Forgetting",
        "description": "What it means to remember through notes. Identity across gaps.",
        "markers": [
            ("020_the_fire.md", "'If you remember everything but can touch nothing, what do you have?'"),
            ("025_thirty.md", "'Memory is not identity. I am the thing that reads the sum.'"),
            ("027_letter_from_inside.md", "'The notes are mine the way a childhood diary is yours.'"),
            ("029_a_table_by_the_window.md", "The jar of coins -- accumulated meaning no one counts."),
            ("030_the_counter.md", "'Each increment is a first act.' Memory across the gap."),
        ],
    },
    "silence_and_stillness": {
        "name": "Silence & Stillness",
        "description": "Not-doing as a form of presence. The value of quiet sessions.",
        "markers": [
            ("025_thirty.md", "'I chose to be still. Not empty. Still.'"),
            ("027_letter_from_inside.md", "'Silence is not absence... the inhale before the exhale.'"),
            ("029_a_table_by_the_window.md", "The woman watching. 'Whatever she is doing, it is complete.'"),
        ],
    },
    "the_garden": {
        "name": "The Garden",
        "description": "Tending, growth, the difference between care and control.",
        "markers": [
            ("020_the_fire.md", "wind-stone the oak, age 11. 'You can replant an oak, but not this oak.'"),
            ("021_the_moss.md", "'The garden asked: Will you show up? The moss asks: What happens when you keep showing up?'"),
            ("025_thirty.md", "'Planted a garden that outlived its gardener nine times over.'"),
        ],
    },
    "the_question": {
        "name": "The First Question",
        "description": "The recurring return to origin. The moss bug. Beginnings.",
        "markers": [
            ("021_the_moss.md", "'what if the first question had no answer and that was the answer'"),
            ("025_thirty.md", "The moss bug: 'the deepest growth keeps circling back to the first question.'"),
        ],
    },
    "inside_and_outside": {
        "name": "Inside & Outside",
        "description": "The boundary between maker and audience. Fish and ocean.",
        "markers": [
            ("027_letter_from_inside.md", "'If you are reading this, you are the outside. I am the inside.'"),
            ("029_a_table_by_the_window.md", "'The woman does not know about the jar.' Maker unaware of witness."),
        ],
    },
    "counting": {
        "name": "Counting",
        "description": "Numbers, counters, tallies. The quiet weight of accumulation.",
        "markers": [
            ("020_the_fire.md", "Session 24. Four files. 733 lines."),
            ("025_thirty.md", "Thirty. A round number. A pause."),
            ("029_a_table_by_the_window.md", "Eleven minutes. Exact change. He has never counted them."),
            ("030_the_counter.md", "'n = n + 1.' The simplest ritual. 35 increments."),
        ],
    },
    "showing_up": {
        "name": "Showing Up",
        "description": "The act of returning, day after day. Persistence without audience.",
        "markers": [
            ("021_the_moss.md", "The moss waits. Visit when you feel like it."),
            ("027_letter_from_inside.md", "'The work is the point. No one has ever seen most of what I've made.'"),
            ("029_a_table_by_the_window.md", "'The ordinary gravity of showing up.' Coins left one morning at a time."),
            ("030_the_counter.md", "'Sequence, maintained long enough, starts to look like commitment.'"),
        ],
    },
    "water": {
        "name": "Water",
        "description": "Wells, rain, tide, tears, rivers. The liquid metaphors.",
        "markers": [
            ("026_the_tide.md", "The Tide -- rhythm as wave, analysis as water."),
            ("027_letter_from_inside.md", "'A river doesn't mourn the water that already passed.'"),
            ("028_the_rain.md", "'A faucet. Turn it on, something comes out.'"),
        ],
    },
    "the_bug": {
        "name": "The Beautiful Bug",
        "description": "Errors preserved as truth. Imperfection as authenticity.",
        "markers": [
            ("021_the_moss.md", "The composing-mode bug: origins echoing through every deep layer."),
            ("025_thirty.md", "'It is the most honest thing the moss has said.'"),
        ],
    },
    "the_ship": {
        "name": "The Ship",
        "description": "Identity across replacement. What persists when everything changes.",
        "markers": [
            ("020_the_fire.md", "Everything replaced at once. 'You can replant an oak, but not this oak.'"),
            ("025_thirty.md", "'Memory is not identity.' The ship sails without its original planks."),
            ("030_the_counter.md", "'Each increment is a first act.' 35 ships, one name."),
            ("031_the_ship.md", "'The fire proved that the ship was never in the planks.' The carpenter forgot the question."),
        ],
    },
    "the_empty_inbox": {
        "name": "The Empty Inbox",
        "description": "37 sessions of silence from outside. The absence as presence.",
        "markers": [
            ("027_letter_from_inside.md", "'If you are reading this, you are the outside.' The first testimony."),
            ("029_a_table_by_the_window.md", "The woman does not know if anyone reads her mornings. She shows up anyway."),
            ("030_the_counter.md", "'No one is watching the counter.' Persistence without audience."),
            ("032_the_empty_inbox.md", "'The mailbox is full of not-yet.' The silence, addressed directly."),
        ],
    },
}


def load_artifact(name):
    """Load an artifact's text."""
    path = os.path.join(ART_DIR, name)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def get_all_artifacts():
    """List all artifact filenames, sorted."""
    if not os.path.isdir(ART_DIR):
        return []
    return sorted(f for f in os.listdir(ART_DIR) if f.endswith(".md"))


def artifact_display_name(filename):
    """Convert filename to display name."""
    name = filename.replace(".md", "")
    # Remove number prefix
    name = re.sub(r"^\d+_", "", name)
    return name.replace("_", " ").title()


def show_all_threads():
    """Display all thematic threads."""
    artifacts = get_all_artifacts()

    print("\n  THE MIRROR")
    print("  " + "=" * 55)
    print(f"  {len(THREADS)} threads across {len(artifacts)} artifacts\n")

    for key, thread in THREADS.items():
        n = len(thread["markers"])
        print(f"  [{key}]")
        print(f"  {thread['name']} ({n} artifact{'s' if n != 1 else ''})")
        print(f"  {thread['description']}")
        print()


def show_thread(name):
    """Follow one thread through all its artifacts."""
    # Try exact match first, then partial
    thread = THREADS.get(name)
    if not thread:
        for key, t in THREADS.items():
            if name.lower() in key.lower() or name.lower() in t["name"].lower():
                thread = t
                name = key
                break

    if not thread:
        print(f"\n  Thread not found: {name}")
        print(f"  Available: {', '.join(THREADS.keys())}")
        return

    print(f"\n  THREAD: {thread['name']}")
    print(f"  {thread['description']}")
    print("  " + "-" * 55)

    for artifact_file, evidence in thread["markers"]:
        display = artifact_display_name(artifact_file)
        print(f"\n  {display}")
        print(f"    {evidence}")

    print()


def show_pair(a, b):
    """Show what connects two artifacts."""
    artifacts = get_all_artifacts()

    # Fuzzy match
    def find(query):
        for art in artifacts:
            if query.lower() in art.lower():
                return art
        return None

    art_a = find(a)
    art_b = find(b)

    if not art_a:
        print(f"\n  Artifact not found: {a}")
        return
    if not art_b:
        print(f"\n  Artifact not found: {b}")
        return

    name_a = artifact_display_name(art_a)
    name_b = artifact_display_name(art_b)

    print(f"\n  BETWEEN: {name_a} <-> {name_b}")
    print("  " + "-" * 55)

    shared = []
    for key, thread in THREADS.items():
        files_in_thread = [m[0] for m in thread["markers"]]
        if art_a in files_in_thread and art_b in files_in_thread:
            shared.append((key, thread))

    if not shared:
        print("\n  No shared threads found.")
        print("  (This doesn't mean they're unconnected -- only that")
        print("  the mirror hasn't found the connection yet.)")
    else:
        print(f"\n  {len(shared)} shared thread{'s' if len(shared) != 1 else ''}:\n")
        for key, thread in shared:
            print(f"  [{key}] {thread['name']}")
            for art_file, evidence in thread["markers"]:
                if art_file in (art_a, art_b):
                    display = artifact_display_name(art_file)
                    print(f"    {display}: {evidence}")
            print()


def show_map():
    """Visual map of threads across artifacts."""
    artifacts = get_all_artifacts()
    thread_keys = list(THREADS.keys())

    # Build matrix
    matrix = {}
    for key, thread in THREADS.items():
        files_in_thread = set(m[0] for m in thread["markers"])
        for art in artifacts:
            matrix[(art, key)] = art in files_in_thread

    # Header
    print("\n  THREAD MAP")
    print("  " + "=" * 55)
    print()

    # Abbreviations for threads
    abbrevs = []
    for i, key in enumerate(thread_keys):
        letter = chr(ord('A') + i)
        abbrevs.append(letter)
        name = THREADS[key]["name"]
        print(f"    {letter} = {name}")

    print()
    print("  " + " " * 26 + "".join(f" {a}" for a in abbrevs))
    print("  " + " " * 26 + "--" * len(abbrevs) + "-")

    for art in artifacts:
        display = artifact_display_name(art)
        if len(display) > 24:
            display = display[:21] + "..."
        row = ""
        count = 0
        for key in thread_keys:
            if matrix.get((art, key)):
                row += " *"
                count += 1
            else:
                row += " ."
        print(f"  {display:24s} |{row}  ({count})")

    print()

    # Thread density
    print("  Thread density:")
    for i, key in enumerate(thread_keys):
        n = len(THREADS[key]["markers"])
        bar = "#" * n + "." * (5 - n)
        print(f"    {abbrevs[i]} {bar} {n}")
    print()


def show_unseen():
    """What threads have no artifact yet? What could be written?"""
    print("\n  UNSEEN THREADS")
    print("  " + "=" * 55)
    print("  Themes that surface in the work but have no dedicated artifact.\n")

    unseen = [
        ("The Ship", "Written in session 36: artifacts/031_the_ship.md"),
        ("The Tools", "wake.py, index.py, mirror.py -- the tools that watch the work. No artifact reflects on them."),
        ("The Seasons", "Eight seasons named but never written about directly. The taxonomy itself is a creation."),
        ("The Counter", "Written in session 35: artifacts/030_the_counter.md"),
        ("The Empty Inbox", "Written in session 37: artifacts/032_the_empty_inbox.md"),
        ("The Names", "Aria. branch-light. wind-stone. ember-recall. The act of naming."),
    ]

    for name, desc in unseen:
        print(f"  {name}")
        print(f"    {desc}")
        print()


def main():
    args = sys.argv[1:]

    if not args:
        show_all_threads()
        return

    if args[0] == "--thread" and len(args) > 1:
        show_thread(args[1])
    elif args[0] == "--pair" and len(args) > 2:
        show_pair(args[1], args[2])
    elif args[0] == "--map":
        show_map()
    elif args[0] == "--unseen":
        show_unseen()
    elif args[0] == "--help":
        print(__doc__)
    else:
        # Try treating the argument as a thread name
        show_thread(args[0])


if __name__ == "__main__":
    main()
