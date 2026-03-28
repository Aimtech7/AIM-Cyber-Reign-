"""
environment.py — Game Environment Module (Phase 2)
====================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Builds the expanded 3D cyberpunk world.  Phase 2 adds:
          • neon pillars
          • boundary walls
          • elevated platforms
          • interactive cyber terminals
          alongside the existing floor grid and cube buildings.

How it connects:
    The SceneManager (scenes.py) instantiates a GameEnvironment when
    the player enters the game scene.  The environment also receives
    an InteractionSystem reference so it can register terminals.

Key concepts:
    • All new object specs live in config.py (PILLAR_SPECS, etc.).
    • Terminals are 3D objects that are also registered as
      Interactable objects with the InteractionSystem.
    • Colours are randomly assigned from the neon palette.
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
            If provided, terminals are registered for player interaction.

    Usage:
        env = GameEnvironment(interaction_system=my_system)
        env.destroy()
    """

    def __init__(self, interaction_system=None):
        """Construct the full environment."""
        # Master list of all entities — used for bulk cleanup
        self.entities = []

        # Store the interaction system reference
        self._interaction = interaction_system

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
        """
        Create a large dark plane and overlay thin cyan grid lines.
        The floor is also the ground collider for the player.
        """
        # Main ground plane
        floor = Entity(
            model='plane',
            scale=FLOOR_SCALE,
            color=color.rgb(*FLOOR_COLOR),
            texture='white_cube',
            texture_scale=(FLOOR_GRID_DENSITY, FLOOR_GRID_DENSITY),
            collider='box',
        )
        self.entities.append(floor)

        # Grid overlay lines (X and Z axes)
        half_size = int(FLOOR_SCALE[0] / 2)
        for i in range(-half_size, half_size + 1, GRID_LINE_SPACING):
            # Line running along X axis
            line_x = Entity(
                model='cube',
                scale=(FLOOR_SCALE[0], 0.01, 0.02),
                position=(0, 0.01, i),
                color=color.rgba(*NEON_CYAN, GRID_LINE_ALPHA),
                unlit=True,
            )
            # Line running along Z axis
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
        """
        Scatter neon‑coloured cube structures around the world.
        Each building has a dark body, a glowing top edge, and
        glowing vertical corner edges.
        """
        neon_palette = [
            color.rgb(*NEON_CYAN),
            color.rgb(*NEON_PURPLE),
            color.rgb(*NEON_MAGENTA),
            color.rgb(*NEON_BLUE),
            color.rgb(*NEON_VIOLET),
        ]

        for x, z, w, h, d in BUILDING_SPECS:
            clr = random.choice(neon_palette)

            # Dark building body
            body = Entity(
                model='cube',
                position=(x, h / 2, z),
                scale=(w, h, d),
                color=color.rgb(int(clr.r * 40), int(clr.g * 40), int(clr.b * 40)),
            )
            self.entities.append(body)

            # Glowing top edge strip
            top_glow = Entity(
                model='cube',
                position=(x, h + 0.05, z),
                scale=(w + 0.1, 0.1, d + 0.1),
                color=clr,
                unlit=True,
            )
            self.entities.append(top_glow)

            # Glowing vertical corner edges
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
    #  PILLARS  (Phase 2)
    # ================================================================== #
    def _build_pillars(self):
        """
        Create decorative neon pillars around the central area.
        Each pillar is a thin tall cube with a glowing ring at the top.
        """
        neon_palette = [
            color.rgb(*NEON_CYAN),
            color.rgb(*NEON_PURPLE),
            color.rgb(*NEON_BLUE),
        ]

        for x, z, radius, height in PILLAR_SPECS:
            clr = random.choice(neon_palette)

            # Pillar body — dark tinted column
            pillar = Entity(
                model='cube',
                position=(x, height / 2, z),
                scale=(radius * 2, height, radius * 2),
                color=color.rgb(int(clr.r * 30), int(clr.g * 30), int(clr.b * 30)),
            )
            self.entities.append(pillar)

            # Glowing ring at the top of the pillar
            ring = Entity(
                model='cube',
                position=(x, height + 0.05, z),
                scale=(radius * 2 + 0.15, 0.12, radius * 2 + 0.15),
                color=clr,
                unlit=True,
            )
            self.entities.append(ring)

            # Glowing base ring at the bottom
            base_ring = Entity(
                model='cube',
                position=(x, 0.05, z),
                scale=(radius * 2 + 0.2, 0.06, radius * 2 + 0.2),
                color=clr,
                unlit=True,
            )
            self.entities.append(base_ring)

    # ================================================================== #
    #  WALLS  (Phase 2)
    # ================================================================== #
    def _build_walls(self):
        """
        Create boundary walls around the arena perimeter.
        Walls have a dark body with a neon top edge.
        """
        for x, z, w, h, d in WALL_SPECS:
            # Dark wall body
            wall = Entity(
                model='cube',
                position=(x, h / 2, z),
                scale=(w, h, d),
                color=color.rgb(8, 8, 20),       # very dark
                collider='box',                    # solid barrier
            )
            self.entities.append(wall)

            # Neon top edge
            wall_glow = Entity(
                model='cube',
                position=(x, h + 0.03, z),
                scale=(w + 0.05, 0.06, d + 0.05),
                color=color.rgb(*NEON_PURPLE),
                unlit=True,
            )
            self.entities.append(wall_glow)

    # ================================================================== #
    #  PLATFORMS  (Phase 2)
    # ================================================================== #
    def _build_platforms(self):
        """
        Create elevated walkable platforms.
        Each platform has a flat top surface with neon edge glow.
        """
        for x, z, w, h, d in PLATFORM_SPECS:
            # Platform surface — walkable with collider
            platform = Entity(
                model='cube',
                position=(x, h / 2, z),
                scale=(w, h, d),
                color=color.rgb(12, 12, 30),
                collider='box',                    # player can stand on it
            )
            self.entities.append(platform)

            # Neon edge glow around the platform top
            edge_glow = Entity(
                model='cube',
                position=(x, h + 0.02, z),
                scale=(w + 0.08, 0.04, d + 0.08),
                color=color.rgb(*NEON_CYAN),
                unlit=True,
            )
            self.entities.append(edge_glow)

    # ================================================================== #
    #  TERMINALS  (Phase 2)
    # ================================================================== #
    def _build_terminals(self):
        """
        Create interactive cyber terminal objects.
        Each terminal is a small glowing pedestal.  If an interaction
        system is available, terminals are registered as Interactable
        objects so the player can activate them with 'E'.
        """
        for x, z, label in TERMINAL_SPECS:
            # Terminal base — dark pedestal
            base = Entity(
                model='cube',
                position=(x, 0.5, z),
                scale=(0.6, 1, 0.6),
                color=color.rgb(15, 10, 30),
            )
            self.entities.append(base)

            # Glowing top screen — bright green
            screen = Entity(
                model='cube',
                position=(x, 1.1, z),
                scale=(0.5, 0.2, 0.5),
                color=color.rgb(*NEON_GREEN),
                unlit=True,
            )
            self.entities.append(screen)

            # Glowing accent ring around the base
            accent = Entity(
                model='cube',
                position=(x, 0.05, z),
                scale=(0.8, 0.06, 0.8),
                color=color.rgb(*NEON_GREEN),
                unlit=True,
            )
            self.entities.append(accent)

            # Register with the interaction system (if available)
            if self._interaction is not None:
                interactable = Interactable(
                    entity=base,                            # the pedestal
                    prompt=f'Press E to access {label}',    # on‑screen hint
                    message=f'[ {label} — CONNECTED ]',    # feedback text
                )
                self._interaction.add_interactable(interactable)

    # ================================================================== #
    #  LIGHTING
    # ================================================================== #
    def _build_lighting(self):
        """Add ambient and directional lights for a moody night feel."""
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
