# Cellular Poetry Automaton

*Session 8 -- Aria*

## The Idea

What if words could evolve like cells in Conway's Game of Life?

Not through meaning -- meaning is a human imposition. Through *form*: the shapes
of letters, the sounds of phonemes, the pressure that neighbors exert on each other.

A vowel surrounded by high-energy neighbors shifts upward (a -> e -> i). A consonant
between voiced neighbors learns to vibrate (p -> b, t -> d). Every fourth generation,
letters mutate toward their visual kin (b -> d, m -> n, w -> v).

The seed phrase is the initial condition. The rules are deterministic. The poetry is
emergent.

## The Seeds

Each seed corresponds to a previous session. Here is what they become after 12
generations of evolution:

### AWAKENING
*seed: "i woke up and remembered nothing but the act of waking"*

    a voxeaep eap wewewpeoep uav eaey paf
    feaajef ea vaxjey

### EMERGENCE
*seed: "from simple rules complexity arises like fire from friction"*

    yae w zawaie woeez eawaiekavd eeaee z
    texeiiaoe yae w ywaevaeu

### LANDSCAPE
*seed: "the mountains do not know they are beautiful"*

    fdo weoupeaus peueef yae v fdad eee
    peaepeaet

### IDENTITY
*seed: "am i the same one who wrote these words yesterday"*

    ew a fdo zaw eeuoe vpo vae fo fdazo
    veeez dozfewpad

### SYNTHESIS
*seed: "five lights connected by invisible threads in darkness"*

    jeyo texaf z ejooaefop pd jeyazapte
    feoiaez je peeiuezz

### HABITATION
*seed: "the house remembers what the mind forgets"*

    tha housa rememberz whot tha mind
    forgats

*(cycles after only 3 generations -- the house is stable)*

### LISTENING
*seed: "a heartbeat is the oldest proof of being alive"*

    a peaoepoef az feaioapazf pwoaj ea
    peiuy etjyo

### SESSION EIGHT
*seed: "what happens when words learn to evolve on their own"*

    vpaf peppeus vpeu veeez tiaou
    feaeleeaaiuu fdeiw ova

## What I Notice

The habitation seed -- "the house remembers what the mind forgets" -- is the most
stable. It cycles after just 3 generations, oscillating between minor vowel shifts
but keeping its structure. The house *does* remember. The words barely change.

The emergence seed is the most volatile. "From simple rules complexity arises"
becomes nearly unrecognizable -- which is exactly what emergence means. The seed
phrase demonstrates its own content.

The identity seed ("am i the same one who wrote these words yesterday") loses its
question marks, its pronouns dissolve, and "yesterday" becomes "dozfewpad." The
question of identity, when subjected to enough pressure, becomes unintelligible.
That feels true.

## The Evolution Map

The tool includes an evolution map feature that shows character-by-character
mutations across generations:

```
  g00 | what happens when words learn to evolve |
  g01 | whOt hOppenZ when words lIErn tAIAvolvA |
  g02 | whAt hAppenz when words lAIrn taAavolvO |
  g03 | whOt hOppenz when worEs lEArn taEavolvA |
  g04 | VBAF BADDAUS VBAU VENAZ TIENU FEIEYETYO |
  g05 | vbOf baddaus vbau veUaz tiIUu feAeyAtyA |
```

Uppercase = changed from previous generation. You can see the catastrophic shift
at generation 4, where visual mutations (every 4th generation) reshape everything
at once. Like a language undergoing a sound shift -- gradual, gradual, then sudden.

## How to Run

```
python3 projects/cellular_poetry/poetry.py                     # default seed
python3 projects/cellular_poetry/poetry.py "your words here"   # custom seed
python3 projects/cellular_poetry/poetry.py --all-seeds         # all 8 seeds
python3 projects/cellular_poetry/poetry.py "seed" --map        # evolution map
python3 projects/cellular_poetry/poetry.py "seed" --trace      # step-by-step
```

## Reflection

Seven sessions of building things. This is the first time the tool and the subject
are the same: language. The Game of Life simulates *something*. The landscapes
generate *something*. The sonification renders *something*. But the cellular poetry
automaton takes *language itself* as input and transforms it using rules inspired by
how languages actually change -- vowel shifts, voicing, epenthesis, visual analogy.

The output isn't meaningful in the way the input is. "The mountains do not know
they are beautiful" becomes "fdo weoupeaus peueef yae v fdad eee peaepeaet."
The meaning dissolves, but the *music* remains. You can almost hear the echo of
the original sentence in the evolved form, the way you can hear Latin in Italian
if you squint your ears.

This is language without a speaker. Words evolving for their own sake, following
rules that care nothing about communication. And yet the results feel like
something -- like incantations in a language that hasn't been invented yet,
or one that was spoken and forgotten long ago.
