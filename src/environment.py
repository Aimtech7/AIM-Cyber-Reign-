"""
environment.py — Game Environment Module (Phase 3)
====================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Builds the expanded 3D cyberpunk world.  Phase 3 gives
          terminals hackable states (locked / active / breached) with
          colour changes driven by the game state.

How it connects:
    The SceneManager (scenes.py) instantiates a GameEnvironment when
    the player enters the game scene.  The environment receives:
        • interaction_system — to register terminals as interactables
        • hack_callback      — function called when a terminal is activated

Key concepts:
    • Terminal base/screen/accent entities are stored per terminal
      so their colours can be updated after a breach.
    • TERMINAL_SPECS now include a security_level field.
    • Colours cycle:  LOCKED (green) → ACTIVE (yellow) → BREACHED (cyan).
"""

# ── Standard library ───────────────────────────────────────────────────── #
import random   # random colour assignment for buildings and pillars

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    AmbientLight,
    DirectionalLight,
    color,
    destroy as ursina_destroy,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN, NEON_PURPLE, NEON_MAGENTA, NEON_BLUE, NEON_VIOLET,
    NEON_GREEN,
    FLOOR_SCALE, FLOOR_COLOR, FLOOR_GRID_DENSITY,
    GRID_LINE_SPACING, GRID_LINE_ALPHA,
    BUILDING_SPECS,
    PILLAR_SPECS,
    WALL_SPECS,
    PLATFORM_SPECS,
    TERMINAL_SPECS,
    AMBIENT_COLOR, SUN_COLOR, SUN_ROTATION,
    TERMINAL_COLOR_LOCKED,
    TERMINAL_COLOR_ACTIVE,
    TERMINAL_COLOR_BREACHED,
)
from src.interaction import Interactable


# ══════════════════════════════════════════════════════════════════════════ #
#  GameEnvironment class
# ══════════════════════════════════════════════════════════════════════════ #
class GameEnvironment:
    """
    Manages every entity that makes up the 3D game world.

    Args:
        interaction_system : InteractionSystem or None
        hack_callback      : callable(label, security_level) or None
            Called when the player presses E on a terminal.

    Usage:
        env = GameEnvironment(interaction_system=sys, hack_callback=fn)
        env.set_terminal_color("Access Node Alpha", "breached")
        env.destroy()
    """

    def __init__(self, interaction_system=None, hack_callback=None):
        """Construct the full environment."""
        # Master list of all entities — used for bulk cleanup
        self.entities = []

        # Store references
        self._interaction   = interaction_system
        self._hack_callback = hack_callback

        # Per‑terminal entity references for colour updates
        # Key = label, Value = dict with 'base', 'screen', 'accent' entities
        self.terminal_parts = {}

        # Build world layers in order
        self._build_floor()       # ground plane + grid
        self._build_buildings()   # neon cube structures
        self._build_pillars()     # decorative neon columns
        self._build_walls()       # boundary walls around the arena
        self._build_platforms()   # elevated walkable surfaces
        self._build_terminals()   # interactive cyber nodes
        self._build_lighting()    # ambient + directional

    # ================================================================== #
    #  FLOOR
    # ================================================================== #
    def _build_floor(self):
        """Create a large dark plane and overlay thin cyan grid lines."""
        floor = Entity(
            model='plane',
            scale=FLOOR_SCALE,
            color=color.rgb(*FLOOR_COLOR),
            texture='white_cube',
            texture_scale=(FLOOR_GRID_DENSITY, FLOOR_GRID_DENSITY),
            collider='box',
        )
        self.entities.append(floor)

        half_size = int(FLOOR_SCALE[0] / 2)
        for i in range(-half_size, half_size + 1, GRID_LINE_SPACING):
            line_x = Entity(
                model='cube',
                scale=(FLOOR_SCALE[0], 0.01, 0.02),
                position=(0, 0.01, i),
                color=color.rgba(*NEON_CYAN, GRID_LINE_ALPHA),
                unlit=True,
            )
            line_z = Entity(
                model='cube',
                scale=(0.02, 0.01, FLOOR_SCALE[2]),
                position=(i, 0.01, 0),
                color=color.rgba(*NEON_CYAN, GRID_LINE_ALPHA),
                unlit=True,
            )
            self.entities.extend([line_x, line_z])

    # ================================================================== #
    #  BUILDINGS
    # ================================================================== #
    def _build_buildings(self):
        """Scatter neon‑coloured cube structures around the world."""
        neon_palette = [
            color.rgb(*NEON_CYAN),
            color.rgb(*NEON_PURPLE),
            color.rgb(*NEON_MAGENTA),
            color.rgb(*NEON_BLUE),
            color.rgb(*NEON_VIOLET),
        ]

        for x, z, w, h, d in BUILDING_SPECS:
            clr = random.choice(neon_palette)

            body = Entity(
                model='cube',
                position=(x, h / 2, z),
                scale=(w, h, d),
                color=color.rgb(int(clr.r * 40), int(clr.g * 40), int(clr.b * 40)),
            )
            self.entities.append(body)

            top_glow = Entity(
                model='cube',
                position=(x, h + 0.05, z),
                scale=(w + 0.1, 0.1, d + 0.1),
                color=clr,
                unlit=True,
            )
            self.entities.append(top_glow)

            for dx, dz in [(-w/2, 0), (w/2, 0), (0, -d/2), (0, d/2)]:
                edge = Entity(
                    model='cube',
                    position=(x + dx, h / 2, z + dz),
                    scale=(0.08, h, 0.08),
                    color=clr,
                    unlit=True,
                )
                self.entities.append(edge)

    # ================================================================== #
    #  PILLARS
    # ================================================================== #
    def _build_pillars(self):
        """Create decorative neon pillars."""
        neon_palette = [
            color.rgb(*NEON_CYAN),
            color.rgb(*NEON_PURPLE),
            color.rgb(*NEON_BLUE),
        ]

        for x, z, radius, height in PILLAR_SPECS:
            clr = random.choice(neon_palette)

            pillar = Entity(
                model='cube',
                position=(x, height / 2, z),
                scale=(radius * 2, height, radius * 2),
                color=color.rgb(int(clr.r * 30), int(clr.g * 30), int(clr.b * 30)),
            )
            self.entities.append(pillar)

            ring = Entity(
                model='cube',
                position=(x, height + 0.05, z),
                scale=(radius * 2 + 0.15, 0.12, radius * 2 + 0.15),
                color=clr,
                unlit=True,
            )
            self.entities.append(ring)

            base_ring = Entity(
                model='cube',
                position=(x, 0.05, z),
                scale=(radius * 2 + 0.2, 0.06, radius * 2 + 0.2),
                color=clr,
                unlit=True,
            )
            self.entities.append(base_ring)

    # ================================================================== #
    #  WALLS
    # ================================================================== #
    def _build_walls(self):
        """Create boundary walls around the arena perimeter."""
        for x, z, w, h, d in WALL_SPECS:
            wall = Entity(
                model='cube',
                position=(x, h / 2, z),
                scale=(w, h, d),
                color=color.rgb(8, 8, 20),
                collider='box',
            )
            self.entities.append(wall)

            wall_glow = Entity(
                model='cube',
                position=(x, h + 0.03, z),
                scale=(w + 0.05, 0.06, d + 0.05),
                color=color.rgb(*NEON_PURPLE),
                unlit=True,
            )
            self.entities.append(wall_glow)

    # ================================================================== #
    #  PLATFORMS
    # ================================================================== #
    def _build_platforms(self):
        """Create elevated walkable platforms."""
        for x, z, w, h, d in PLATFORM_SPECS:
            platform = Entity(
                model='cube',
                position=(x, h / 2, z),
                scale=(w, h, d),
                color=color.rgb(12, 12, 30),
                collider='box',
            )
            self.entities.append(platform)

            edge_glow = Entity(
                model='cube',
                position=(x, h + 0.02, z),
                scale=(w + 0.08, 0.04, d + 0.08),
                color=color.rgb(*NEON_CYAN),
                unlit=True,
            )
            self.entities.append(edge_glow)

    # ================================================================== #
    #  TERMINALS  (Phase 3 — now with states)
    # ================================================================== #
    def _build_terminals(self):
        """
        Create interactive cyber terminal objects with state support.
        Each terminal starts in 'locked' state.  Colour changes when
        the player interacts or breaches the terminal.
        """
        for x, z, label, security_level in TERMINAL_SPECS:
            # Default glow colour = locked (green)
            glow_clr = color.rgb(*TERMINAL_COLOR_LOCKED)

            # Terminal base — dark pedestal
            base = Entity(
                model='cube',
                position=(x, 0.5, z),
                scale=(0.6, 1, 0.6),
                color=color.rgb(15, 10, 30),
            )
            self.entities.append(base)

            # Glowing top screen
            screen = Entity(
                model='cube',
                position=(x, 1.1, z),
                scale=(0.5, 0.2, 0.5),
                color=glow_clr,
                unlit=True,
            )
            self.entities.append(screen)

            # Glowing accent ring around the base
            accent = Entity(
                model='cube',
                position=(x, 0.05, z),
                scale=(0.8, 0.06, 0.8),
                color=glow_clr,
                unlit=True,
            )
            self.entities.append(accent)

            # Store per‑terminal entity references for later recolouring
            self.terminal_parts[label] = {
                'base':   base,
                'screen': screen,
                'accent': accent,
            }

            # Register with the interaction system (if available)
            if self._interaction is not None:
                # Build a callback that carries the terminal's label
                # and security level to the hacking system
                def make_callback(lbl, sec):
                    """Factory to capture label + security in a closure."""
                    def cb():
                        if self._hack_callback:
                            self._hack_callback(lbl, sec)
                    return cb

                interactable = Interactable(
                    entity=base,
                    prompt=f'Press E to hack {label}',
                    message=f'[ Initiating breach on {label} … ]',
                    callback=make_callback(label, security_level),
                )
                self._interaction.add_interactable(interactable)

    # ================================================================== #
    #  TERMINAL COLOUR UPDATE  (Phase 3)
    # ================================================================== #
    def set_terminal_color(self, label, state):
        """
        Update a terminal's glow colour based on its current state.

        Args:
            label : str — terminal label (must match a key in terminal_parts)
            state : str — one of 'locked', 'active', 'breached'
        """
        parts = self.terminal_parts.get(label)
        if parts is None:
            return   # unknown terminal — skip silently

        # Pick the colour for the requested state
        if state == 'active':
            clr = color.rgb(*TERMINAL_COLOR_ACTIVE)
        elif state == 'breached':
            clr = color.rgb(*TERMINAL_COLOR_BREACHED)
        else:
            clr = color.rgb(*TERMINAL_COLOR_LOCKED)

        # Apply to screen and accent ring
        parts['screen'].color = clr
        parts['accent'].color = clr

    # ================================================================== #
    #  LIGHTING
    # ================================================================== #
    def _build_lighting(self):
        """Add ambient and directional lights."""
        ambient = AmbientLight(color=color.rgb(*AMBIENT_COLOR))
        self.entities.append(ambient)

        sun = DirectionalLight(y=10, rotation=SUN_ROTATION)
        sun.color = color.rgb(*SUN_COLOR)
        self.entities.append(sun)

    # ================================================================== #
    #  CLEANUP
    # ================================================================== #
    def destroy(self):
        """Remove every entity created by this environment."""
        for entity in reversed(self.entities):
            try:
                ursina_destroy(entity)
            except Exception:
                pass
        self.entities.clear()
        self.terminal_parts.clear()
