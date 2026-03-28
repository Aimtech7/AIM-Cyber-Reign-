"""
player.py — Player Controller Module (Phase 2)
=================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides a first‑person player controller with WASD movement,
          mouse look, jumping, and **sprinting** (hold Shift).

Changes in Phase 2:
    • Added sprint mechanic — holding Left Shift increases speed
    • Created a custom Entity subclass so update() runs each frame
      for continuous sprint detection

How it connects:
    The SceneManager (scenes.py) creates a PlayerController when
    entering the game scene and calls destroy() on exit.

Key concepts:
    • We subclass Entity so we get an automatic update() callback.
    • Inside update(), we check whether Left Shift is held and
      adjust the controller's speed accordingly.
    • The base speed comes from config.py (PLAYER_SPEED).
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Vec2,
    held_keys,               # dictionary of currently held keys
    destroy as ursina_destroy,
)
from ursina.prefabs.first_person_controller import FirstPersonController

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    PLAYER_SPEED,
    PLAYER_SPRINT_MULTIPLIER,
    PLAYER_JUMP_HEIGHT,
    PLAYER_MOUSE_SENSITIVITY,
    PLAYER_START_POS,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  PlayerController class
# ══════════════════════════════════════════════════════════════════════════ #
class PlayerController(Entity):
    """
    First‑person player with walk, sprint, look, and jump.

    Inherits from Entity so its ``update()`` runs every frame,
    allowing continuous input checks (e.g. held sprint key).

    Attributes:
        controller : FirstPersonController
            The underlying Ursina prefab that handles physics.
        is_sprinting : bool
            Whether the player is currently sprinting.

    Usage:
        player = PlayerController()   # spawns at PLAYER_START_POS
        player.destroy()              # removes from scene
    """

    def __init__(self):
        """
        Instantiate the FPS controller and set game defaults.
        """
        # Initialise the Entity base (invisible, no model)
        super().__init__()

        # Track sprint state for the HUD or other systems
        self.is_sprinting = False

        # Create the Ursina first‑person controller
        self.controller = FirstPersonController(
            speed=PLAYER_SPEED,                              # walk speed
            jump_height=PLAYER_JUMP_HEIGHT,                  # jump height
            mouse_sensitivity=Vec2(*PLAYER_MOUSE_SENSITIVITY),  # look speed
            position=PLAYER_START_POS,                       # spawn point
        )

        # Hide the default grey crosshair dot — we have our own HUD
        self.controller.cursor.visible = False

    # ------------------------------------------------------------------ #
    #  Per‑frame update (sprint detection)
    # ------------------------------------------------------------------ #
    def update(self):
        """
        Called every frame by Ursina.  Checks if the player is holding
        Left Shift and adjusts movement speed for sprinting.
        """
        if self.controller is None:
            return  # guard against post‑destroy calls

        # Check if Left Shift is held down
        if held_keys['left shift']:
            # Sprinting — multiply base speed
            self.controller.speed = PLAYER_SPEED * PLAYER_SPRINT_MULTIPLIER
            self.is_sprinting = True
        else:
            # Normal walk speed
            self.controller.speed = PLAYER_SPEED
            self.is_sprinting = False

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """
        Remove the player entity and controller from the scene.
        """
        try:
            ursina_destroy(self.controller)  # remove the FPS controller
        except Exception:
            pass
        self.controller = None
        super().destroy()   # remove this Entity itself
