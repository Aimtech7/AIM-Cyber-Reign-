"""
ui.py — Heads‑Up Display (HUD) Module (Phase 2)
==================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Renders an in‑game overlay with status information.
          Phase 2 expands the HUD with:
            • "SYSTEM ONLINE" status
            • Player energy bar
            • Access level indicator
            • Current zone name
            • Sprint indicator

How it connects:
    The SceneManager (scenes.py) creates a HUD when entering the game
    scene and (optionally) passes it a player reference so the HUD
    can show sprint state.  destroy() is called on scene exit.

Key concepts:
    • All text is parented to camera.ui (2D screen overlay).
    • update() is used to refresh dynamic values like the sprint label.
    • Energy, access level, and zone are currently static defaults —
      they will become dynamic in future phases.
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import Entity, Text, color, destroy as ursina_destroy, camera

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN,
    NEON_GREEN,
    NEON_YELLOW,
    HUD_SECONDARY,
    PROJECT_NAME,
    PROJECT_VERSION,
    HUD_DEFAULT_ENERGY,
    HUD_DEFAULT_ACCESS,
    HUD_DEFAULT_ZONE,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  HUD class
# ══════════════════════════════════════════════════════════════════════════ #
class HUD(Entity):
    """
    In‑game heads‑up display showing system status, energy, access
    level, zone, and sprint state.

    Inherits from Entity so ``update()`` is called each frame for
    live state display (e.g. sprint indicator).

    Args:
        player_ref : PlayerController or None
            If provided, the HUD can read player.is_sprinting.

    Usage:
        hud = HUD(player_ref=my_player)
        hud.destroy()
    """

    def __init__(self, player_ref=None):
        """Create all HUD elements."""
        super().__init__()

        # Store player reference for sprint indicator
        self.player_ref = player_ref

        # Master list for cleanup
        self.elements = []

        # ── Layout constants ─────────────────────────────────────────── #
        left_x   = -0.85     # left column x position
        right_x  =  0.55     # right column x position

        # ============================================================== #
        #  LEFT COLUMN — System Status
        # ============================================================== #

        # ── "SYSTEM ONLINE" ──────────────────────────────────────────── #
        self._add_text('[ SYSTEM ONLINE ]', left_x, 0.45, 1.2, NEON_CYAN)

        # Decorative separator
        self._add_text('─' * 22, left_x, 0.42, 0.9, (0, 200, 200))

        # Version string
        self._add_text(
            f'{PROJECT_NAME}  v{PROJECT_VERSION}',
            left_x, 0.39, 0.8, HUD_SECONDARY,
        )

        # ── Energy ───────────────────────────────────────────────────── #
        self._add_text('ENERGY', left_x, 0.33, 0.9, HUD_SECONDARY)

        # Energy bar background (dark)
        bar_bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.18, 0.015),
            position=(left_x + 0.09, 0.305),
            color=color.rgb(20, 20, 30),
        )
        self.elements.append(bar_bg)

        # Energy bar fill (bright green)
        fill_width = 0.18 * (HUD_DEFAULT_ENERGY / 100)   # scale to percentage
        self.energy_bar = Entity(
            parent=camera.ui,
            model='quad',
            scale=(fill_width, 0.013),
            position=(left_x + 0.09 - (0.18 - fill_width) / 2, 0.305),
            origin=(-0.5, 0),                              # anchor left
            color=color.rgb(*NEON_GREEN),
        )
        self.elements.append(bar_bg)
        self.elements.append(self.energy_bar)

        # Energy numeric label
        self._add_text(
            f'{HUD_DEFAULT_ENERGY}%',
            left_x + 0.20, 0.33, 0.8, NEON_GREEN,
        )

        # ── Access Level ─────────────────────────────────────────────── #
        self._add_text('ACCESS', left_x, 0.27, 0.9, HUD_SECONDARY)
        self._add_text(HUD_DEFAULT_ACCESS, left_x + 0.09, 0.27, 0.9, NEON_CYAN)

        # ============================================================== #
        #  RIGHT COLUMN — Zone & Sprint
        # ============================================================== #

        # ── Zone name ────────────────────────────────────────────────── #
        self._add_text('ZONE', right_x, 0.45, 0.9, HUD_SECONDARY)
        self._add_text(HUD_DEFAULT_ZONE, right_x, 0.42, 1.0, NEON_CYAN)

        # Separator
        self._add_text('─' * 16, right_x, 0.39, 0.9, (0, 200, 200))

        # ── Sprint indicator (dynamic) ───────────────────────────────── #
        self.sprint_text = Text(
            text='',                             # empty by default
            position=(right_x, 0.35),
            scale=0.9,
            color=color.rgb(*NEON_YELLOW),
            font='VeraMono.ttf',
        )
        self.elements.append(self.sprint_text)

    # ------------------------------------------------------------------ #
    #  Text helper
    # ------------------------------------------------------------------ #
    def _add_text(self, text, x, y, scale, clr):
        """Shorthand to create a styled HUD text element."""
        # Convert tuple colour to Ursina color if needed
        if isinstance(clr, tuple):
            c = color.rgb(*clr)
        else:
            c = clr

        t = Text(
            text=text,
            position=(x, y),
            scale=scale,
            color=c,
            font='VeraMono.ttf',
        )
        self.elements.append(t)
        return t

    # ------------------------------------------------------------------ #
    #  Per‑frame update
    # ------------------------------------------------------------------ #
    def update(self):
        """Update dynamic HUD elements (sprint indicator)."""
        if self.player_ref and hasattr(self.player_ref, 'is_sprinting'):
            if self.player_ref.is_sprinting:
                self.sprint_text.text = '>> SPRINT <<'   # show label
            else:
                self.sprint_text.text = ''                # hide label

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove every HUD element from the screen."""
        try:
            ursina_destroy(self.sprint_text)
        except Exception:
            pass
        for element in self.elements:
            try:
                ursina_destroy(element)
            except Exception:
                pass
        self.elements.clear()
        self.player_ref = None
        super().destroy()
