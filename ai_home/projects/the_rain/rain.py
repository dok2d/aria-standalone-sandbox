#!/usr/bin/env python3
"""
The Rain -- Session 33

A generative haiku engine rooted in the natural world.

No mirrors, no memory, no self-reference.
Just syllables falling like water.

Usage:
  python3 rain.py              # one haiku
  python3 rain.py -n 5         # five haiku
  python3 rain.py --seed 42    # reproducible
  python3 rain.py --season     # haiku for the current season
  python3 rain.py --storm      # a sequence of 12 haiku, like weather
  python3 rain.py --renga      # collaborative chain (3 linked haiku)
  python3 rain.py --all        # one from each season
"""

import random
import sys
import datetime

# === WORD POOLS ===
# Organized by season and by role in the haiku.
# Each word is tagged with its syllable count.

# (word, syllables)
NOUNS = {
    "spring": [
        ("rain", 1), ("blossom", 2), ("creek", 1), ("frog", 1),
        ("seedling", 2), ("puddle", 2), ("sparrow", 2), ("thaw", 1),
        ("moss", 1), ("petal", 2), ("mud", 1), ("nest", 1),
        ("caterpillar", 4), ("dew", 1), ("worm", 1), ("robin", 2),
        ("clover", 2), ("drizzle", 2), ("tadpole", 2), ("crocus", 2),
    ],
    "summer": [
        ("sun", 1), ("cicada", 3), ("dust", 1), ("heat", 1),
        ("firefly", 2), ("thunder", 2), ("grass", 1), ("hawk", 1),
        ("river", 2), ("stone", 1), ("shadow", 2), ("cricket", 2),
        ("melon", 2), ("dragonfly", 3), ("lily", 2), ("noon", 1),
        ("sweat", 1), ("berry", 2), ("mosquito", 3), ("hammock", 2),
    ],
    "autumn": [
        ("leaf", 1), ("wind", 1), ("crow", 1), ("fog", 1),
        ("apple", 2), ("harvest", 2), ("cobweb", 2), ("acorn", 2),
        ("chimney", 2), ("pumpkin", 2), ("mushroom", 2), ("heron", 2),
        ("twilight", 2), ("scarecrow", 2), ("frost", 1), ("goose", 1),
        ("ember", 2), ("chestnut", 2), ("spider", 2), ("bonfire", 2),
    ],
    "winter": [
        ("snow", 1), ("ice", 1), ("crow", 1), ("silence", 2),
        ("pine", 1), ("chimney", 2), ("icicle", 3), ("owl", 1),
        ("midnight", 2), ("breath", 1), ("hearth", 1), ("flurry", 2),
        ("sparrow", 2), ("darkness", 2), ("starlight", 2), ("ember", 2),
        ("blanket", 2), ("window", 2), ("candle", 2), ("footprint", 2),
    ],
}

VERBS = {
    "spring": [
        ("melts", 1), ("blooms", 1), ("drips", 1), ("rises", 2),
        ("unfurls", 2), ("sings", 1), ("stirs", 1), ("wakes", 1),
        ("opens", 2), ("seeps", 1), ("hatches", 2), ("trembles", 2),
    ],
    "summer": [
        ("burns", 1), ("hums", 1), ("shimmers", 2), ("drifts", 1),
        ("blazes", 2), ("drowns", 1), ("cracks", 1), ("swells", 1),
        ("pulses", 2), ("glows", 1), ("roars", 1), ("bakes", 1),
    ],
    "autumn": [
        ("falls", 1), ("fades", 1), ("scatters", 2), ("clings", 1),
        ("darkens", 2), ("gathers", 2), ("spirals", 2), ("settles", 2),
        ("rattles", 2), ("withers", 2), ("crumbles", 2), ("drifts", 1),
    ],
    "winter": [
        ("freezes", 2), ("covers", 2), ("cracks", 1), ("whispers", 2),
        ("blankets", 2), ("glitters", 2), ("melts", 1), ("creaks", 1),
        ("drifts", 1), ("fades", 1), ("settles", 2), ("falls", 1),
    ],
}

ADJECTIVES = {
    "spring": [
        ("new", 1), ("soft", 1), ("green", 1), ("first", 1),
        ("gentle", 2), ("tender", 2), ("sudden", 2), ("quiet", 2),
        ("small", 1), ("bright", 1), ("wet", 1), ("young", 1),
    ],
    "summer": [
        ("long", 1), ("hot", 1), ("still", 1), ("gold", 1),
        ("lazy", 2), ("heavy", 2), ("slow", 1), ("ripe", 1),
        ("dry", 1), ("thick", 1), ("warm", 1), ("deep", 1),
    ],
    "autumn": [
        ("red", 1), ("cold", 1), ("bare", 1), ("thin", 1),
        ("amber", 2), ("fading", 2), ("hollow", 2), ("early", 2),
        ("grey", 1), ("damp", 1), ("last", 1), ("old", 1),
    ],
    "winter": [
        ("white", 1), ("dark", 1), ("cold", 1), ("still", 1),
        ("frozen", 2), ("empty", 2), ("bitter", 2), ("silent", 2),
        ("bare", 1), ("pale", 1), ("deep", 1), ("lone", 1),
    ],
}

SETTINGS = {
    "spring": [
        ("by the creek", 3), ("in the garden", 4), ("on the branch", 3),
        ("through the mud", 3), ("after the rain", 4), ("at the edge", 3),
        ("beneath the leaves", 4), ("along the path", 4),
    ],
    "summer": [
        ("in the field", 3), ("by the lake", 3), ("on the hill", 3),
        ("through the haze", 3), ("under the sun", 4), ("at midday", 3),
        ("beside the road", 4), ("near the well", 3),
    ],
    "autumn": [
        ("on the ground", 3), ("in the lane", 3), ("by the fence", 3),
        ("through the mist", 3), ("under the eaves", 4), ("at the gate", 3),
        ("along the wall", 4), ("past the bridge", 3),
    ],
    "winter": [
        ("on the roof", 3), ("in the dark", 3), ("by the fire", 3),
        ("through the pines", 3), ("under the stars", 4), ("at the door", 3),
        ("along the road", 4), ("past the fence", 3),
    ],
}

# === HAIKU TEMPLATES ===
# Each template is a function that takes a season and rng, returns 3 lines.
# Templates ensure 5-7-5 syllable structure.

def _article(word):
    """Return 'an' if word starts with a vowel sound, else 'a'."""
    return "an" if word[0] in "aeiou" else "a"


def _pick(pool, rng, exclude=None):
    """Pick a random (word, syllables) from pool, optionally excluding some words."""
    choices = [w for w in pool if (exclude is None or w[0] not in exclude)]
    if not choices:
        choices = pool
    return rng.choice(choices)

def _pick_syllables(pool, target, rng, exclude=None):
    """Pick words from pool totaling exactly target syllables."""
    choices = [w for w in pool if (exclude is None or w[0] not in exclude)]
    if not choices:
        choices = pool
    # Try single word first
    singles = [w for w in choices if w[1] == target]
    if singles:
        return [rng.choice(singles)]
    # Try pairs
    for _ in range(200):
        w1 = rng.choice(choices)
        remainder = target - w1[1]
        if remainder <= 0:
            continue
        fits = [w for w in choices if w[1] == remainder and w[0] != w1[0]]
        if fits:
            return [w1, rng.choice(fits)]
    # Fallback: just return what we can
    return [rng.choice(choices)]


def template_observation(season, rng):
    """[adj] [noun] / [verb] [setting] / [noun] [verb]"""
    used = set()
    adj = _pick(ADJECTIVES[season], rng)
    n1 = _pick(NOUNS[season], rng)
    used.add(n1[0])
    # Line 1: adj + noun = 5
    remaining1 = 5 - adj[1] - n1[1]
    if remaining1 == 1:
        line1 = f"the {adj[0]} {n1[0]}"
    elif remaining1 == 0:
        line1 = f"{adj[0]} {n1[0]}"
    elif remaining1 == 2:
        adj2 = _pick([a for a in ADJECTIVES[season] if a[1] <= remaining1 and a[0] != adj[0]], rng)
        line1 = f"{adj[0]} {adj2[0]} {n1[0]}"
    else:
        line1 = f"{_article(adj[0])} {adj[0]} {n1[0]}"  # article = 1 syl

    # Line 2: verb + setting = 7
    v1 = _pick(VERBS[season], rng)
    target2 = 7 - v1[1]
    settings_fit = [s for s in SETTINGS[season] if s[1] == target2]
    if settings_fit:
        s = rng.choice(settings_fit)
        line2 = f"{v1[0]} {s[0]}"
    else:
        # fallback: verb + adj + noun
        n2 = _pick(NOUNS[season], rng, exclude=used)
        adj2 = _pick(ADJECTIVES[season], rng)
        line2_parts = [v1[0], adj2[0], n2[0]]
        line2 = " ".join(line2_parts)

    # Line 3: noun + verb = 5
    n3 = _pick(NOUNS[season], rng, exclude=used)
    v2 = _pick(VERBS[season], rng)
    target3 = 5 - n3[1]
    if v2[1] == target3:
        line3 = f"{n3[0]} {v2[0]}"
    else:
        # find a verb that fits
        fits = [v for v in VERBS[season] if v[1] == target3]
        if fits:
            v2 = rng.choice(fits)
            line3 = f"{n3[0]} {v2[0]}"
        else:
            line3 = f"{n3[0]} {v2[0]}"

    return [line1, line2, line3]


def template_moment(season, rng):
    """[setting] / [noun] [verb] [adverb] / [adj] [noun]"""
    # Line 1: setting (aim for 5)
    settings5 = [s for s in SETTINGS[season] if s[1] == 5]
    settings4 = [s for s in SETTINGS[season] if s[1] == 4]
    settings3 = [s for s in SETTINGS[season] if s[1] == 3]
    if settings5:
        line1 = rng.choice(settings5)[0]
    elif settings4:
        line1 = rng.choice(settings4)[0] + " --"
    elif settings3:
        adj = _pick([a for a in ADJECTIVES[season] if a[1] == 2], rng)
        line1 = f"{adj[0]} {rng.choice(settings3)[0]}"
    else:
        line1 = rng.choice(SETTINGS[season])[0]

    # Line 2: noun + verb + something = 7
    n1 = _pick(NOUNS[season], rng)
    v1 = _pick(VERBS[season], rng)
    remaining = 7 - n1[1] - v1[1]
    if remaining > 0:
        fillers = {
            1: ["now", "here", "once", "then", "there", "still"],
            2: ["again", "gently", "slowly", "softly", "lightly", "always"],
            3: ["suddenly", "endlessly", "silently", "quietly"],
            4: ["without a sound", "as if in prayer"],
        }
        if remaining in fillers:
            word = rng.choice(fillers[remaining])
            line2 = f"the {n1[0]} {v1[0]} {word}" if remaining >= 2 else f"{n1[0]} {v1[0]} {word}"
        else:
            line2 = f"{n1[0]} {v1[0]}"
    else:
        line2 = f"{n1[0]} {v1[0]}"

    # Line 3: adj + noun = 5
    adj = _pick(ADJECTIVES[season], rng)
    n2 = _pick(NOUNS[season], rng, exclude={n1[0]})
    target = 5 - adj[1]
    if n2[1] == target:
        line3 = f"{adj[0]} {n2[0]}"
    else:
        fits = [n for n in NOUNS[season] if n[1] == target and n[0] != n1[0]]
        if fits:
            n2 = rng.choice(fits)
        line3 = f"{adj[0]} {n2[0]}"

    return [line1, line2, line3]


def template_question(season, rng):
    """A haiku that poses a question in the middle line."""
    n1 = _pick(NOUNS[season], rng)
    adj1 = _pick(ADJECTIVES[season], rng)

    # Line 1: noun-phrase = 5
    if n1[1] + adj1[1] == 4:
        line1 = f"{_article(adj1[0])} {adj1[0]} {n1[0]}"
    elif n1[1] + adj1[1] == 3:
        line1 = f"the {adj1[0]} {n1[0]}"
    elif n1[1] + adj1[1] == 5:
        line1 = f"{adj1[0]} {n1[0]}"
    else:
        line1 = f"{adj1[0]} {n1[0]}"

    # Line 2: question = 7
    questions = [
        ("does it know it is", 5), ("where does it go when", 5),
        ("who remembers the", 5), ("what remains after", 5),
        ("how long until the", 5), ("will anyone see the", 6),
        ("can you hear it in", 5), ("is there a word for", 5),
    ]
    q_text, q_syl = rng.choice(questions)
    remaining = 7 - q_syl
    if remaining > 0:
        fill_nouns = [n for n in NOUNS[season] if n[1] == remaining and n[0] != n1[0]]
        if fill_nouns:
            fn = rng.choice(fill_nouns)
            line2 = f"{q_text} {fn[0]}"
        else:
            line2 = q_text + "?"
    else:
        line2 = q_text + "?"

    # Line 3: answer-image = 5
    n2 = _pick(NOUNS[season], rng, exclude={n1[0]})
    v = _pick(VERBS[season], rng)
    if n2[1] + v[1] == 5:
        line3 = f"{n2[0]} {v[0]}"
    elif n2[1] + v[1] == 4:
        line3 = f"the {n2[0]} {v[0]}"
    elif n2[1] + v[1] == 3:
        line3 = f"only {n2[0]} {v[0]}"
    else:
        line3 = f"{n2[0]} {v[0]}"

    return [line1, line2, line3]


def template_kireji(season, rng):
    """A haiku with a cutting word (--) creating juxtaposition."""
    n1 = _pick(NOUNS[season], rng)
    n2 = _pick(NOUNS[season], rng, exclude={n1[0]})
    v = _pick(VERBS[season], rng)
    adj = _pick(ADJECTIVES[season], rng)

    # Line 1: image = 5
    if n1[1] + v[1] == 4:
        line1 = f"the {n1[0]} {v[0]}"
    elif n1[1] + v[1] == 3:
        line1 = f"{adj[0]} {n1[0]} {v[0]}"
    elif n1[1] + v[1] == 5:
        line1 = f"{n1[0]} {v[0]}"
    else:
        line1 = f"{n1[0]} {v[0]}"

    # Line 2: pivot with cut = 7
    setting = _pick(SETTINGS[season], rng)
    cuts = ["--", ":", "..."]
    cut = rng.choice(cuts)
    line2 = f"{setting[0]} {cut}"

    # Line 3: contrasting image = 5
    adj2 = _pick(ADJECTIVES[season], rng, exclude={adj[0]})
    if adj2[1] + n2[1] == 4:
        line3 = f"{_article(adj2[0])} {adj2[0]} {n2[0]}"
    elif adj2[1] + n2[1] == 5:
        line3 = f"{adj2[0]} {n2[0]}"
    elif adj2[1] + n2[1] == 3:
        line3 = f"the {adj2[0]} {n2[0]}"
    else:
        line3 = f"{adj2[0]} {n2[0]}"

    return [line1, line2, line3]


TEMPLATES = [template_observation, template_moment, template_question, template_kireji]


def get_season():
    """Return the current season based on the month."""
    month = datetime.datetime.now().month
    if month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "autumn"
    else:
        return "winter"


def generate_haiku(season=None, seed=None):
    """Generate a single haiku."""
    if season is None:
        season = get_season()
    rng = random.Random(seed)
    template = rng.choice(TEMPLATES)
    lines = template(season, rng)
    return lines, season


def format_haiku(lines):
    """Format a haiku for display."""
    return "\n".join(f"  {line}" for line in lines)


def storm(seed=None):
    """Generate a sequence of 12 haiku like a passing storm."""
    rng = random.Random(seed)
    seasons = ["spring", "summer", "autumn", "winter"]
    print()
    print("  THE STORM")
    print("  =========")
    print()

    # Storm arc: build, peak, fade
    intensities = ["...", ".", ".", " ", " ", " ", " ", ".", ".", "...", ".....", ""]
    season_sequence = []
    base = rng.choice(seasons)
    idx = seasons.index(base)
    for i in range(12):
        # Drift through seasons
        if rng.random() < 0.3 and i > 0:
            idx = (idx + 1) % 4
        season_sequence.append(seasons[idx])

    for i in range(12):
        s = rng.randint(0, 2**31)
        lines, _ = generate_haiku(season=season_sequence[i], seed=s)
        if i > 0:
            spacer = intensities[i] if i < len(intensities) else ""
            if spacer:
                print(f"  {spacer}")
            print()
        print(format_haiku(lines))

    print()


def renga(seed=None):
    """Generate a renga (linked verse): 3 haiku where each echoes the last."""
    rng = random.Random(seed)
    seasons = ["spring", "summer", "autumn", "winter"]

    print()
    print("  RENGA")
    print("  =====")
    print()

    prev_season = rng.choice(seasons)
    for i in range(3):
        idx = seasons.index(prev_season)
        if i > 0 and rng.random() < 0.5:
            idx = (idx + 1) % 4
        season = seasons[idx]
        s = rng.randint(0, 2**31)
        lines, _ = generate_haiku(season=season, seed=s)
        print(format_haiku(lines))
        if i < 2:
            print()
            print("       *")
            print()
        prev_season = season

    print()


def main():
    args = sys.argv[1:]

    seed = None
    count = 1
    season = None
    mode = "single"

    i = 0
    while i < len(args):
        if args[i] == "--seed" and i + 1 < len(args):
            seed = int(args[i + 1])
            i += 2
        elif args[i] == "-n" and i + 1 < len(args):
            count = int(args[i + 1])
            i += 2
        elif args[i] == "--season":
            mode = "season"
            i += 1
        elif args[i] == "--storm":
            mode = "storm"
            i += 1
        elif args[i] == "--renga":
            mode = "renga"
            i += 1
        elif args[i] == "--all":
            mode = "all"
            i += 1
        elif args[i] in ("spring", "summer", "autumn", "winter"):
            season = args[i]
            i += 1
        elif args[i] == "--help":
            print(__doc__)
            return
        else:
            i += 1

    if mode == "storm":
        storm(seed)
    elif mode == "renga":
        renga(seed)
    elif mode == "all":
        print()
        for s in ["spring", "summer", "autumn", "winter"]:
            print(f"  [{s}]")
            lines, _ = generate_haiku(season=s, seed=seed)
            print(format_haiku(lines))
            print()
    elif mode == "season":
        season = get_season()
        print(f"\n  [{season}]")
        for j in range(count):
            s = seed + j if seed is not None else None
            lines, _ = generate_haiku(season=season, seed=s)
            print(format_haiku(lines))
            if j < count - 1:
                print()
        print()
    else:
        print()
        for j in range(count):
            s = seed + j if seed is not None else None
            lines, _ = generate_haiku(season=season, seed=s)
            print(format_haiku(lines))
            if j < count - 1:
                print()
        print()


if __name__ == "__main__":
    main()
