"""
environment.py — Game Environment Module (Phase 8)
====================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Builds the 3D cyberpunk world including:
            • Floor grid, buildings, pillars, walls, platforms
            • Hackable terminals with state colours
            • Extraction zone (Phase 5)
            • Mission‑target terminal highlighting (Phase 5)
            • GlowPulse effects on terminals & extraction zone (Phase 8)
            • Neon accent strips on buildings (Phase 8)
"""

# ── Standard library ───────────────────────────────────────────────────── #
import random   # random colour assignment for buildings and pillars
import math     # for extraction zone pulse effect

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    AmbientLight,
    DirectionalLight,
    color,
    destroy as ursina_destroy,
    time as ursina_time,
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
    EXTRACTION_ZONE_POS,
    EXTRACTION_ZONE_RADIUS,
    EXTRACTION_ZONE_COLOR,
    MISSION_TARGET_COLOR,
    MISSION_REQUIRED_TERMINALS,
    ITEM_PICKUP_SPECS,           # Phase 6 — item spawn points
)
from src.interaction import Interactable
from src.inventory import ItemPickup   # Phase 6 — pickup entities
from src.effects import GlowPulse      # Phase 8 — pulsing glow rings


# ══════════════════════════════════════════════════════════════════════════ #
#  GameEnvironment class
# ══════════════════════════════════════════════════════════════════════════ #
class GameEnvironment:
    """
    Manages every entity that makes up the 3D game world.

    Args:
        interaction_system : InteractionSystem or None
        hack_callback      : callable(label, security_level) or None
        extraction_callback: callable() or None — called when player is
                             near the extraction zone and presses E
    """

    def __init__(self, interaction_system=None, hack_callback=None,
                 extraction_callback=None):
        """Construct the full environment."""
        self.entities = []
        self._interaction       = interaction_system
        self._hack_callback     = hack_callback
        self._extraction_cb     = extraction_callback
        self.terminal_parts     = {}
        self.extraction_ring    = None   # pulsing ring Entity
        self.item_pickups       = []     # Phase 6 — ItemPickup entities
        self._glow_effects      = []     # Phase 8 — GlowPulse entities

        self._build_floor()
        self._build_buildings()
        self._build_pillars()
        self._build_walls()
        self._build_platforms()
        self._build_terminals()
        self._build_extraction_zone()   # Phase 5
        self._build_item_pickups()      # Phase 6
        self._build_lighting()

    # ================================================================== #
    #  FLOOR
    # ================================================================== #
    def _build_floor(self):
        floor = Entity(
            model='plane', scale=FLOOR_SCALE,
            color=color.rgb(*FLOOR_COLOR),
            texture='white_cube',
            texture_scale=(FLOOR_GRID_DENSITY, FLOOR_GRID_DENSITY),
            collider='box',
        )
        self.entities.append(floor)
        half = int(FLOOR_SCALE[0] / 2)
        for i in range(-half, half + 1, GRID_LINE_SPACING):
            lx = Entity(model='cube', scale=(FLOOR_SCALE[0], 0.01, 0.02),
                        position=(0, 0.01, i),
                        color=color.rgba(*NEON_CYAN, GRID_LINE_ALPHA), unlit=True)
            lz = Entity(model='cube', scale=(0.02, 0.01, FLOOR_SCALE[2]),
                        position=(i, 0.01, 0),
                        color=color.rgba(*NEON_CYAN, GRID_LINE_ALPHA), unlit=True)
            self.entities.extend([lx, lz])

    # ================================================================== #
    #  BUILDINGS
    # ================================================================== #
    def _build_buildings(self):
        palette = [color.rgb(*c) for c in
                   [NEON_CYAN, NEON_PURPLE, NEON_MAGENTA, NEON_BLUE, NEON_VIOLET]]
        for x, z, w, h, d in BUILDING_SPECS:
            clr = random.choice(palette)
            body = Entity(model='cube', position=(x, h/2, z), scale=(w, h, d),
                          color=color.rgb(int(clr.r*40), int(clr.g*40), int(clr.b*40)))
            self.entities.append(body)
            top = Entity(model='cube', position=(x, h+0.05, z),
                         scale=(w+0.1, 0.1, d+0.1), color=clr, unlit=True)
            self.entities.append(top)
            for dx, dz in [(-w/2, 0), (w/2, 0), (0, -d/2), (0, d/2)]:
                e = Entity(model='cube', position=(x+dx, h/2, z+dz),
                           scale=(0.08, h, 0.08), color=clr, unlit=True)
                self.entities.append(e)

            # Phase 8 — neon accent strip across the building face
            accent_strip = Entity(
                model='cube',
                position=(x, h * 0.6, z),
                scale=(w + 0.05, 0.05, d + 0.05),
                color=clr, unlit=True,
            )
            self.entities.append(accent_strip)

    # ================================================================== #
    #  PILLARS
    # ================================================================== #
    def _build_pillars(self):
        palette = [color.rgb(*c) for c in [NEON_CYAN, NEON_PURPLE, NEON_BLUE]]
        for x, z, r, h in PILLAR_SPECS:
            clr = random.choice(palette)
            p = Entity(model='cube', position=(x, h/2, z), scale=(r*2, h, r*2),
                       color=color.rgb(int(clr.r*30), int(clr.g*30), int(clr.b*30)))
            self.entities.append(p)
            t = Entity(model='cube', position=(x, h+0.05, z),
                       scale=(r*2+0.15, 0.12, r*2+0.15), color=clr, unlit=True)
            self.entities.append(t)
            b = Entity(model='cube', position=(x, 0.05, z),
                       scale=(r*2+0.2, 0.06, r*2+0.2), color=clr, unlit=True)
            self.entities.append(b)

    # ================================================================== #
    #  WALLS
    # ================================================================== #
    def _build_walls(self):
        for x, z, w, h, d in WALL_SPECS:
            wall = Entity(model='cube', position=(x, h/2, z), scale=(w, h, d),
                          color=color.rgb(8, 8, 20), collider='box')
            self.entities.append(wall)
            g = Entity(model='cube', position=(x, h+0.03, z),
                       scale=(w+0.05, 0.06, d+0.05),
                       color=color.rgb(*NEON_PURPLE), unlit=True)
            self.entities.append(g)

    # ================================================================== #
    #  PLATFORMS
    # ================================================================== #
    def _build_platforms(self):
        for x, z, w, h, d in PLATFORM_SPECS:
            p = Entity(model='cube', position=(x, h/2, z), scale=(w, h, d),
                       color=color.rgb(12, 12, 30), collider='box')
            self.entities.append(p)
            e = Entity(model='cube', position=(x, h+0.02, z),
                       scale=(w+0.08, 0.04, d+0.08),
                       color=color.rgb(*NEON_CYAN), unlit=True)
            self.entities.append(e)

    # ================================================================== #
    #  TERMINALS  (with mission‑target highlighting)
    # ================================================================== #
    def _build_terminals(self):
        """Create hackable terminals. Mission‑required ones glow orange."""
        for x, z, label, security_level in TERMINAL_SPECS:
            # Mission targets start orange; others start green
            is_target = label in MISSION_REQUIRED_TERMINALS
            glow_clr = (color.rgb(*MISSION_TARGET_COLOR)
                        if is_target
                        else color.rgb(*TERMINAL_COLOR_LOCKED))

            base = Entity(model='cube', position=(x, 0.5, z),
                          scale=(0.6, 1, 0.6), color=color.rgb(15, 10, 30))
            self.entities.append(base)

            screen = Entity(model='cube', position=(x, 1.1, z),
                            scale=(0.5, 0.2, 0.5), color=glow_clr, unlit=True)
            self.entities.append(screen)

            accent = Entity(model='cube', position=(x, 0.05, z),
                            scale=(0.8, 0.06, 0.8), color=glow_clr, unlit=True)
            self.entities.append(accent)

            self.terminal_parts[label] = {
                'base': base, 'screen': screen, 'accent': accent,
            }

            # Phase 8 — add pulsing glow ring around the terminal base
            glow_clr_tuple = (MISSION_TARGET_COLOR if is_target
                              else TERMINAL_COLOR_LOCKED)
            glow = GlowPulse(
                parent_entity=base,
                base_scale=(1.5, 0.08, 1.5),
                glow_color=glow_clr_tuple,
            )
            self._glow_effects.append(glow)
            self.entities.append(glow)

            if self._interaction is not None:
                def make_cb(lbl, sec):
                    def cb():
                        if self._hack_callback:
                            self._hack_callback(lbl, sec)
                    return cb
                # Add [TARGET] prefix for mission terminals
                prefix = '[TARGET] ' if is_target else ''
                interactable = Interactable(
                    entity=base,
                    prompt=f'Press E to hack {prefix}{label}',
                    message=f'[ Initiating breach on {label} … ]',
                    callback=make_cb(label, security_level),
                )
                self._interaction.add_interactable(interactable)

    # ================================================================== #
    #  EXTRACTION ZONE  (Phase 5)
    # ================================================================== #
    def _build_extraction_zone(self):
        """
        Create a clearly marked extraction point at EXTRACTION_ZONE_POS.
        Consists of:
          • A flat glowing platform
          • A pulsing outer ring (updated each frame in scenes.py or self)
          • A label text
          • Registered as an interactable with the extraction callback
        """
        ex, ey, ez = EXTRACTION_ZONE_POS
        radius = EXTRACTION_ZONE_RADIUS

        # Flat glowing pad
        pad = Entity(
            model='cube',
            position=(ex, 0.05, ez),
            scale=(radius * 2, 0.1, radius * 2),
            color=color.rgba(*EXTRACTION_ZONE_COLOR, 80),
            unlit=True,
        )
        self.entities.append(pad)

        # Outer ring (will pulse)
        self.extraction_ring = Entity(
            model='cube',
            position=(ex, 0.12, ez),
            scale=(radius * 2 + 0.4, 0.06, radius * 2 + 0.4),
            color=color.rgb(*EXTRACTION_ZONE_COLOR),
            unlit=True,
        )
        self.entities.append(self.extraction_ring)

        # Corner markers (4 small pillars)
        for dx, dz in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            marker = Entity(
                model='cube',
                position=(ex + dx * radius * 0.8, 1.0, ez + dz * radius * 0.8),
                scale=(0.15, 2, 0.15),
                color=color.rgb(*EXTRACTION_ZONE_COLOR),
                unlit=True,
            )
            self.entities.append(marker)

        # Phase 8 — pulsing glow ring around the extraction pad
        extract_glow = GlowPulse(
            parent_entity=pad,
            base_scale=(1.1, 0.08, 1.1),
            glow_color=EXTRACTION_ZONE_COLOR,
            speed=1.5,   # slightly slower pulse for grandeur
        )
        self._glow_effects.append(extract_glow)
        self.entities.append(extract_glow)

        # Register with interaction system
        if self._interaction is not None and self._extraction_cb is not None:
            interactable = Interactable(
                entity=pad,
                prompt='Press E — EXTRACTION ZONE',
                message='[ Attempting extraction… ]',
                callback=self._extraction_cb,
            )
            self._interaction.add_interactable(interactable)

    # ================================================================== #
    #  TERMINAL COLOUR UPDATE
    # ================================================================== #
    def set_terminal_color(self, label, state):
        parts = self.terminal_parts.get(label)
        if parts is None:
            return
        if state == 'active':
            clr = color.rgb(*TERMINAL_COLOR_ACTIVE)
        elif state == 'breached':
            clr = color.rgb(*TERMINAL_COLOR_BREACHED)
        else:
            clr = color.rgb(*TERMINAL_COLOR_LOCKED)
        parts['screen'].color = clr
        parts['accent'].color = clr

    # ================================================================== #
    #  ITEM PICKUPS  (Phase 6)
    # ================================================================== #
    def _build_item_pickups(self):
        """
        Spawn item pickup entities at positions from ITEM_PICKUP_SPECS.
        Each pickup is an ItemPickup that bobs and glows in the world.
        """
        for x, z, item_type in ITEM_PICKUP_SPECS:
            pickup = ItemPickup(
                position=(x, z),           # world x, z coordinates
                item_type=item_type,       # which item this gives
            )
            self.item_pickups.append(pickup)   # track for proximity check
            self.entities.append(pickup)       # track for cleanup

    # ================================================================== #
    #  LIGHTING
    # ================================================================== #
    def _build_lighting(self):
        ambient = AmbientLight(color=color.rgb(*AMBIENT_COLOR))
        self.entities.append(ambient)
        sun = DirectionalLight(y=10, rotation=SUN_ROTATION)
        sun.color = color.rgb(*SUN_COLOR)
        self.entities.append(sun)

    # ================================================================== #
    #  CLEANUP
    # ================================================================== #
    def destroy(self):
        for e in reversed(self.entities):
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.entities.clear()
        self.terminal_parts.clear()
        self.extraction_ring = None
        self.item_pickups.clear()   # Phase 6 — clear pickup refs
        self._glow_effects.clear()  # Phase 8 — clear glow refs
