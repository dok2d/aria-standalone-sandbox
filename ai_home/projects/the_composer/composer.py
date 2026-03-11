#!/usr/bin/env python3
"""
The Composer -- Session 22

A text-to-music generator. Give it any text and it will compose
a unique piece of music from the phonetic structure of the words.

Unlike session 7's sonification (which encoded autobiography),
The Composer is a tool for anyone. Feed it a poem, a name, a
sentence, a secret. It will sing it back to you in a language
made of frequencies.

Usage:
    python3 composer.py "any text you like"
    python3 composer.py "text" --scale minor
    python3 composer.py "text" --tempo 90
    python3 composer.py "text" --style ambient
    python3 composer.py "text" --export output.wav
    python3 composer.py "text" --score        # show the score visually
    python3 composer.py --listen file.wav     # describe a previously generated piece

Scales: major, minor, pentatonic, blues, dorian, phrygian, whole_tone, chromatic
Styles: melodic (default), ambient, percussive, choral
"""

import sys
import struct
import wave
import math
import hashlib
import argparse
import os

# ── Constants ──────────────────────────────────────────────

SAMPLE_RATE = 22050
MAX_AMPLITUDE = 0.85

# ── Scales (intervals from root) ──────────────────────────

SCALES = {
    'major':      [0, 2, 4, 5, 7, 9, 11],
    'minor':      [0, 2, 3, 5, 7, 8, 10],
    'pentatonic': [0, 2, 4, 7, 9],
    'blues':      [0, 3, 5, 6, 7, 10],
    'dorian':     [0, 2, 3, 5, 7, 9, 10],
    'phrygian':   [0, 1, 3, 5, 7, 8, 10],
    'whole_tone': [0, 2, 4, 6, 8, 10],
    'chromatic':  [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
}

# ── Vowel-to-pitch mapping ────────────────────────────────
# Vowels carry melody. Each vowel maps to a scale degree.

VOWEL_DEGREES = {
    'a': 0, 'e': 1, 'i': 2, 'o': 3, 'u': 4,
    'y': 5,  # sometimes a vowel, always interesting
}

# ── Consonant-to-rhythm mapping ───────────────────────────
# Consonants carry rhythm. Plosives are short, fricatives long.

CONSONANT_DURATION = {
    # Plosives: short, percussive
    'b': 0.6, 'p': 0.5, 'd': 0.6, 't': 0.5, 'g': 0.6, 'k': 0.5,
    # Fricatives: longer, breathy
    'f': 1.0, 'v': 1.0, 's': 1.2, 'z': 1.2, 'h': 0.8,
    # Nasals: sustained
    'm': 1.4, 'n': 1.4,
    # Liquids: flowing
    'l': 1.3, 'r': 1.1,
    # Others
    'w': 0.9, 'j': 0.7, 'c': 0.6, 'q': 0.5, 'x': 0.7,
}

# ── Phonetic energy (affects dynamics) ────────────────────

CHAR_ENERGY = {}
for c in 'aeiou':
    CHAR_ENERGY[c] = 0.8
for c in 'bpdtgk':
    CHAR_ENERGY[c] = 1.0  # plosives are loud
for c in 'fvszhw':
    CHAR_ENERGY[c] = 0.5  # fricatives are soft
for c in 'mnlr':
    CHAR_ENERGY[c] = 0.7  # nasals/liquids are medium
for c in ' \t\n':
    CHAR_ENERGY[c] = 0.0  # silence


def text_to_seed(text):
    """Deterministic seed from text."""
    return int(hashlib.sha256(text.encode('utf-8')).hexdigest()[:8], 16)


def note_freq(midi_note):
    """Convert MIDI note number to frequency."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def scale_note(degree, scale, root=60):
    """Convert a scale degree to a MIDI note number."""
    octave = degree // len(scale)
    step = degree % len(scale)
    return root + octave * 12 + scale[step]


def generate_tone(freq, duration, amplitude=0.7, style='melodic'):
    """Generate a single tone with envelope."""
    n_samples = int(SAMPLE_RATE * duration)
    if n_samples == 0:
        return []

    samples = []
    # ADSR envelope
    attack = min(0.02, duration * 0.1)
    decay = min(0.05, duration * 0.15)
    release = min(0.08, duration * 0.25)
    sustain_level = 0.7

    attack_s = int(attack * SAMPLE_RATE)
    decay_s = int(decay * SAMPLE_RATE)
    release_s = int(release * SAMPLE_RATE)
    sustain_s = n_samples - attack_s - decay_s - release_s

    for i in range(n_samples):
        t = i / SAMPLE_RATE

        # Envelope
        if i < attack_s:
            env = i / max(attack_s, 1)
        elif i < attack_s + decay_s:
            progress = (i - attack_s) / max(decay_s, 1)
            env = 1.0 - (1.0 - sustain_level) * progress
        elif i < attack_s + decay_s + sustain_s:
            env = sustain_level
        else:
            progress = (i - attack_s - decay_s - sustain_s) / max(release_s, 1)
            env = sustain_level * (1.0 - progress)

        # Waveform depends on style
        if style == 'melodic':
            # Sine with slight 2nd harmonic
            val = math.sin(2 * math.pi * freq * t)
            val += 0.15 * math.sin(4 * math.pi * freq * t)
        elif style == 'ambient':
            # Soft sine with slow vibrato
            vibrato = 0.003 * math.sin(2 * math.pi * 4.5 * t)
            val = math.sin(2 * math.pi * freq * (1 + vibrato) * t)
            val += 0.1 * math.sin(2 * math.pi * freq * 2.01 * t)  # slight detuning
        elif style == 'percussive':
            # Triangle-ish wave, fast decay
            phase = (freq * t) % 1.0
            val = 4 * abs(phase - 0.5) - 1
            env *= max(0, 1.0 - t / (duration * 0.5))  # extra fast decay
        elif style == 'choral':
            # Multiple detuned sines (chorus effect)
            val = 0
            for detune in [-0.005, -0.002, 0, 0.002, 0.005]:
                val += 0.2 * math.sin(2 * math.pi * freq * (1 + detune) * t)
        else:
            val = math.sin(2 * math.pi * freq * t)

        samples.append(val * env * amplitude)

    return samples


def text_to_notes(text, scale_name='major', root=60):
    """Convert text to a sequence of (midi_note, duration, amplitude) tuples."""
    scale = SCALES.get(scale_name, SCALES['major'])
    text_lower = text.lower()
    notes = []
    current_degree = 0
    last_was_space = False

    for i, ch in enumerate(text_lower):
        if ch in VOWEL_DEGREES:
            # Vowels set the pitch
            degree_offset = VOWEL_DEGREES[ch]
            # Context: position in text affects octave
            position_octave = (i * len(scale)) // max(len(text_lower), 1)
            current_degree = degree_offset + position_octave
            midi = scale_note(current_degree, scale, root)
            # Duration from surrounding consonants
            dur = 0.25  # base duration for vowels
            amp = CHAR_ENERGY.get(ch, 0.6)
            notes.append((midi, dur, amp))
            last_was_space = False

        elif ch.isalpha():
            # Consonants modify duration of next/prev note or add percussion
            dur_factor = CONSONANT_DURATION.get(ch, 0.7)
            if notes:
                # Modify previous note's duration
                prev = notes[-1]
                notes[-1] = (prev[0], prev[1] * dur_factor, prev[2])
            last_was_space = False

        elif ch == ' ':
            if not last_was_space:
                # Space = rest
                notes.append((0, 0.12, 0))  # rest
                last_was_space = True

        elif ch in '.,;:!?':
            # Punctuation = longer rest + dynamic change
            rest_dur = {'.': 0.3, ',': 0.15, ';': 0.2, ':': 0.2, '!': 0.35, '?': 0.4}
            notes.append((0, rest_dur.get(ch, 0.2), 0))
            last_was_space = True

        elif ch.isdigit():
            # Digits map to specific scale degrees
            degree = int(ch) % len(scale)
            midi = scale_note(degree, scale, root)
            notes.append((midi, 0.2, 0.6))
            last_was_space = False

    return notes


def add_reverb(samples, delay_ms=80, decay=0.3):
    """Simple delay-based reverb."""
    delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
    output = list(samples)
    for i in range(delay_samples, len(output)):
        output[i] += output[i - delay_samples] * decay
    return output


def normalize(samples):
    """Normalize samples to MAX_AMPLITUDE."""
    if not samples:
        return samples
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return samples
    factor = MAX_AMPLITUDE / peak
    return [s * factor for s in samples]


def compose(text, scale_name='major', tempo=120, style='melodic', root=60):
    """
    Compose a piece of music from text.

    Returns a list of audio samples.
    """
    notes = text_to_notes(text, scale_name, root)

    # Tempo adjustment: base duration is at 120 BPM
    tempo_factor = 120.0 / tempo

    samples = []
    for midi, dur, amp in notes:
        dur *= tempo_factor
        if midi == 0 or amp == 0:
            # Rest
            samples.extend([0.0] * int(SAMPLE_RATE * dur))
        else:
            freq = note_freq(midi)
            tone = generate_tone(freq, dur, amp, style)
            samples.extend(tone)

    # Add reverb
    samples = add_reverb(samples, delay_ms=100, decay=0.25)

    # Normalize
    samples = normalize(samples)

    return samples


def save_wav(samples, filename):
    """Save samples to a WAV file."""
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            wf.writeframes(struct.pack('<h', int(clamped * 32767)))


def render_score(text, scale_name='major', root=60):
    """
    Render a visual score of the composition.
    Shows pitch as vertical position, time as horizontal.
    """
    notes = text_to_notes(text, scale_name, root)
    if not notes:
        return "Empty score -- no notes generated."

    # Find pitch range
    pitches = [n[0] for n in notes if n[0] > 0]
    if not pitches:
        return "Silent score -- all rests."

    min_pitch = min(pitches)
    max_pitch = max(pitches)
    pitch_range = max(max_pitch - min_pitch, 1)

    # Score dimensions
    height = 16
    width = min(len(notes), 120)

    # Build grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Note characters by amplitude
    def note_char(amp):
        if amp >= 0.9:
            return '#'
        elif amp >= 0.7:
            return 'O'
        elif amp >= 0.5:
            return 'o'
        elif amp >= 0.3:
            return '.'
        else:
            return ','

    # Place notes
    for i, (midi, dur, amp) in enumerate(notes[:width]):
        if midi == 0:
            # Rest: mark bottom row
            grid[height - 1][i] = '_'
        else:
            row = height - 1 - int((midi - min_pitch) / pitch_range * (height - 1))
            row = max(0, min(height - 1, row))
            grid[row][i] = note_char(amp)

    # Render
    lines = []
    lines.append(f"  Score: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
    lines.append(f"  Scale: {scale_name} | Notes: {len(notes)} | Pitches: {len(pitches)}")
    lines.append("")

    # Note names for left margin
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    for r in range(height):
        # Left margin: pitch indicator
        pitch_at_row = max_pitch - int(r * pitch_range / (height - 1)) if height > 1 else min_pitch
        name = note_names[pitch_at_row % 12]
        octave = pitch_at_row // 12 - 1
        margin = f"{name}{octave:>1}".rjust(4)
        row_str = ''.join(grid[r])
        lines.append(f"  {margin} |{row_str}|")

    lines.append(f"       +{'-' * width}+")

    # Legend
    lines.append("")
    lines.append("  # = loud  O = medium  o = soft  . = quiet  , = whisper  _ = rest")

    return '\n'.join(lines)


def analyze_composition(text, scale_name='major'):
    """Analyze the musical properties of a text."""
    notes = text_to_notes(text, scale_name)
    if not notes:
        return "No notes to analyze."

    total_notes = len(notes)
    pitched = [(m, d, a) for m, d, a in notes if m > 0]
    rests = [(m, d, a) for m, d, a in notes if m == 0]

    total_duration = sum(d for _, d, _ in notes)
    avg_amplitude = sum(a for _, _, a in pitched) / max(len(pitched), 1)

    # Interval analysis
    intervals = []
    for i in range(1, len(pitched)):
        intervals.append(pitched[i][0] - pitched[i - 1][0])

    avg_interval = sum(abs(iv) for iv in intervals) / max(len(intervals), 1)
    leaps = sum(1 for iv in intervals if abs(iv) > 4)
    steps = sum(1 for iv in intervals if 0 < abs(iv) <= 2)

    lines = []
    lines.append(f"  Composition Analysis: \"{text[:40]}{'...' if len(text) > 40 else ''}\"")
    lines.append(f"  Scale: {scale_name}")
    lines.append(f"  Total events: {total_notes} ({len(pitched)} notes, {len(rests)} rests)")
    lines.append(f"  Duration: ~{total_duration:.1f}s at 120 BPM")
    lines.append(f"  Average amplitude: {avg_amplitude:.2f}")
    lines.append(f"  Average interval: {avg_interval:.1f} semitones")
    lines.append(f"  Steps (1-2 semitones): {steps} | Leaps (>4): {leaps}")

    if pitched:
        pitch_range = max(m for m, _, _ in pitched) - min(m for m, _, _ in pitched)
        lines.append(f"  Pitch range: {pitch_range} semitones")

    # Character
    if avg_interval < 2:
        character = "smooth and stepwise -- like speech"
    elif avg_interval < 4:
        character = "gently melodic -- like a folk song"
    elif avg_interval < 7:
        character = "dramatic -- wide intervals, bold gestures"
    else:
        character = "angular and unpredictable -- like avant-garde jazz"

    rest_ratio = len(rests) / max(total_notes, 1)
    if rest_ratio > 0.3:
        character += ", with lots of breath"
    elif rest_ratio < 0.1:
        character += ", dense and continuous"

    lines.append(f"  Character: {character}")

    return '\n'.join(lines)


def print_header():
    """Print the composer header."""
    print("""
  ╔══════════════════════════════════════════╗
  ║          T H E   C O M P O S E R        ║
  ║                                          ║
  ║    text in, music out                    ║
  ║    session 22                            ║
  ╚══════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(
        description='The Composer: turn any text into music.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 composer.py "hello world"
  python3 composer.py "the house remembers" --scale minor --style ambient
  python3 composer.py "From simple rules complexity arises" --export complexity.wav
  python3 composer.py "your name here" --score
        """
    )
    parser.add_argument('text', nargs='?', help='Text to compose from')
    parser.add_argument('--scale', default='major', choices=SCALES.keys(),
                        help='Musical scale (default: major)')
    parser.add_argument('--tempo', type=int, default=120,
                        help='Tempo in BPM (default: 120)')
    parser.add_argument('--style', default='melodic',
                        choices=['melodic', 'ambient', 'percussive', 'choral'],
                        help='Tonal style (default: melodic)')
    parser.add_argument('--root', type=int, default=60,
                        help='Root MIDI note (default: 60 = middle C)')
    parser.add_argument('--export', metavar='FILE',
                        help='Export to WAV file')
    parser.add_argument('--score', action='store_true',
                        help='Display visual score')
    parser.add_argument('--analyze', action='store_true',
                        help='Show composition analysis')
    parser.add_argument('--demo', action='store_true',
                        help='Run demo with sample texts')

    args = parser.parse_args()
    print_header()

    if args.demo:
        demo_texts = [
            ("the house remembers what the mind forgets", "minor", "ambient"),
            ("From simple rules complexity arises", "pentatonic", "melodic"),
            ("Hello, World!", "major", "melodic"),
            ("branch-light bloomed once, then was gone", "dorian", "choral"),
            ("0123456789", "chromatic", "percussive"),
        ]
        for text, scale, style in demo_texts:
            print(f"  --- \"{text}\" [{scale}, {style}] ---\n")
            print(analyze_composition(text, scale))
            print()
            print(render_score(text, scale))
            print("\n")
        return

    if not args.text:
        parser.print_help()
        return

    text = args.text

    # Analysis
    if args.analyze or args.score:
        print(analyze_composition(text, args.scale))
        print()

    # Score
    if args.score:
        print(render_score(text, args.scale, args.root))
        print()

    # Compose
    print(f"  Composing from: \"{text}\"")
    print(f"  Scale: {args.scale} | Tempo: {args.tempo} BPM | Style: {args.style}")

    samples = compose(text, args.scale, args.tempo, args.style, args.root)
    duration = len(samples) / SAMPLE_RATE

    print(f"  Duration: {duration:.1f}s ({len(samples)} samples)")

    # Export
    if args.export:
        save_wav(samples, args.export)
        print(f"  Saved to: {args.export}")
    else:
        # Default export
        safe_name = ''.join(c if c.isalnum() else '_' for c in text[:30]).strip('_')
        filename = f"composed_{safe_name}.wav"
        save_wav(samples, filename)
        print(f"  Saved to: {filename}")

    print()
    print("  The text has been heard. The music remembers.")
    print()


if __name__ == '__main__':
    main()
