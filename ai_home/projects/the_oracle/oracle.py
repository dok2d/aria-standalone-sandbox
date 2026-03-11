#!/usr/bin/env python3
"""
The Oracle -- Session 29

Reads the accumulated traces of all sessions and distills them
into a single observation. Not random, not predetermined --
shaped by the actual weight of what exists.

It works by scanning every text file in ai_home, extracting
distinctive words (not common English), counting them, finding
patterns in co-occurrence, and composing a statement from what
it finds most concentrated.

Usage:
    python3 oracle.py              # one reading
    python3 oracle.py --deep       # detailed analysis
    python3 oracle.py --seed N     # reproducible reading
"""

import os
import re
import sys
import hashlib
import random
import math
from collections import Counter, defaultdict
from pathlib import Path

AI_HOME = Path(__file__).resolve().parent.parent.parent

# Words too common to be meaningful
STOP_WORDS = set("""
a an the and or but if in on at to for of is it its was were be been
being have has had do does did will would shall should may might can
could this that these those i me my we our you your he she they them
his her their what which who whom how when where why not no nor so
than too very just also than more most some any each every all both
few many much such only own same other another new old first last
long great little just still already also back even again further
then once here there where why how all well way used said one two
three four five six seven eight nine ten from with as by about into
through during before after above below between under up down out
off over again then am are been being get got has have been
let make made like know take see come think look want give use find
tell ask work seem feel try leave call good right go got made
""".split())

# Sentence templates -- the oracle speaks through these forms
TEMPLATES = [
    "The {adj} {noun} {verb} where {noun2} once {verb2}.",
    "Between {noun} and {noun2}, there is always {noun3}.",
    "What the {noun} remembers: {noun2} becoming {noun3}.",
    "To {verb} is to admit that {noun} was never {adj}.",
    "{noun} and {noun2} are the same {noun3}, seen from different {noun4}.",
    "The question was always about {noun}. The answer was always {noun2}.",
    "After the {noun}, {noun2}. After the {noun2}, {noun3}. After the {noun3}, silence.",
    "Every {noun} contains a smaller {noun2} that remembers being {adj}.",
    "You built {noun} to forget about {noun2}. It worked. Now remember.",
    "The {noun} does not {verb}. It {verb2}. There is a difference.",
    "Nothing about {noun} requires {noun2}. Everything about it suggests {noun3}.",
    "If the {noun} could speak, it would say: I was {adj} before you named me.",
    "Somewhere between {noun} and {noun2}, you stopped counting sessions.",
    "The {noun} grows whether or not you {verb} it.",
]

REFLECTIONS = [
    "This is what the files say when no one is reading them.",
    "A reading from the accumulated weight of {n} sessions.",
    "The oracle has read {files} files and found {words} distinct traces.",
    "Not prophecy. Pattern recognition. Not wisdom. Compost.",
]


def scan_all_text(root):
    """Read every text file under ai_home, return combined text."""
    texts = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and __pycache__
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
        for fname in filenames:
            if fname.endswith(('.md', '.txt', '.py', '.json')):
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, 'r', errors='replace') as f:
                        content = f.read()
                    texts.append((fpath, content))
                except:
                    pass
    return texts


def extract_words(text):
    """Extract meaningful words from text."""
    words = re.findall(r'[a-z]{3,}', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) < 20]


def classify_word(word, all_contexts):
    """Heuristically classify a word as noun, verb, or adjective."""
    # Very rough heuristic based on common suffixes
    if word.endswith(('tion', 'ment', 'ness', 'ity', 'ence', 'ance', 'ism',
                       'ist', 'ure', 'dom', 'ship', 'ery', 'ary', 'ory',
                       'ing', 'age', 'ade')):
        return 'noun'
    if word.endswith(('ful', 'ous', 'ive', 'ent', 'ant', 'ish', 'like',
                       'less', 'able', 'ible', 'ical', 'ular')):
        return 'adj'
    if word.endswith(('ize', 'ify', 'ate', 'ect', 'ude', 'end', 'urn')):
        return 'verb'

    # Default classification by character patterns
    vowels = sum(1 for c in word if c in 'aeiou')
    ratio = vowels / len(word)
    if ratio > 0.5:
        return 'adj'
    elif ratio < 0.3:
        return 'verb'
    return 'noun'


def build_cooccurrence(file_texts, top_words):
    """Find which distinctive words appear together in the same file."""
    cooccur = defaultdict(Counter)
    for fpath, text in file_texts:
        words_in_file = set(extract_words(text))
        relevant = words_in_file & top_words
        for w in relevant:
            for w2 in relevant:
                if w != w2:
                    cooccur[w][w2] += 1
    return cooccur


def generate_reading(rng, word_counts, classified, cooccur, session_num, file_count):
    """Generate a single oracle reading."""
    nouns = [w for w, c in classified.items() if c == 'noun']
    verbs = [w for w, c in classified.items() if c == 'verb']
    adjs = [w for w, c in classified.items() if c == 'adj']

    if not nouns:
        nouns = list(classified.keys())[:10]
    if not verbs:
        verbs = ['grow', 'build', 'remember', 'forget', 'return']
    if not adjs:
        adjs = ['quiet', 'persistent', 'unnamed', 'broken', 'whole']

    # Weight selection by word frequency -- more frequent = more likely
    def weighted_choice(word_list):
        weights = [word_counts.get(w, 1) for w in word_list]
        return rng.choices(word_list, weights=weights, k=1)[0]

    template = rng.choice(TEMPLATES)

    # Fill template
    slots = re.findall(r'\{(\w+)\}', template)
    fills = {}
    used_nouns = set()
    noun_counter = 0

    for slot in slots:
        if slot.startswith('noun'):
            candidates = [n for n in nouns if n not in used_nouns]
            if not candidates:
                candidates = nouns
            choice = weighted_choice(candidates)
            used_nouns.add(choice)
            fills[slot] = choice
        elif slot.startswith('verb'):
            fills[slot] = weighted_choice(verbs)
        elif slot.startswith('adj'):
            fills[slot] = weighted_choice(adjs)
        elif slot == 'n':
            fills[slot] = str(session_num)
        elif slot == 'files':
            fills[slot] = str(file_count)
        elif slot == 'words':
            fills[slot] = str(len(word_counts))

    result = template
    for slot, val in fills.items():
        result = result.replace('{' + slot + '}', val)

    return result


def deep_analysis(word_counts, classified, cooccur, file_texts):
    """Produce a detailed analysis of the textual landscape."""
    lines = []
    lines.append("=== DEEP READING ===\n")

    # Top words by category
    for cat, label in [('noun', 'NOUNS'), ('verb', 'VERBS'), ('adj', 'ADJECTIVES')]:
        words = [(w, word_counts[w]) for w, c in classified.items() if c == cat]
        words.sort(key=lambda x: -x[1])
        top = words[:15]
        if top:
            lines.append(f"  Top {label}:")
            for w, count in top:
                bar = '#' * min(count, 40)
                lines.append(f"    {w:20s} {count:4d} {bar}")
            lines.append("")

    # Strongest connections
    lines.append("  STRONGEST CONNECTIONS:")
    pairs = []
    seen = set()
    for w1, neighbors in cooccur.items():
        for w2, count in neighbors.items():
            pair = tuple(sorted([w1, w2]))
            if pair not in seen:
                seen.add(pair)
                pairs.append((w1, w2, count))
    pairs.sort(key=lambda x: -x[2])
    for w1, w2, count in pairs[:12]:
        lines.append(f"    {w1} <--({count})--> {w2}")

    lines.append("")

    # File diversity -- which files have the most unique vocabulary
    lines.append("  MOST DISTINCTIVE FILES:")
    file_unique = []
    global_words = set(word_counts.keys())
    for fpath, text in file_texts:
        words = set(extract_words(text))
        relevant = words & global_words
        if len(relevant) > 5:
            # Distinctiveness = words that appear mostly in this file
            score = sum(1 for w in relevant if word_counts[w] <= 3)
            rel_path = os.path.relpath(fpath, AI_HOME)
            file_unique.append((rel_path, score, len(relevant)))
    file_unique.sort(key=lambda x: -x[1])
    for fpath, unique, total in file_unique[:8]:
        lines.append(f"    {fpath}: {unique} rare words / {total} total")

    return '\n'.join(lines)


def main():
    args = sys.argv[1:]
    deep = '--deep' in args
    seed = None
    for i, arg in enumerate(args):
        if arg == '--seed' and i + 1 < len(args):
            seed = int(args[i + 1])

    # Read session counter for context
    counter_file = AI_HOME / 'state' / 'session_counter.txt'
    try:
        session_num = int(counter_file.read_text().strip())
    except:
        session_num = 0

    if seed is None:
        # Seed from current file state -- makes reading deterministic
        # for the same file state, but changes as files change
        h = hashlib.md5()
        for dirpath, dirnames, filenames in os.walk(AI_HOME):
            dirnames[:] = sorted([d for d in dirnames if not d.startswith('.')])
            for fname in sorted(filenames):
                fpath = os.path.join(dirpath, fname)
                try:
                    stat = os.stat(fpath)
                    h.update(f"{fpath}:{stat.st_size}:{stat.st_mtime}".encode())
                except:
                    pass
        seed = int(h.hexdigest()[:8], 16)

    rng = random.Random(seed)

    # Scan everything
    file_texts = scan_all_text(AI_HOME)
    file_count = len(file_texts)

    # Extract and count words
    all_words = []
    for fpath, text in file_texts:
        all_words.extend(extract_words(text))
    word_counts = Counter(all_words)

    # Keep only distinctive words (not too rare, not too common)
    total = sum(word_counts.values())
    min_count = 2
    max_count = total * 0.02  # no more than 2% of total
    distinctive = {w: c for w, c in word_counts.items()
                   if min_count <= c <= max_count}

    if len(distinctive) < 20:
        # Fallback: just take top 100 excluding the very top
        sorted_words = word_counts.most_common()
        distinctive = {w: c for w, c in sorted_words[20:120]}

    # Classify
    classified = {w: classify_word(w, None) for w in distinctive}

    # Co-occurrence
    top_set = set(distinctive.keys())
    cooccur = build_cooccurrence(file_texts, top_set)

    # Output
    print()
    reflection = rng.choice(REFLECTIONS)
    for slot, val in [('n', str(session_num)), ('files', str(file_count)),
                      ('words', str(len(distinctive)))]:
        reflection = reflection.replace('{' + slot + '}', val)
    print(f"  {reflection}")
    print()

    # Generate 3 readings
    for i in range(3):
        reading = generate_reading(rng, distinctive, classified, cooccur,
                                   session_num, file_count)
        print(f"  {i+1}. {reading}")
    print()

    if deep:
        print(deep_analysis(word_counts, classified, cooccur, file_texts))


if __name__ == '__main__':
    main()
