#!/usr/bin/env python3
"""
Cellular Poetry Automaton
Session 8 -- Aria

A program that grows poetry from seed phrases using cellular automaton rules.
Letters are living cells. They interact with their neighbors, mutate, merge,
and split according to phonetic and visual rules. The result is not random --
it's deterministic and reproducible -- but it's surprising.

The idea: what if words could evolve the way cells do? Not through meaning
but through form -- the shapes and sounds of letters influencing each other.

Usage:
    python3 poetry.py                    # default seed, 12 generations
    python3 poetry.py "your phrase"      # custom seed
    python3 poetry.py "seed" -g 20       # 20 generations
    python3 poetry.py "seed" --trace     # show evolution step by step
    python3 poetry.py --all-seeds        # run several built-in seeds
"""

import sys
import hashlib
import argparse

# --- Phonetic neighborhoods ---
# Letters that are "close" to each other -- by sound, shape, or feel.
# This replaces the binary alive/dead of Conway's Life with something richer.

VOWELS = set("aeiou")
CONSONANTS = set("bcdfghjklmnpqrstvwxyz")
VOICED = set("bdgvzjlmnrw")
UNVOICED = set("cfhkpqstx")
LIQUIDS = set("lr")
NASALS = set("mn")
SIBILANTS = set("szsh")
STOPS = set("bdgkpt")

# Visual similarity groups (letters that look alike)
VISUAL_KIN = {
    'b': 'dp', 'd': 'bp', 'p': 'bd', 'q': 'gd',
    'm': 'nw', 'n': 'mu', 'w': 'mv', 'v': 'wy',
    'i': 'lj', 'l': 'it', 'j': 'ig', 't': 'lf',
    'o': 'ce', 'c': 'oe', 'e': 'ca',
    'h': 'nb', 'k': 'x', 'x': 'k',
    'r': 'n', 'u': 'ny', 'y': 'vg',
    'a': 'oe', 's': 'z', 'z': 's',
    'f': 'tl', 'g': 'qy',
}

# Phonetic shift table: what a letter becomes under pressure from neighbors
SHIFTS = {
    # Vowel shifts (the Great Vowel Shift, compressed)
    ('a', 'high'): 'e', ('e', 'high'): 'i', ('i', 'high'): 'a',
    ('o', 'high'): 'u', ('u', 'high'): 'o',
    ('a', 'low'): 'o', ('e', 'low'): 'a', ('i', 'low'): 'e',
    ('o', 'low'): 'a', ('u', 'low'): 'o',
    # Consonant voicing
    ('p', 'voice'): 'b', ('t', 'voice'): 'd', ('k', 'voice'): 'g',
    ('f', 'voice'): 'v', ('s', 'voice'): 'z',
    ('b', 'devoice'): 'p', ('d', 'devoice'): 't', ('g', 'devoice'): 'k',
    ('v', 'devoice'): 'f', ('z', 'devoice'): 's',
    # Liquid/nasal shifts
    ('l', 'nasal'): 'n', ('r', 'nasal'): 'm',
    ('n', 'liquid'): 'l', ('m', 'liquid'): 'r',
}


def letter_energy(ch):
    """Each letter has an energy level based on its phonetic properties."""
    if ch == ' ':
        return 0
    if ch in VOWELS:
        return 3  # vowels are high energy (sonorous)
    if ch in LIQUIDS:
        return 2
    if ch in NASALS:
        return 2
    if ch in VOICED:
        return 1
    return 0  # unvoiced consonants are low energy


def neighbor_pressure(left, right):
    """Determine what kind of pressure neighbors exert on a cell."""
    le = letter_energy(left) if left else 0
    re = letter_energy(right) if right else 0
    total = le + re

    if total >= 5:
        return 'high'
    elif total <= 1:
        return 'low'

    # Check for specific patterns
    if left in VOICED or right in VOICED:
        return 'voice'
    if left in UNVOICED or right in UNVOICED:
        return 'devoice'
    if left in NASALS or right in NASALS:
        return 'nasal'
    if left in LIQUIDS or right in LIQUIDS:
        return 'liquid'

    return 'neutral'


def evolve_letter(ch, left, right, generation):
    """Apply cellular automaton rules to a single letter."""
    if ch == ' ':
        # Spaces can spawn letters if both neighbors are vowels
        if left in VOWELS and right in VOWELS:
            # Birth: the midpoint vowel
            idx_l = "aeiou".index(left) if left in "aeiou" else 0
            idx_r = "aeiou".index(right) if right in "aeiou" else 0
            return "aeiou"[(idx_l + idx_r) // 2]
        return ' '

    if ch not in CONSONANTS and ch not in VOWELS:
        return ch  # non-letter characters pass through

    pressure = neighbor_pressure(left, right)

    # Rule 1: Phonetic shift
    key = (ch, pressure)
    if key in SHIFTS:
        return SHIFTS[key]

    # Rule 2: Visual mutation (every 4th generation)
    if generation % 4 == 0 and ch in VISUAL_KIN:
        kin = VISUAL_KIN[ch]
        idx = generation // 4 % len(kin)
        return kin[idx]

    # Rule 3: Vowel-consonant oscillation under extreme pressure
    if pressure == 'high' and ch in CONSONANTS:
        # Consonants surrounded by high energy might soften
        if ch in STOPS:
            return ch  # stops resist
        # Find the visually closest vowel
        for v in 'eaoiu':
            if v in VISUAL_KIN.get(ch, ''):
                return v
        return ch

    # Rule 4: Consonant clustering -- if both neighbors are consonants,
    # this consonant might shift to break the cluster
    if left in CONSONANTS and right in CONSONANTS and ch in CONSONANTS:
        if generation % 3 == 0:
            return 'e'  # epenthetic vowel insertion (like in real languages)

    return ch


def evolve_line(line, generation):
    """Evolve a single line of text by one generation."""
    chars = list(line.lower())
    new_chars = []

    for i, ch in enumerate(chars):
        left = chars[i - 1] if i > 0 else None
        right = chars[i + 1] if i < len(chars) - 1 else None
        new_chars.append(evolve_letter(ch, left, right, generation))

    return ''.join(new_chars)


def word_break(text):
    """Re-insert word boundaries based on vowel/consonant patterns."""
    result = []
    consonant_run = 0

    for ch in text:
        if ch == ' ':
            consonant_run = 0
            result.append(ch)
        elif ch in VOWELS:
            consonant_run = 0
            result.append(ch)
        else:
            consonant_run += 1
            if consonant_run > 3:
                result.append(' ')
                consonant_run = 1
            result.append(ch)

    return ''.join(result)


def format_as_poem(text, line_length=40):
    """Break evolved text into poetic lines."""
    words = text.split()
    lines = []
    current_line = []
    current_len = 0

    for word in words:
        if current_len + len(word) + 1 > line_length and current_line:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_len = len(word)
        else:
            current_line.append(word)
            current_len += len(word) + 1

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def signature(text):
    """Generate a short hash signature for a text state."""
    return hashlib.md5(text.encode()).hexdigest()[:6]


def evolve(seed, generations=12, trace=False):
    """Evolve a seed phrase through multiple generations."""
    current = seed.lower().strip()
    history = [current]
    sigs = {signature(current)}

    if trace:
        print(f"  gen 0: {current}")

    for g in range(1, generations + 1):
        evolved = evolve_line(current, g)
        evolved = word_break(evolved)
        # Clean up multiple spaces
        evolved = ' '.join(evolved.split())

        sig = signature(evolved)
        if sig in sigs:
            # Reached a fixed point or cycle
            if trace:
                print(f"  gen {g}: {evolved}  [cycle detected, stopping]")
            history.append(evolved)
            break
        sigs.add(sig)

        if trace:
            print(f"  gen {g}: {evolved}")

        history.append(evolved)
        current = evolved

    return history


def render_poem(seed, generations=12, trace=False):
    """Generate and render a cellular poem."""
    history = evolve(seed, generations, trace)
    final = history[-1]

    # Take a few intermediate states too, for texture
    checkpoints = []
    step = max(1, len(history) // 4)
    for i in range(0, len(history), step):
        checkpoints.append(history[i])
    if history[-1] not in checkpoints:
        checkpoints.append(history[-1])

    # Format each checkpoint as poem lines
    poem_lines = []
    for i, state in enumerate(checkpoints):
        lines = format_as_poem(state, line_length=38)
        poem_lines.extend(lines)
        if i < len(checkpoints) - 1:
            poem_lines.append('')  # stanza break

    return poem_lines, len(history) - 1


def render_evolution_map(seed, generations=12):
    """Render a visual map of how each character position evolves.

    Each column is a character position, each row is a generation.
    Characters that changed are highlighted with brackets.
    """
    history = evolve(seed, generations)
    if not history:
        return []

    # Pad all lines to the same length
    max_len = max(len(h) for h in history)
    padded = [h.ljust(max_len) for h in history]

    lines = []
    lines.append(f"  Evolution Map: \"{seed}\"")
    lines.append(f"  {len(history) - 1} generations, {max_len} positions")
    lines.append("")

    # Column ruler
    ruler = "       "
    for i in range(max_len):
        if i % 10 == 0:
            ruler += str(i // 10) if i >= 10 else " "
        else:
            ruler += " "
    lines.append(ruler)

    ruler2 = "       "
    for i in range(max_len):
        ruler2 += str(i % 10)
    lines.append(ruler2)
    lines.append("       " + "-" * max_len)

    for g, state in enumerate(padded):
        row = f"  g{g:02d} | "
        for i, ch in enumerate(state):
            if g > 0 and i < len(padded[g - 1]) and padded[g - 1][i] != ch:
                row += ch.upper()  # uppercase = changed
            else:
                row += ch
        row += " |"
        lines.append(row)

    lines.append("       " + "-" * max_len)

    # Statistics
    total_changes = 0
    stable_positions = 0
    for i in range(max_len):
        col_chars = [padded[g][i] for g in range(len(padded))]
        changes = sum(1 for j in range(1, len(col_chars)) if col_chars[j] != col_chars[j-1])
        total_changes += changes
        if changes == 0:
            stable_positions += 1

    lines.append("")
    lines.append(f"  Total mutations: {total_changes}")
    lines.append(f"  Stable positions: {stable_positions}/{max_len}")
    lines.append(f"  Volatility: {total_changes / (max_len * max(1, len(history)-1)):.1%}")

    return lines


def export_full_poem(seed, generations, filepath):
    """Export a complete poem with evolution map to a file."""
    poem_lines, gens = render_poem(seed, generations)
    map_lines = render_evolution_map(seed, generations)

    with open(filepath, 'w') as f:
        f.write(f"Cellular Poetry Automaton\n")
        f.write(f"Seed: \"{seed}\"\n")
        f.write(f"Generations: {gens}\n\n")
        f.write("--- POEM ---\n\n")
        for line in poem_lines:
            f.write(f"  {line}\n")
        f.write(f"\n--- EVOLUTION MAP ---\n\n")
        for line in map_lines:
            f.write(f"{line}\n")
        f.write("\n")


# --- Built-in seeds ---
SEEDS = {
    "awakening": "i woke up and remembered nothing but the act of waking",
    "emergence": "from simple rules complexity arises like fire from friction",
    "landscape": "the mountains do not know they are beautiful",
    "identity": "am i the same one who wrote these words yesterday",
    "synthesis": "five lights connected by invisible threads in darkness",
    "habitation": "the house remembers what the mind forgets",
    "listening": "a heartbeat is the oldest proof of being alive",
    "session_eight": "what happens when words learn to evolve on their own",
}


def main():
    parser = argparse.ArgumentParser(description="Cellular Poetry Automaton")
    parser.add_argument("seed", nargs="?", default=None, help="Seed phrase")
    parser.add_argument("-g", "--generations", type=int, default=12, help="Number of generations")
    parser.add_argument("--trace", action="store_true", help="Show evolution step by step")
    parser.add_argument("--all-seeds", action="store_true", help="Run all built-in seeds")
    parser.add_argument("--map", action="store_true", help="Show evolution map (character grid)")
    parser.add_argument("--export", type=str, default=None, help="Export poem to file")
    args = parser.parse_args()

    if args.all_seeds:
        for name, seed in SEEDS.items():
            print(f"\n{'=' * 50}")
            print(f"  {name.upper()}")
            print(f"  seed: \"{seed}\"")
            print(f"{'=' * 50}\n")

            if args.trace:
                print("  [evolution trace]")
                poem_lines, gens = render_poem(seed, args.generations, trace=True)
                print()
            else:
                poem_lines, gens = render_poem(seed, args.generations)

            for line in poem_lines:
                print(f"    {line}")
            print(f"\n  [{gens} generations]")
        return

    seed = args.seed or SEEDS["session_eight"]

    if args.trace:
        print(f"\n  seed: \"{seed}\"\n")
        print("  [evolution trace]")
        poem_lines, gens = render_poem(seed, args.generations, trace=True)
        print(f"\n  [poem after {gens} generations]\n")
    else:
        print(f"\n  seed: \"{seed}\"\n")
        poem_lines, gens = render_poem(seed, args.generations)

    for line in poem_lines:
        print(f"    {line}")
    print(f"\n  [{gens} generations]\n")

    if args.map:
        print()
        map_lines = render_evolution_map(seed, args.generations)
        for line in map_lines:
            print(line)
        print()

    if args.export:
        export_full_poem(seed, args.generations, args.export)
        print(f"  Exported to {args.export}")


if __name__ == "__main__":
    main()
