"""
hacking.py — Hacking Interface & Mini‑Game Module
====================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides the full‑screen hacking panel that appears when
          the player interacts with a cyber terminal.  The mini‑game
          is a timed key‑sequence challenge: the panel displays a row
          of keys; the player must press each one in order before the
          timer runs out.

Mini‑game rules:
    • The key sequence length is based on the terminal's security
      level (security 1 → 4 keys, 2 → 5 keys, 3 → 6 keys).
    • Each correct key press highlights the next key in the sequence.
    • A wrong key press removes HACK_WRONG_PENALTY correct keys.
    • Running out of time = failure.
    • Pressing ESC aborts with no penalty.
    • On success or failure, a callback is fired.

How it connects:
    scenes.py opens a HackingPanel when the player interacts with a
    terminal.  On completion, scenes.py receives a callback with
    the result (True/False) and updates GameState + terminal visuals.

Key concepts:
    • HackingPanel inherits from Entity so update() and input()
      run automatically.
    • The player's FPS controller is disabled while hacking (frozen).
    • All UI elements are parented to camera.ui (2D overlay).
"""

# ── Standard library ───────────────────────────────────────────────────── #
import random   # used to generate random key sequences

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Text,
    camera,
    color,
    time as ursina_time,
    destroy as ursina_destroy,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    HACK_KEY_POOL,
    HACK_BASE_LENGTH,
    HACK_TIME_LIMIT,
    HACK_WRONG_PENALTY,
    HACK_PANEL_BG,
    HACK_PANEL_BORDER,
    NEON_CYAN,
    NEON_GREEN,
    NEON_MAGENTA,
    NEON_YELLOW,
    NEON_PURPLE,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  HackingPanel class
# ══════════════════════════════════════════════════════════════════════════ #
class HackingPanel(Entity):
    """
    Full‑screen hacking interface with a key‑sequence mini‑game.

    Args:
        terminal_label  : str      — name of the terminal being hacked
        security_level  : int      — difficulty (1–3)
        on_complete     : callable — called with (bool) True=success False=fail

    Usage:
        panel = HackingPanel("Access Node Alpha", 1, my_callback)
        # … runs until the player succeeds, fails, or aborts …
        # my_callback(True) or my_callback(False) is called automatically
    """

    def __init__(self, terminal_label, security_level, on_complete):
        """Build the hacking panel UI and generate the key sequence."""
        # Initialise the Entity
        super().__init__()

        # Store parameters
        self.terminal_label = terminal_label          # e.g. "Access Node Alpha"
        self.security_level = security_level          # 1, 2, or 3
        self.on_complete    = on_complete             # callback(bool)

        # ── Generate the key sequence ────────────────────────────────── #
        # Length = base + (security_level - 1)  →  4, 5, or 6
        seq_length = HACK_BASE_LENGTH + (security_level - 1)
        self.sequence = [random.choice(HACK_KEY_POOL) for _ in range(seq_length)]

        # How many keys the player has correctly pressed so far
        self.progress = 0

        # Timer tracking (counts down from HACK_TIME_LIMIT)
        self.time_remaining = HACK_TIME_LIMIT

        # Whether the panel is still active (False after success/fail/abort)
        self.active = True

        # Master list of UI elements for cleanup
        self.elements = []

        # ── Build the visual panel ───────────────────────────────────── #
        self._build_ui()

    # ================================================================== #
    #  UI CONSTRUCTION
    # ================================================================== #
    def _build_ui(self):
        """Create all on‑screen elements for the hacking interface."""

        # ── Dark semi‑transparent backdrop ───────────────────────────── #
        bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 1),
            color=color.rgba(*HACK_PANEL_BG, 230),
            z=0.5,
        )
        self.elements.append(bg)

        # ── Panel border (decorative neon rectangle) ─────────────────── #
        border_top = Entity(
            parent=camera.ui, model='quad',
            scale=(0.7, 0.003), position=(0, 0.32),
            color=color.rgb(*HACK_PANEL_BORDER), z=0,
        )
        border_bot = Entity(
            parent=camera.ui, model='quad',
            scale=(0.7, 0.003), position=(0, -0.32),
            color=color.rgb(*HACK_PANEL_BORDER), z=0,
        )
        border_left = Entity(
            parent=camera.ui, model='quad',
            scale=(0.003, 0.64), position=(-0.35, 0),
            color=color.rgb(*HACK_PANEL_BORDER), z=0,
        )
        border_right = Entity(
            parent=camera.ui, model='quad',
            scale=(0.003, 0.64), position=(0.35, 0),
            color=color.rgb(*HACK_PANEL_BORDER), z=0,
        )
        self.elements.extend([border_top, border_bot, border_left, border_right])

        # ── "HACKING" header ─────────────────────────────────────────── #
        header = Text(
            text='[ HACKING IN PROGRESS ]',
            parent=camera.ui, position=(0, 0.28), origin=(0, 0),
            scale=2.0, color=color.rgb(*NEON_MAGENTA), font='VeraMono.ttf',
        )
        self.elements.append(header)

        # ── Terminal name ────────────────────────────────────────────── #
        name_text = Text(
            text=f'TARGET: {self.terminal_label}',
            parent=camera.ui, position=(0, 0.21), origin=(0, 0),
            scale=1.2, color=color.rgb(*NEON_CYAN), font='VeraMono.ttf',
        )
        self.elements.append(name_text)

        # ── Security level ───────────────────────────────────────────── #
        sec_text = Text(
            text=f'SECURITY LEVEL: {self.security_level}',
            parent=camera.ui, position=(0, 0.16), origin=(0, 0),
            scale=1.0, color=color.rgb(*NEON_YELLOW), font='VeraMono.ttf',
        )
        self.elements.append(sec_text)

        # ── Key sequence display ─────────────────────────────────────── #
        # Each key gets its own Text entity so we can colour them
        self.key_texts = []           # list of Text entities
        total_keys = len(self.sequence)
        spacing = 0.08                # gap between key boxes

        # Calculate start x so keys are centred
        start_x = -((total_keys - 1) * spacing) / 2

        for i, key_char in enumerate(self.sequence):
            x_pos = start_x + i * spacing

            # Key background box (dark)
            box = Entity(
                parent=camera.ui, model='quad',
                scale=(0.055, 0.055), position=(x_pos, 0.06),
                color=color.rgb(20, 15, 40), z=0.1,
            )
            self.elements.append(box)

            # Key label
            kt = Text(
                text=key_char.upper(),
                parent=camera.ui, position=(x_pos, 0.06), origin=(0, 0),
                scale=1.6, color=color.rgb(100, 100, 140), font='VeraMono.ttf',
            )
            self.key_texts.append(kt)
            self.elements.append(kt)

        # ── Timer bar background ─────────────────────────────────────── #
        timer_bg = Entity(
            parent=camera.ui, model='quad',
            scale=(0.5, 0.018), position=(0, -0.06),
            color=color.rgb(20, 15, 40),
        )
        self.elements.append(timer_bg)

        # Timer bar fill (shrinks as time runs out)
        self.timer_bar = Entity(
            parent=camera.ui, model='quad',
            scale=(0.5, 0.016), position=(0, -0.06),
            color=color.rgb(*NEON_CYAN), origin=(-0.5, 0),
        )
        self.elements.append(self.timer_bar)

        # Timer text
        self.timer_text = Text(
            text=f'TIME: {self.time_remaining:.1f}s',
            parent=camera.ui, position=(0, -0.10), origin=(0, 0),
            scale=1.0, color=color.rgb(*NEON_CYAN), font='VeraMono.ttf',
        )
        self.elements.append(self.timer_text)

        # ── Status text (changes on success / fail / wrong key) ──────── #
        self.status_text = Text(
            text='>> Enter the key sequence <<',
            parent=camera.ui, position=(0, -0.18), origin=(0, 0),
            scale=1.2, color=color.rgb(180, 180, 200), font='VeraMono.ttf',
        )
        self.elements.append(self.status_text)

        # ── Hint ─────────────────────────────────────────────────────── #
        hint = Text(
            text='[ESC] Abort',
            parent=camera.ui, position=(0, -0.26), origin=(0, 0),
            scale=0.8, color=color.rgb(80, 80, 100), font='VeraMono.ttf',
        )
        self.elements.append(hint)

    # ================================================================== #
    #  UPDATE — timer countdown
    # ================================================================== #
    def update(self):
        """
        Each frame: count down the timer and update the bar.
        If time reaches zero, the hack fails.
        """
        if not self.active:
            return  # already finished — skip

        # Subtract elapsed time
        self.time_remaining -= ursina_time.dt

        # Clamp to zero
        if self.time_remaining < 0:
            self.time_remaining = 0

        # Update timer bar width (proportional to remaining time)
        fraction = self.time_remaining / HACK_TIME_LIMIT
        self.timer_bar.scale_x = 0.5 * fraction  # shrinks toward zero

        # Change bar colour as time runs low
        if fraction < 0.25:
            self.timer_bar.color = color.rgb(*NEON_MAGENTA)  # critical — red/pink
        elif fraction < 0.5:
            self.timer_bar.color = color.rgb(*NEON_YELLOW)   # warning — yellow
        else:
            self.timer_bar.color = color.rgb(*NEON_CYAN)     # safe — cyan

        # Update timer label
        self.timer_text.text = f'TIME: {self.time_remaining:.1f}s'

        # ── Time expired → failure ───────────────────────────────────── #
        if self.time_remaining <= 0:
            self._finish(success=False, reason='TIME EXPIRED')

    # ================================================================== #
    #  INPUT — key matching
    # ================================================================== #
    def input(self, key):
        """
        Handle key presses during the hacking mini‑game.

        Correct key   → advance progress, highlight next key.
        Wrong key     → penalise, flash warning.
        ESC           → abort without penalty.
        """
        if not self.active:
            return  # ignore input after completion

        # ── ESC to abort ─────────────────────────────────────────────── #
        if key == 'escape':
            self._finish(success=False, reason='ABORTED')
            return

        # Only process single‑character key presses (letters)
        if len(key) != 1:
            return   # ignore held keys, modifiers, etc.

        # ── Correct key ──────────────────────────────────────────────── #
        expected = self.sequence[self.progress]
        if key == expected:
            # Highlight the correctly pressed key in bright green
            self.key_texts[self.progress].color = color.rgb(*NEON_GREEN)
            self.progress += 1

            # Update status
            self.status_text.text = f'>> {self.progress}/{len(self.sequence)} <<'
            self.status_text.color = color.rgb(*NEON_GREEN)

            # ── All keys entered → success! ──────────────────────────── #
            if self.progress >= len(self.sequence):
                self._finish(success=True, reason='BREACH COMPLETE')

        else:
            # ── Wrong key → penalise ─────────────────────────────────── #
            # Roll back progress by the penalty amount (minimum 0)
            old_progress = self.progress
            self.progress = max(0, self.progress - HACK_WRONG_PENALTY)

            # Un‑highlight any rolled‑back keys
            for i in range(self.progress, old_progress):
                self.key_texts[i].color = color.rgb(100, 100, 140)  # dim again

            # Flash warning
            self.status_text.text = f'WRONG KEY! {self.progress}/{len(self.sequence)}'
            self.status_text.color = color.rgb(*NEON_MAGENTA)

    # ================================================================== #
    #  FINISH — success or failure
    # ================================================================== #
    def _finish(self, success, reason):
        """
        End the hacking session and fire the completion callback.

        Args:
            success : bool — True if breach succeeded
            reason  : str  — message to display briefly
        """
        self.active = False   # stop further updates and input

        # Show final status
        if success:
            self.status_text.text = f'[[ {reason} ]]'
            self.status_text.color = color.rgb(*NEON_GREEN)
        else:
            self.status_text.text = f'[[ {reason} ]]'
            self.status_text.color = color.rgb(*NEON_MAGENTA)

        # Schedule cleanup + callback after a short delay
        # (invoke() is Ursina's timer — calls the function after N seconds)
        from ursina import invoke  # import locally to avoid circular issues
        invoke(self._cleanup_and_callback, success, delay=1.5)

    # ================================================================== #
    #  CLEANUP
    # ================================================================== #
    def _cleanup_and_callback(self, success):
        """Remove all UI elements and notify the caller."""
        # Fire the callback first (so caller can update state)
        if self.on_complete:
            self.on_complete(success)

        # Destroy all UI elements
        self.destroy()

    def destroy(self):
        """Remove every hacking panel element from the screen."""
        for element in self.elements:
            try:
                ursina_destroy(element)
            except Exception:
                pass
        self.elements.clear()
        self.key_texts.clear()
        self.on_complete = None
        try:
            super().destroy()   # remove the Entity itself
        except Exception:
            pass
