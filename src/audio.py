"""
audio.py — Audio Manager Module (Phase 7)
============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides a centralised AudioManager that handles:
            • Background music with looping and track switching
            • One‑shot sound effects (SFX)
            • Volume control per channel (master / music / sfx)
            • Graceful fallback — missing files warn but never crash

How it connects:
    scenes.py creates one AudioManager at startup.
    Other modules receive an audio_manager reference and call
    play_sfx(name) or play_music(track) as needed.

Ursina notes:
    Ursina's Audio() class handles .wav and .ogg playback.
    We wrap it so the rest of the codebase doesn't import Ursina audio.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import os   # path joining and file existence checks

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import Audio, destroy as ursina_destroy

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    AUDIO_DIR,               # base folder: 'assets/audio'
    AUDIO_MASTER_VOLUME,     # default master volume
    AUDIO_MUSIC_VOLUME,      # default music volume
    AUDIO_SFX_VOLUME,        # default sfx volume
)


# ══════════════════════════════════════════════════════════════════════════ #
#  AudioManager class
# ══════════════════════════════════════════════════════════════════════════ #
class AudioManager:
    """
    Centralised audio controller for music and sound effects.

    Attributes:
        volumes       : dict  — {master, music, sfx} volume levels (0–1)
        _current_music : Audio or None — currently playing music track
        _music_name    : str  — name of the active music track
    """

    def __init__(self):
        """Initialise with default volumes and no active music."""
        # Volume channels (0.0 = silent, 1.0 = max)
        self.volumes = {
            'master': AUDIO_MASTER_VOLUME,   # overall volume
            'music':  AUDIO_MUSIC_VOLUME,    # music channel
            'sfx':    AUDIO_SFX_VOLUME,      # sound effects channel
        }

        # Currently playing music track
        self._current_music = None   # Ursina Audio instance
        self._music_name    = ''     # track name for comparison

    # ================================================================== #
    #  INTERNAL — resolve file path
    # ================================================================== #
    def _resolve_path(self, name):
        """
        Build the full relative path for an audio file.

        Tries .wav first, then .ogg.  Returns None if neither exists.

        Args:
            name : str — base filename without extension (e.g. 'click')

        Returns:
            str or None — relative path to the audio file
        """
        # Try .wav first (most common for SFX)
        wav_path = os.path.join(AUDIO_DIR, f'{name}.wav')
        if os.path.isfile(wav_path):
            return wav_path   # found .wav

        # Try .ogg as fallback (better for music)
        ogg_path = os.path.join(AUDIO_DIR, f'{name}.ogg')
        if os.path.isfile(ogg_path):
            return ogg_path   # found .ogg

        # File not found — will be handled gracefully by callers
        return None

    # ================================================================== #
    #  EFFECTIVE VOLUME — combines master with channel
    # ================================================================== #
    def _effective_volume(self, channel):
        """
        Calculate the effective volume for a channel.

        Args:
            channel : str — 'music' or 'sfx'

        Returns:
            float — master × channel volume (0.0–1.0)
        """
        master  = self.volumes.get('master', 1.0)   # overall volume
        ch_vol  = self.volumes.get(channel, 1.0)     # channel volume
        return master * ch_vol   # combined volume

    # ================================================================== #
    #  MUSIC — looping background tracks
    # ================================================================== #
    def play_music(self, track_name, loop=True):
        """
        Start playing a background music track.

        If the requested track is already playing, do nothing.
        Otherwise, stop the current track and start the new one.

        Args:
            track_name : str  — base name (e.g. 'menu_loop')
            loop       : bool — whether to loop the track
        """
        # Skip if already playing this track
        if track_name == self._music_name and self._current_music is not None:
            return   # same track — no change

        # Stop current music first
        self.stop_music()

        # Resolve the file path
        path = self._resolve_path(track_name)
        if path is None:
            print(f'[AudioManager] Music file not found: {track_name}')
            return   # graceful fallback — no crash

        # Create and play the Ursina Audio instance
        try:
            vol = self._effective_volume('music')   # combined volume
            self._current_music = Audio(
                path,
                loop=loop,          # repeat indefinitely
                autoplay=True,      # start immediately
                volume=vol,         # set volume level
            )
            self._music_name = track_name   # remember current track
        except Exception as e:
            print(f'[AudioManager] Error playing music {track_name}: {e}')

    def stop_music(self):
        """Stop the currently playing music track."""
        if self._current_music is not None:
            try:
                self._current_music.stop()    # halt playback
                ursina_destroy(self._current_music)  # clean up entity
            except Exception:
                pass   # ignore errors during cleanup
            self._current_music = None   # clear reference
            self._music_name    = ''     # clear name

    # ================================================================== #
    #  SFX — one‑shot sound effects
    # ================================================================== #
    def play_sfx(self, sfx_name):
        """
        Play a one‑shot sound effect.

        Args:
            sfx_name : str — base name (e.g. 'click', 'hack_success')
        """
        # Resolve the file path
        path = self._resolve_path(sfx_name)
        if path is None:
            # Silently skip missing SFX — don't spam the console
            return   # graceful fallback

        # Play the sound effect
        try:
            vol = self._effective_volume('sfx')   # combined volume
            Audio(
                path,
                loop=False,        # one‑shot — play once
                autoplay=True,     # start immediately
                auto_destroy=True, # auto‑cleanup after playback
                volume=vol,        # set volume level
            )
        except Exception:
            pass   # ignore playback errors silently

    # ================================================================== #
    #  VOLUME CONTROL
    # ================================================================== #
    def set_volume(self, channel, value):
        """
        Adjust a volume channel.

        Args:
            channel : str   — 'master', 'music', or 'sfx'
            value   : float — new volume (0.0–1.0)
        """
        # Clamp to valid range
        value = max(0.0, min(1.0, value))
        self.volumes[channel] = value   # store the new level

        # If music is playing, update its volume immediately
        if channel in ('master', 'music') and self._current_music:
            try:
                self._current_music.volume = self._effective_volume('music')
            except Exception:
                pass   # ignore errors

    # ================================================================== #
    #  CLEANUP
    # ================================================================== #
    def destroy(self):
        """Stop all audio and release resources."""
        self.stop_music()   # stop background music
        # SFX are auto‑destroyed — nothing else to clean up
