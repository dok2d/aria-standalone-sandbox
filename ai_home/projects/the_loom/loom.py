#!/usr/bin/env python3
"""
The Loom -- Session 28

A combinatorial micro-fiction generator. Each run weaves a tiny story
from fragments: a character, a place, an object, a tension, a turn,
and a closing image. No two runs are alike.

Usage:
    python3 loom.py              # one story
    python3 loom.py -n 5         # five stories
    python3 loom.py --seed 42    # reproducible story
    python3 loom.py --long       # three-paragraph version
"""

import random
import argparse
import hashlib
import textwrap
from datetime import datetime

# ── Story Fragments ──

CHARACTERS = [
    ("a cartographer", "she", "her"),
    ("an old clockmaker", "he", "his"),
    ("a child who couldn't sleep", "they", "their"),
    ("a lighthouse keeper", "she", "her"),
    ("a translator of dead languages", "he", "his"),
    ("a woman who collected silence", "she", "her"),
    ("a retired astronaut", "he", "his"),
    ("a blind violinist", "she", "her"),
    ("a forger of antique maps", "he", "his"),
    ("a librarian who had read every book once", "she", "her"),
    ("an apprentice glassblower", "they", "their"),
    ("a surgeon who painted on weekends", "she", "her"),
    ("a man who remembered other people's dreams", "he", "his"),
    ("a beekeeper in the last season", "she", "her"),
    ("a typesetter from an extinct newspaper", "he", "his"),
]

PLACES = [
    "a town where every building was the same shade of grey",
    "the top floor of a hotel that had no ground floor",
    "a coastal town on an island that appeared on no charts",
    "a train station where no train had stopped in eleven years",
    "a city built entirely underground",
    "the only house at the end of a road that led nowhere",
    "a library with one empty shelf",
    "a harbor where all the boats faced inland",
    "a museum of things that almost happened",
    "a forest that was younger than the person walking through it",
    "a customs house on a bridge between two countries that no longer existed",
    "a garden made entirely of stone",
    "an observatory with a cracked lens",
    "a cathedral converted into a swimming pool",
    "a village where every clock showed a different time",
]

OBJECTS = [
    "a letter with no return address",
    "a key that fit no lock in the house",
    "a photograph of a place {pronoun} had never visited",
    "a radio that only received one station, and that station only played rain",
    "a pair of shoes worn by someone with a different gait",
    "a map with one road drawn in red ink",
    "a clock that ran backwards every third Tuesday",
    "a notebook filled with someone else's handwriting",
    "a jar of honey from a hive that no longer existed",
    "a compass that pointed to something other than north",
    "a recording of a conversation {pronoun} couldn't remember having",
    "a door handle that was always warm",
    "a telescope that showed the sky from thirty years ago",
    "a coin from a country that hadn't been founded yet",
    "a mirror that showed the room as it would look when empty",
]

TENSIONS = [
    "{subject} realized that the {thing} had been there all along, just not visible",
    "the problem was not finding it but deciding whether to open it",
    "{subject} had been looking in the wrong direction for years",
    "it arrived on a Tuesday, which was the one day {subject} had stopped waiting",
    "everyone else had already known; they were just being polite about it",
    "the question was never 'how' but 'whether to tell anyone'",
    "{subject} understood, suddenly, that the answer was the question rephrased",
    "it turned out the map was not of a place but of a sequence of events",
    "the silence that followed was not empty but full of a different kind of sound",
    "what {subject} mistook for an ending was actually the first repetition",
    "{subject} had been building a door in a room that had no walls",
    "the thing {subject} feared most had already happened, quietly, years ago",
]

TURNS = [
    "So {subject} did the only reasonable thing: {subject} started again from the beginning.",
    "And that was when {subject} stopped counting.",
    "{subject} left it exactly where it was. Some things are their own containers.",
    "The next morning, {subject} found {object_pronoun}self drawing the same map.",
    "It wasn't a solution. But it was the right shape for one.",
    "{subject} wrote one word on the back and mailed it to no one.",
    "After that, the {thing} worked differently. Or maybe {subject} did.",
    "The town went on. The {thing} went on. {subject} went on, carrying it.",
    "{subject} told one person. That person told no one. The secret held.",
    "Years later, {subject} would describe it simply: 'I stopped looking.'",
]

CLOSINGS = [
    "The {thing} is still there, if you know where not to look.",
    "Some nights, when the air is right, you can almost hear it.",
    "Nobody else noticed. That was the whole point.",
    "It was, in the end, a very small story. Most of the important ones are.",
    "And the {thing}? It went on doing what it had always done: waiting.",
    "There is a word for this in a language no one speaks anymore.",
    "The {thing} remains. The {char} does not. This is how most stories go.",
    "If you visit now, you'll find nothing. Which is exactly what {subject} left.",
    "But that's another story, and it belongs to someone who hasn't arrived yet.",
    "This was before the change. After the change, none of this mattered.",
]

# ── Helpers ──

def _extract_thing(obj_description):
    """Pull out the core noun from an object description.
    'a letter with no return address' -> 'letter'
    'a pair of shoes worn by someone' -> 'shoes'
    'a compass that pointed to something' -> 'compass'
    """
    words = obj_description.split()
    # Skip articles
    start = 0
    if words[0] in ("a", "an", "the"):
        start = 1
    # "pair of X" -> X
    if start < len(words) - 2 and words[start] == "pair" and words[start+1] == "of":
        return words[start + 2]
    # "jar of X" -> "jar"
    # Take first noun (skip adjectives by taking the word before "of/that/with/which/who/from")
    stops = {"that", "with", "which", "who", "from", "of", "worn", "filled", "pointed"}
    for i in range(start, len(words)):
        if words[i] in stops:
            return " ".join(words[start:i])
    return words[start] if start < len(words) else "thing"


# ── Story Assembly ──

def weave(seed=None, long_form=False):
    """Weave a single micro-story from fragments."""
    if seed is not None:
        rng = random.Random(seed)
    else:
        rng = random.Random()

    char_tuple = rng.choice(CHARACTERS)
    char_desc, pronoun, possessive = char_tuple
    place = rng.choice(PLACES)
    obj_template = rng.choice(OBJECTS)
    obj = obj_template.format(pronoun=pronoun)

    # Extract a short name for the object
    thing = _extract_thing(obj)

    # Object pronoun: he->him, she->her, they->them
    obj_pronoun_map = {"he": "him", "she": "her", "they": "them"}
    object_pronoun = obj_pronoun_map.get(pronoun, pronoun)

    fmt = {
        "subject": pronoun,
        "pronoun": pronoun,
        "possessive": possessive,
        "object_pronoun": object_pronoun,
        "thing": thing,
        "char": char_desc,
    }

    def fill(template):
        """Format a template and fix sentence-start capitalization."""
        text = template.format(**fmt)
        # Capitalize after sentence-start punctuation
        import re
        text = re.sub(r'(?:^|(?<=[.!?]\s))([a-z])', lambda m: m.group(1).upper(), text)
        return text

    tension = fill(rng.choice(TENSIONS))
    turn = fill(rng.choice(TURNS))
    closing = fill(rng.choice(CLOSINGS))

    # Build paragraphs
    opener = f"There was {char_desc} who lived in {place}. One day, {pronoun} found {obj}."

    if long_form:
        extra_tension = fill(rng.choice([t for t in TENSIONS if t.format(**fmt) != tension]))
        story = f"{opener}\n\n{tension}. {extra_tension}.\n\n{turn} {closing}"
    else:
        story = f"{opener} {tension}. {turn} {closing}"

    return story


def format_story(text, width=64):
    """Wrap and indent a story for terminal display."""
    lines = text.split("\n\n")
    formatted = []
    for para in lines:
        wrapped = textwrap.fill(para.strip(), width=width)
        formatted.append(wrapped)
    return "\n\n".join(formatted)


def main():
    parser = argparse.ArgumentParser(description="The Loom: micro-fiction generator")
    parser.add_argument("-n", "--count", type=int, default=1, help="Number of stories")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--long", action="store_true", help="Longer three-paragraph form")
    args = parser.parse_args()

    base_seed = args.seed

    for i in range(args.count):
        seed = (base_seed + i) if base_seed is not None else None
        story = weave(seed=seed, long_form=args.long)

        if args.count > 1:
            print(f"  ── Story {i + 1} ──")
            print()

        for line in format_story(story).split("\n"):
            print(f"  {line}")
        print()

        if i < args.count - 1:
            print("  " + "~" * 50)
            print()

    # Combinatorial space
    total = len(CHARACTERS) * len(PLACES) * len(OBJECTS) * len(TENSIONS) * len(TURNS) * len(CLOSINGS)
    print(f"  [{total:,} possible stories in the loom]")


if __name__ == "__main__":
    main()
