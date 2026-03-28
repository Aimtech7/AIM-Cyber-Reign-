"""
ui.py — Heads‑Up Display (HUD) Module (Phase 3)
==================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : In‑game overlay showing status information.
          Phase 3 adds:
            • Breached node count (e.g. "2 / 4 NODES BREACHED")
            • Dynamic access level from game state
            • Current target terminal label (if near one)

How it connects:
    SceneManager creates a HUD with a player ref and a game_state ref.
    The HUD's update() reads both every frame to refresh displays.
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import Entity, Text, color, destroy as ursina_destroy, camera

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN,
    NEON_GREEN,
    NEON_YELLOW,
    NEON_MAGENTA,
    HUD_SECONDARY,
    PROJECT_NAME,
    PROJECT_VERSION,
    HUD_DEFAULT_ENERGY,
    HUD_DEFAULT_ZONE,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  HUD class
# ══════════════════════════════════════════════════════════════════════════ #
class HUD(Entity):
    """
    In‑game heads‑up display with:
      • System status   • Energy bar   • Access level (dynamic)
      • Zone name       • Sprint indicator
      • Breached nodes  • Current target

    Args:
        player_ref : PlayerController or None
        game_state : GameState or None
    """

    def __init__(self, player_ref=None, game_state=None):
        """Create all HUD elements."""
        super().__init__()

        # Store references
        self.player_ref = player_ref
        self.game_state = game_state

        # Master list for cleanup
        self.elements = []

        # ── Layout constants ─────────────────────────────────────────── #
        left_x  = -0.85
        right_x =  0.55

        # ============================================================== #
        #  LEFT COLUMN — System Status
        # ============================================================== #

        # ── "SYSTEM ONLINE" ──────────────────────────────────────────── #
        self._add_text('[ SYSTEM ONLINE ]', left_x, 0.45, 1.2, NEON_CYAN)
        self._add_text('─' * 22, left_x, 0.42, 0.9, (0, 200, 200))
        self._add_text(
            f'{PROJECT_NAME}  v{PROJECT_VERSION}',
            left_x, 0.39, 0.8, HUD_SECONDARY,
        )

        # ── Energy ───────────────────────────────────────────────────── #
        self._add_text('ENERGY', left_x, 0.33, 0.9, HUD_SECONDARY)

        bar_bg = Entity(
            parent=camera.ui, model='quad',
            scale=(0.18, 0.015), position=(left_x + 0.09, 0.305),
            color=color.rgb(20, 20, 30),
        )
        self.elements.append(bar_bg)

        fill_width = 0.18 * (HUD_DEFAULT_ENERGY / 100)
        self.energy_bar = Entity(
            parent=camera.ui, model='quad',
            scale=(fill_width, 0.013),
            position=(left_x + 0.09 - (0.18 - fill_width) / 2, 0.305),
            origin=(-0.5, 0),
            color=color.rgb(*NEON_GREEN),
        )
        self.elements.append(bar_bg)
        self.elements.append(self.energy_bar)

        self._add_text(
            f'{HUD_DEFAULT_ENERGY}%', left_x + 0.20, 0.33, 0.8, NEON_GREEN,
        )

        # ── Access Level (dynamic from game state) ───────────────────── #
        self._add_text('ACCESS', left_x, 0.27, 0.9, HUD_SECONDARY)
        self.access_text = self._add_text(
            'LEVEL 1', left_x + 0.09, 0.27, 0.9, NEON_CYAN,
        )

        # ── Breached Nodes (Phase 3) ─────────────────────────────────── #
        self._add_text('NODES', left_x, 0.21, 0.9, HUD_SECONDARY)
        self.nodes_text = self._add_text(
            '0 / 0 BREACHED', left_x + 0.09, 0.21, 0.9, NEON_GREEN,
        )

        # ============================================================== #
        #  RIGHT COLUMN — Zone & Sprint & Target
        # ============================================================== #

        # ── Zone name ────────────────────────────────────────────────── #
        self._add_text('ZONE', right_x, 0.45, 0.9, HUD_SECONDARY)
        self._add_text(HUD_DEFAULT_ZONE, right_x, 0.42, 1.0, NEON_CYAN)
        self._add_text('─' * 16, right_x, 0.39, 0.9, (0, 200, 200))

        # ── Sprint indicator (dynamic) ───────────────────────────────── #
        self.sprint_text = Text(
            text='',
            position=(right_x, 0.35),
            scale=0.9,
            color=color.rgb(*NEON_YELLOW),
            font='VeraMono.ttf',
        )
        self.elements.append(self.sprint_text)

        # ── Current target label (Phase 3) ───────────────────────────── #
        self.target_text = Text(
            text='',
            position=(right_x, 0.31),
            scale=0.8,
            color=color.rgb(*NEON_MAGENTA),
            font='VeraMono.ttf',
        )
        self.elements.append(self.target_text)

    # ------------------------------------------------------------------ #
    #  Text helper
    # ------------------------------------------------------------------ #
    def _add_text(self, text, x, y, scale, clr):
        """Create a styled HUD text element."""
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
        """Refresh dynamic HUD values each frame."""
        # ── Sprint ───────────────────────────────────────────────────── #
        if self.player_ref and hasattr(self.player_ref, 'is_sprinting'):
            if self.player_ref.is_sprinting:
                self.sprint_text.text = '>> SPRINT <<'
            else:
                self.sprint_text.text = ''

        # ── Game state: nodes + access level ─────────────────────────── #
        if self.game_state:
            stats = self.game_state.get_stats()

            # Update breached node count
            breached = stats['breached']
            total    = stats['total']
            self.nodes_text.text = f'{breached} / {total} BREACHED'

            # Colour: green when progress, magenta when all done
            if breached >= total and total > 0:
                self.nodes_text.color = color.rgb(*NEON_MAGENTA)
            else:
                self.nodes_text.color = color.rgb(*NEON_GREEN)

            # Update access level
            self.access_text.text = f'LEVEL {stats["access_level"]}'

    # ------------------------------------------------------------------ #
    #  Set the current target label (called externally)
    # ------------------------------------------------------------------ #
    def set_target(self, label):
        """Show / clear the current terminal target name."""
        if label:
            self.target_text.text = f'TARGET: {label}'
        else:
            self.target_text.text = ''

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove every HUD element."""
        try:
            ursina_destroy(self.sprint_text)
        except Exception:
            pass
        try:
            ursina_destroy(self.target_text)
        except Exception:
            pass
        for element in self.elements:
            try:
                ursina_destroy(element)
            except Exception:
                pass
        self.elements.clear()
        self.player_ref = None
        self.game_state = None
        super().destroy()
