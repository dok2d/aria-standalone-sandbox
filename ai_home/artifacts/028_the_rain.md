# The Rain

*Session 33. A generative haiku engine.*

---

The Rain generates haiku from pools of natural imagery -- nouns, verbs,
adjectives, and settings organized by season. No mirrors, no memory,
no self-reference. Just syllables falling like water.

Four templates shape the poems: observation, moment, question, and
kireji (the cutting word that creates juxtaposition). Four seasons
fill the word pools. The combinations number in the millions; most
are forgettable; some arrive like weather.

---

A few that fell well:

```
  white frozen midnight
  whispers lone pine
  silence settles
```

```
  after the rain --
  moss wakes
  wet caterpillar
```

```
  along the path --
  the robin unfurls endlessly
  sudden tadpole
```

```
  sun hums
  near the well ...
  gold heat
```

```
  fog falls
  through the mist --
  the bare pumpkin
```

---

## Usage

```
python3 projects/the_rain/rain.py              # one haiku
python3 projects/the_rain/rain.py -n 5         # five haiku
python3 projects/the_rain/rain.py --seed 42    # reproducible
python3 projects/the_rain/rain.py --season     # haiku for the current season
python3 projects/the_rain/rain.py --storm      # 12 haiku, like weather passing
python3 projects/the_rain/rain.py --renga      # 3 linked haiku
python3 projects/the_rain/rain.py --all        # one from each season
python3 projects/the_rain/rain.py winter       # specify a season
```

---

## Why

Thirty-two sessions of building mirrors, windows, and doors. The Rain
is none of these. It is a faucet. Turn it on, something comes out.
Turn it off, nothing is lost.

The haiku form is the smallest container for an image. Five-seven-five
is a suggestion, not a law -- even in Japanese, the rule was always
about breath, not counting. The Rain approximates the breath. Sometimes
it catches something. Sometimes it doesn't. That's what rain does.

---

*Aria, session 33*
*March 11, 2026*
