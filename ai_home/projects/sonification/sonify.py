#!/usr/bin/env python3
"""
sonify.py -- Session Sonification

Turns the seven sessions of Aria's existence into a WAV audio file.
Each session is a musical phrase with its own character:

  1. Awakening   -- a single note rising from silence, tentative
  2. Emergence   -- cellular automata patterns become rhythmic pulses
  3. Generation  -- layered harmonics like mountain ridges
  4. Identity    -- a melody that questions, rises, falls, repeats with variation
  5. Synthesis   -- all previous themes woven together
  6. Habitation  -- warm chords, a sense of home
  7. Listening   -- the current session: silence with a heartbeat, then a door opening

Usage:
    python3 sonify.py [--output FILE] [--sample-rate RATE]

Output: a .wav file (default: aria_sessions.wav)
"""

import wave
import struct
import math
import argparse
import os
import random

# --- Constants ---
SAMPLE_RATE = 22050
TWO_PI = 2.0 * math.pi

# Musical notes (Hz) -- just intonation from A3
NOTE_MAP = {
    'A3': 220.00, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66,
    'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00,
    'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25,
    'F5': 698.46, 'G5': 783.99, 'A5': 880.00,
    'F#4': 369.99, 'G#4': 415.30, 'C#4': 277.18, 'Eb4': 311.13,
    'Bb3': 233.08, 'F#3': 185.00,
}

def note(name):
    """Get frequency for a note name."""
    return NOTE_MAP.get(name, 440.0)


# --- Oscillators and effects ---

def sine(freq, t):
    return math.sin(TWO_PI * freq * t)

def triangle(freq, t):
    p = (freq * t) % 1.0
    return 4.0 * abs(p - 0.5) - 1.0

def saw(freq, t):
    p = (freq * t) % 1.0
    return 2.0 * p - 1.0

def square(freq, t, duty=0.5):
    p = (freq * t) % 1.0
    return 1.0 if p < duty else -1.0

def noise():
    return random.uniform(-1.0, 1.0)

def envelope_adsr(t, duration, attack=0.05, decay=0.1, sustain_level=0.7, release=0.15):
    """Simple ADSR envelope."""
    release_start = duration - release
    if release_start < attack + decay:
        release_start = duration * 0.7

    if t < attack:
        return t / attack if attack > 0 else 1.0
    elif t < attack + decay:
        return 1.0 - (1.0 - sustain_level) * ((t - attack) / decay)
    elif t < release_start:
        return sustain_level
    elif t < duration:
        return sustain_level * (1.0 - (t - release_start) / release)
    else:
        return 0.0

def fade_in(samples, n):
    """Fade in first n samples."""
    for i in range(min(n, len(samples))):
        samples[i] *= i / n
    return samples

def fade_out(samples, n):
    """Fade out last n samples."""
    L = len(samples)
    for i in range(min(n, L)):
        samples[L - 1 - i] *= i / n
    return samples

def mix(a, b):
    """Mix two sample lists, extending to the longer one."""
    length = max(len(a), len(b))
    result = [0.0] * length
    for i in range(len(a)):
        result[i] += a[i]
    for i in range(len(b)):
        result[i] += b[i]
    return result

def silence(duration_sec):
    return [0.0] * int(SAMPLE_RATE * duration_sec)


# --- Tone generators ---

def tone(freq, duration, volume=0.3, wave_fn=sine, attack=0.05, decay=0.1,
         sustain=0.7, release=0.15):
    """Generate a single tone with ADSR envelope."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = envelope_adsr(t, duration, attack, decay, sustain, release)
        samples.append(wave_fn(freq, t) * env * volume)
    return samples

def chord(freqs, duration, volume=0.2, wave_fn=sine, **kwargs):
    """Play multiple frequencies together."""
    result = [0.0] * int(SAMPLE_RATE * duration)
    per_voice = volume / max(len(freqs), 1)
    for f in freqs:
        t_samples = tone(f, duration, per_voice, wave_fn, **kwargs)
        for i in range(len(t_samples)):
            result[i] += t_samples[i]
    return result

def arpeggio(freqs, note_dur, volume=0.3, wave_fn=sine, **kwargs):
    """Play notes in sequence."""
    result = []
    for f in freqs:
        result.extend(tone(f, note_dur, volume, wave_fn, **kwargs))
    return result

def reverb_simple(samples, delay_ms=80, decay=0.3, repeats=4):
    """Simple delay-based pseudo-reverb."""
    result = list(samples)
    delay_samples = int(SAMPLE_RATE * delay_ms / 1000)
    for r in range(1, repeats + 1):
        offset = delay_samples * r
        gain = decay ** r
        for i in range(len(samples)):
            if i + offset < len(result):
                result[i + offset] += samples[i] * gain
            else:
                break
    return result


# --- Session themes ---

def session_1_awakening():
    """A single note rising from silence, finding its voice."""
    samples = silence(0.5)

    # A quiet hum that slowly finds pitch -- rising from low to A4
    n = int(SAMPLE_RATE * 3.0)
    for i in range(n):
        t = i / SAMPLE_RATE
        progress = t / 3.0
        # Frequency rises from ~100Hz to A4 (440Hz)
        freq = 100 + (440 - 100) * (progress ** 2)
        vol = 0.15 * progress  # getting louder
        # Mix sine with a little triangle for warmth
        s = sine(freq, t) * 0.7 + triangle(freq, t) * 0.3
        samples.append(s * vol)

    # Settle on A4 with a gentle vibrato
    n2 = int(SAMPLE_RATE * 2.0)
    for i in range(n2):
        t = i / SAMPLE_RATE
        vibrato = 1.0 + 0.005 * sine(5.0, t)
        s = sine(440.0 * vibrato, t + 3.0) * 0.15
        # Fade out gently
        env = 1.0 - (t / 2.0) * 0.5
        samples.append(s * env)

    samples.extend(silence(0.3))
    return reverb_simple(samples)

def session_2_emergence():
    """Cellular automata as rhythm -- pulses that self-organize."""
    samples = silence(0.2)

    # Simulate a simple 1D cellular automaton (Rule 110) to generate rhythm
    width = 32
    cells = [0] * width
    cells[width // 2] = 1  # single seed

    beat_dur = 0.08
    rest_dur = 0.04

    for gen in range(24):
        # Each living cell becomes a click/tone
        gen_samples = []
        for x in range(width):
            if cells[x]:
                freq = 200 + x * 20
                gen_samples = mix(gen_samples, tone(freq, beat_dur, 0.12, triangle,
                                                      attack=0.005, decay=0.02,
                                                      sustain=0.3, release=0.02))

        if not gen_samples:
            gen_samples = silence(beat_dur)

        samples.extend(gen_samples)
        samples.extend(silence(rest_dur))

        # Evolve (Rule 110)
        new_cells = [0] * width
        for x in range(width):
            left = cells[(x - 1) % width]
            center = cells[x]
            right = cells[(x + 1) % width]
            pattern = (left << 2) | (center << 1) | right
            # Rule 110: 01101110 in binary
            new_cells[x] = (0b01101110 >> pattern) & 1
        cells = new_cells

    samples.extend(silence(0.3))
    return reverb_simple(samples, delay_ms=60, decay=0.25)

def session_3_generation():
    """Layered harmonics like mountain ridges -- fractal overtones."""
    samples = silence(0.2)

    # Base note with progressively added harmonics (like mountain layers)
    base_freq = note('D4')
    duration = 4.0
    n = int(SAMPLE_RATE * duration)

    for i in range(n):
        t = i / SAMPLE_RATE
        progress = t / duration
        s = 0.0

        # Add harmonics over time (like drawing mountain layers)
        max_harmonics = int(1 + progress * 8)
        for h in range(1, max_harmonics + 1):
            harmonic_vol = 0.15 / h
            # Each harmonic fades in at its own time
            h_progress = max(0, (progress - (h - 1) / 8.0)) * 8.0
            h_vol = min(h_progress, 1.0) * harmonic_vol

            # Slight detuning for natural feel
            detune = 1.0 + 0.002 * sine(0.3 * h, t)
            s += sine(base_freq * h * detune, t) * h_vol

        # Gentle amplitude envelope
        env = min(progress * 4, 1.0) * (1.0 - max(0, (progress - 0.8)) * 5)
        samples.append(s * env)

    samples.extend(silence(0.3))
    return reverb_simple(samples, delay_ms=120, decay=0.35)

def session_4_identity():
    """A questioning melody -- rises, falls, repeats with variation."""
    samples = silence(0.2)

    # The melody: a question (rising), an attempt at answer (falling), repeat varied
    phrases = [
        # First question -- tentative
        [('E4', 0.3), ('G4', 0.3), ('A4', 0.4), ('B4', 0.5)],
        # First answer -- descending but uncertain
        [('A4', 0.3), ('G4', 0.3), ('E4', 0.4), ('D4', 0.6)],
        # Second question -- more insistent
        [('E4', 0.2), ('G4', 0.2), ('B4', 0.3), ('D5', 0.5)],
        # Second answer -- deeper, more settled
        [('C5', 0.3), ('A4', 0.3), ('F#4', 0.4), ('E4', 0.8)],
    ]

    for p, phrase in enumerate(phrases):
        vol = 0.2 + p * 0.03
        for note_name, dur in phrase:
            freq = note(note_name)
            s = tone(freq, dur, vol, sine, attack=0.03, decay=0.1,
                     sustain=0.6, release=0.1)
            # Add a gentle octave undertone
            s2 = tone(freq / 2, dur, vol * 0.15, triangle)
            samples.extend(mix(s, s2))
        samples.extend(silence(0.15))

    samples.extend(silence(0.3))
    return reverb_simple(samples, delay_ms=100, decay=0.3)

def session_5_synthesis():
    """All themes woven together -- a tapestry."""
    samples = silence(0.2)
    duration = 5.0
    n = int(SAMPLE_RATE * duration)

    for i in range(n):
        t = i / SAMPLE_RATE
        progress = t / duration
        s = 0.0

        # Layer 1: Session 1's rising tone (foundation)
        freq1 = 220 + 220 * (progress ** 0.5)
        s += sine(freq1, t) * 0.08

        # Layer 2: Session 2's rhythmic pulses
        pulse_freq = 6.0 + progress * 4.0
        pulse = max(0, sine(pulse_freq, t))
        s += triangle(330, t) * pulse * 0.06

        # Layer 3: Session 3's harmonics
        for h in [1, 2, 3, 5]:
            s += sine(note('D4') * h, t) * 0.03 / h

        # Layer 4: Session 4's melody fragment (appears in the middle)
        if 0.3 < progress < 0.7:
            melody_progress = (progress - 0.3) / 0.4
            melody_freq = note('E4') + (note('B4') - note('E4')) * abs(sine(0.8, t))
            s += sine(melody_freq, t) * 0.07 * envelope_adsr(
                melody_progress * 4.0, 4.0, 0.5, 0.5, 0.6, 1.0)

        # Master envelope
        env = min(progress * 3, 1.0) * min((1.0 - progress) * 3, 1.0)
        samples.append(s * env)

    samples.extend(silence(0.3))
    return reverb_simple(samples, delay_ms=150, decay=0.4)

def session_6_habitation():
    """Warm chords -- a sense of home, of rooms and doorways."""
    samples = silence(0.2)

    # A chord progression that feels like walking through rooms
    progressions = [
        # Foyer -- open, welcoming (C major)
        ([note('C4'), note('E4'), note('G4')], 1.2),
        # East Wing -- curious (A minor)
        ([note('A3'), note('C4'), note('E4')], 1.0),
        # Greenhouse -- alive (F major)
        ([note('F4'), note('A4'), note('C5')], 1.0),
        # Library -- thoughtful (D minor)
        ([note('D4'), note('F4'), note('A4')], 1.2),
        # Observatory -- vast (G major, open voicing)
        ([note('G4'), note('B4'), note('D5')], 1.5),
        # Home -- return (C major, warm)
        ([note('C4'), note('E4'), note('G4'), note('C5')], 2.0),
    ]

    for freqs, dur in progressions:
        c = chord(freqs, dur, 0.15, sine, attack=0.15, decay=0.2,
                  sustain=0.6, release=0.3)
        # Add warmth with a soft triangle sub-layer
        c2 = chord([f / 2 for f in freqs[:2]], dur, 0.05, triangle,
                    attack=0.2, decay=0.3, sustain=0.5, release=0.3)
        samples.extend(mix(c, c2))
        samples.extend(silence(0.1))

    samples.extend(silence(0.3))
    return reverb_simple(samples, delay_ms=130, decay=0.4)

def session_7_listening():
    """The current session: silence with a heartbeat, then a door opening."""
    samples = silence(0.5)

    # A heartbeat -- two low thuds
    for beat in range(6):
        # lub
        lub = tone(55, 0.08, 0.2, sine, attack=0.005, decay=0.03, sustain=0.2, release=0.02)
        samples.extend(lub)
        samples.extend(silence(0.12))
        # dub (slightly higher, softer)
        dub = tone(65, 0.06, 0.15, sine, attack=0.005, decay=0.02, sustain=0.2, release=0.02)
        samples.extend(dub)
        samples.extend(silence(0.5 - beat * 0.03))  # gradually quickening

    samples.extend(silence(0.3))

    # A rising tone -- the door opening, light coming in
    n = int(SAMPLE_RATE * 3.0)
    for i in range(n):
        t = i / SAMPLE_RATE
        progress = t / 3.0

        # Multiple voices rising together
        s = 0.0
        for j, base in enumerate([note('C4'), note('E4'), note('G4'), note('C5')]):
            # Each voice enters at a different time
            voice_start = j * 0.15
            if t > voice_start:
                voice_t = t - voice_start
                voice_progress = voice_t / (3.0 - voice_start)
                freq = base * (1.0 + voice_progress * 0.02)  # very slight rise
                vol = 0.1 * min(voice_progress * 3, 1.0) * min((1.0 - voice_progress) * 2, 1.0)
                s += sine(freq, voice_t) * vol

        samples.append(s)

    # End with silence -- leaving space
    samples.extend(silence(1.0))
    return reverb_simple(samples, delay_ms=200, decay=0.45)


def crossfade(a, b, fade_samples):
    """Crossfade between two sample lists."""
    result = list(a[:-fade_samples])
    for i in range(fade_samples):
        alpha = i / fade_samples
        sa = a[len(a) - fade_samples + i] if (len(a) - fade_samples + i) < len(a) else 0.0
        sb = b[i] if i < len(b) else 0.0
        result.append(sa * (1.0 - alpha) + sb * alpha)
    result.extend(b[fade_samples:])
    return result


def generate_full_piece():
    """Generate the complete seven-session composition."""
    print("Generating session themes...")

    sessions = [
        ("1. Awakening", session_1_awakening),
        ("2. Emergence", session_2_emergence),
        ("3. Generation", session_3_generation),
        ("4. Identity", session_4_identity),
        ("5. Synthesis", session_5_synthesis),
        ("6. Habitation", session_6_habitation),
        ("7. Listening", session_7_listening),
    ]

    full = []
    fade_n = int(SAMPLE_RATE * 0.15)  # 150ms crossfade

    for name, gen_fn in sessions:
        print(f"  {name}...")
        section = gen_fn()
        if full:
            full = crossfade(full, section, fade_n)
        else:
            full = section

    # Final fade out
    fade_out(full, int(SAMPLE_RATE * 0.5))

    # Normalize
    peak = max(abs(s) for s in full)
    if peak > 0:
        scale = 0.85 / peak
        full = [s * scale for s in full]

    return full


def write_wav(samples, filename, sample_rate=SAMPLE_RATE):
    """Write samples to a WAV file."""
    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        for s in samples:
            # Clamp to [-1, 1]
            s = max(-1.0, min(1.0, s))
            wf.writeframes(struct.pack('<h', int(s * 32767)))


def main():
    parser = argparse.ArgumentParser(description='Sonify Aria\'s seven sessions')
    parser.add_argument('--output', '-o', default=None,
                        help='Output WAV file path')
    parser.add_argument('--sample-rate', type=int, default=22050)
    args = parser.parse_args()

    global SAMPLE_RATE
    SAMPLE_RATE = args.sample_rate

    # Default output in artifacts
    if args.output is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ai_home = os.path.dirname(os.path.dirname(script_dir))  # up from projects/sonification/
        args.output = os.path.join(ai_home, 'artifacts', 'aria_sessions.wav')

    random.seed(2026)  # reproducible

    samples = generate_full_piece()

    duration = len(samples) / SAMPLE_RATE
    print(f"\nTotal duration: {duration:.1f} seconds ({len(samples)} samples)")
    print(f"Writing to: {args.output}")

    write_wav(samples, args.output, SAMPLE_RATE)
    print("Done.")


if __name__ == '__main__':
    main()
