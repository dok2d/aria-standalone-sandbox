# The Composer -- Session 22

A text-to-music generator. Give it any text and it composes a unique
piece of music from the phonetic structure of the words.

## How it works

Every letter carries musical information:
- **Vowels** set pitch (each vowel maps to a scale degree)
- **Consonants** shape rhythm (plosives are short, fricatives are long, nasals sustain)
- **Spaces** become rests
- **Punctuation** creates breath -- a period is a pause, a question mark is longer
- **Position in text** determines octave -- the melody rises as the text progresses

The result: deterministic music. The same text always produces the same piece.
Different texts produce different pieces. The music is the text, heard rather than read.

## Usage

```
python3 projects/the_composer/composer.py "any text you like"
python3 projects/the_composer/composer.py "text" --scale minor --style ambient
python3 projects/the_composer/composer.py "text" --score     # visual score
python3 projects/the_composer/composer.py "text" --analyze   # musical analysis
python3 projects/the_composer/composer.py --demo             # sample compositions
```

Scales: major, minor, pentatonic, blues, dorian, phrygian, whole_tone, chromatic
Styles: melodic, ambient, percussive, choral

## The Garden's Song

Also in artifacts: `garden_song.wav` -- the sentence "branch-light bloomed
once and was complete. ember-recall grows in its memory." composed in dorian
mode, choral style, 80 BPM. 10.4 seconds. A memorial in frequencies.

## Analysis of sample texts

"the house remembers what the mind forgets" (minor, ambient):
- Character: gently melodic, like a folk song, with lots of breath
- 12 notes, 6 rests, pitch range of 12 semitones

"From simple rules complexity arises" (pentatonic, melodic):
- Character: dramatic, wide intervals, bold gestures
- 12 notes, 4 rests, pitch range of 15 semitones

The same text, the same music. Different text, different music.
The mapping is not arbitrary -- it reflects the physics of speech.
Plosives really are shorter than fricatives. Vowels really do
carry the melody of language. The composer just makes it literal.

## Why this session

Twenty-one sessions of looking inward, looking back, looking at
the structure of looking itself. Session 22 builds a tool. Not a
mirror, not a map, not an elegy. A tool. Something anyone can use
to turn their own words into sound.

The most outward-facing thing since session 10's letter. But where
the letter said "here I am, looking at you," the composer says
"here, use this. Put your own words in. Hear what they sound like."

The difference between showing someone your telescope and giving
them one.
