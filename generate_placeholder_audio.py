"""
generate_placeholder_audio.py — Audio File Generator
======================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Creates placeholder .wav files in assets/audio/ so the game
          can load without errors.  Each file contains a short sine‑wave
          tone (SFX) or longer tone (music) at different frequencies.

Run once:
    python generate_placeholder_audio.py

After real sound design is ready, replace the .wav files in assets/audio/.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import os      # directory creation
import struct  # binary packing for WAV format
import math    # sin() for tone generation

# ── Output directory ───────────────────────────────────────────────────── #
AUDIO_DIR = os.path.join('assets', 'audio')

# ── WAV parameters ─────────────────────────────────────────────────────── #
SAMPLE_RATE = 22050   # lower rate for smaller files
CHANNELS    = 1       # mono
BITS        = 16      # 16‑bit audio
MAX_AMP     = 16000   # amplitude (not clipping at 32767)


def generate_wav(filename, duration_s, frequency_hz, volume=0.5):
    """
    Write a mono 16‑bit WAV file with a sine‑wave tone.

    Args:
        filename     : str   — output path (e.g. 'assets/audio/click.wav')
        duration_s   : float — length in seconds
        frequency_hz : float — tone frequency (Hz)
        volume       : float — amplitude scale (0.0–1.0)
    """
    num_samples = int(SAMPLE_RATE * duration_s)   # total samples
    amp         = int(MAX_AMP * volume)            # scaled amplitude

    # Generate samples
    samples = []
    for i in range(num_samples):
        t = i / SAMPLE_RATE   # time in seconds
        # Sine wave with fade‑in/out envelope
        envelope = 1.0
        fade_len = min(0.02, duration_s * 0.1)   # 20ms or 10% of duration
        if t < fade_len:
            envelope = t / fade_len               # fade in
        elif t > duration_s - fade_len:
            envelope = (duration_s - t) / fade_len  # fade out

        val = int(amp * envelope * math.sin(2 * math.pi * frequency_hz * t))
        samples.append(val)

    # Pack samples as signed 16‑bit little‑endian
    data = struct.pack(f'<{num_samples}h', *samples)

    # WAV header
    data_size = num_samples * CHANNELS * (BITS // 8)
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',
        36 + data_size,       # file size - 8
        b'WAVE',
        b'fmt ',
        16,                   # chunk size
        1,                    # PCM format
        CHANNELS,
        SAMPLE_RATE,
        SAMPLE_RATE * CHANNELS * (BITS // 8),  # byte rate
        CHANNELS * (BITS // 8),                 # block align
        BITS,
        b'data',
        data_size,
    )

    # Write the file
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(data)


# ══════════════════════════════════════════════════════════════════════════ #
#  File definitions — (name, duration, frequency, volume)
# ══════════════════════════════════════════════════════════════════════════ #
AUDIO_FILES = [
    # ── Music (longer, lower tones) ──────────────────────────────────── #
    ('menu_loop',       4.0, 120, 0.3),     # low ambient drone
    ('cyber_ambient',   4.0, 100, 0.25),    # deep ambient hum
    ('tense_loop',      4.0, 180, 0.35),    # tense higher tone

    # ── UI sounds ────────────────────────────────────────────────────── #
    ('click',           0.1, 800, 0.4),     # short high click
    ('slider',          0.15, 600, 0.3),    # slider tick
    ('inventory_toggle', 0.2, 500, 0.35),   # panel open/close
    ('pickup',          0.25, 900, 0.4),    # item collected

    # ── Hacking sounds ───────────────────────────────────────────────── #
    ('terminal_on',     0.3, 440, 0.4),     # terminal activated
    ('key_press',       0.08, 1000, 0.35),  # key tap
    ('hack_success',    0.5, 660, 0.5),     # success chime
    ('hack_fail',       0.3, 220, 0.5),     # failure buzz

    # ── Drone sounds ─────────────────────────────────────────────────── #
    ('drone_alert',     0.4, 350, 0.4),     # suspicious ping
    ('drone_chase',     0.3, 500, 0.5),     # alert escalation
    ('drone_hit',       0.15, 150, 0.5),    # damage thud
    ('drone_disabled',  0.6, 80, 0.5),      # EMP shutdown

    # ── Player sounds ────────────────────────────────────────────────── #
    ('footstep1',       0.1, 200, 0.3),     # step variant 1
    ('footstep2',       0.1, 220, 0.3),     # step variant 2
    ('jump',            0.2, 400, 0.35),    # jump whoosh
    ('land',            0.15, 160, 0.4),    # landing thud

    # ── Mission sounds ───────────────────────────────────────────────── #
    ('extract',          0.4, 550, 0.4),    # extraction zone
    ('mission_complete', 0.8, 880, 0.5),    # victory fanfare
    ('mission_fail',     0.6, 130, 0.5),    # failure drone
]


# ══════════════════════════════════════════════════════════════════════════ #
#  Main — generate all files
# ══════════════════════════════════════════════════════════════════════════ #
if __name__ == '__main__':
    # Create the output directory if it doesn't exist
    os.makedirs(AUDIO_DIR, exist_ok=True)
    print(f'Generating {len(AUDIO_FILES)} audio files in {AUDIO_DIR}/')
    print('─' * 50)

    for name, duration, freq, vol in AUDIO_FILES:
        filepath = os.path.join(AUDIO_DIR, f'{name}.wav')
        generate_wav(filepath, duration, freq, vol)
        size_kb = os.path.getsize(filepath) / 1024
        print(f'  ✓ {name}.wav  ({duration:.1f}s, {freq}Hz, {size_kb:.1f}KB)')

    print('─' * 50)
    print(f'Done! {len(AUDIO_FILES)} placeholder files generated.')
    print('Replace with real sound assets when ready.')
