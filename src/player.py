"""
player.py — Player Controller Module (Phase 8)
=================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides a first‑person player controller with WASD movement,
          mouse look, jumping, sprinting (Shift), head bob, and camera shake.

Phase 8 changes:
    • Added head bob — subtle vertical oscillation while walking/sprinting
    • Added camera shake integration — CameraFX offsets applied each frame
    • Improved movement feel with smoother camera response

How it connects:
    The SceneManager (scenes.py) creates a PlayerController when
    entering the game scene and calls destroy() on exit.
    effects.py CameraFX provides shake/bob calculations.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import random   # random footstep variant selection (Phase 7)

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
    # Phase 7 — footstep and movement SFX
    SFX_FOOTSTEP_1, SFX_FOOTSTEP_2,
    SFX_JUMP, SFX_LAND,
    FOOTSTEP_WALK_INTERVAL, FOOTSTEP_SPRINT_INTERVAL,
    # Phase 8 — camera polish constants
    HEAD_BOB_SPEED, HEAD_BOB_AMOUNT, HEAD_BOB_SPRINT_MULTIPLIER,
)
from src.effects import CameraFX   # Phase 8 — camera effects helper


# ══════════════════════════════════════════════════════════════════════════ #
#  PlayerController class
# ══════════════════════════════════════════════════════════════════════════ #
class PlayerController(Entity):
    """
    First‑person player with walk, sprint, look, jump, and audio.

    Inherits from Entity so its ``update()`` runs every frame,
    allowing continuous input checks (e.g. held sprint key).

    Attributes:
        controller   : FirstPersonController
        is_sprinting : bool
        _audio       : AudioManager or None (Phase 7)

    Usage:
        player = PlayerController()   # spawns at PLAYER_START_POS
        player.destroy()              # removes from scene
    """

    def __init__(self, audio_manager=None):
        """
        Instantiate the FPS controller and set game defaults.

        Args:
            audio_manager : AudioManager (Phase 7) — optional
        """
        # Initialise the Entity base (invisible, no model)
        super().__init__()

        # Track sprint state for the HUD or other systems
        self.is_sprinting = False

        # Phase 7 — audio manager reference
        self._audio = audio_manager

        # Phase 7 — footstep timer and jump/land tracking
        self._footstep_timer = 0.0
        self._was_grounded   = True   # for landing detection

        # Phase 8 — head bob state
        self._bob_phase  = 0.0   # oscillation phase (radians)
        self._bob_offset = 0.0   # current Y offset from bob

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
        Called every frame by Ursina.  Handles sprinting, footsteps,
        jump detection, landing detection, head bob, and camera shake.
        """
        if self.controller is None:
            return  # guard against post‑destroy calls

        dt = getattr(__import__('ursina', fromlist=['time']), 'time').dt

        # Check if Left Shift is held down
        if held_keys['left shift']:
            # Sprinting — multiply base speed
            self.controller.speed = PLAYER_SPEED * PLAYER_SPRINT_MULTIPLIER
            self.is_sprinting = True
        else:
            # Normal walk speed
            self.controller.speed = PLAYER_SPEED
            self.is_sprinting = False

        # ── Check if player is moving (used by footsteps + head bob) ── #
        is_moving = (
            held_keys['w'] or held_keys['a']
            or held_keys['s'] or held_keys['d']
        )

        # ── Phase 8: Head bob ─────────────────────────────────────── #
        if self.controller.grounded and self.controller.enabled:
            self._bob_phase, self._bob_offset = CameraFX.head_bob(
                phase=self._bob_phase,
                dt=dt,
                is_moving=is_moving,
                is_sprinting=self.is_sprinting,
                bob_speed=HEAD_BOB_SPEED,
                bob_amount=HEAD_BOB_AMOUNT,
                sprint_multiplier=HEAD_BOB_SPRINT_MULTIPLIER,
            )
        else:
            # Airborne or disabled — no head bob
            self._bob_offset = 0.0

        # ── Phase 8: Camera shake + head bob application ──────────── #
        shake_x, shake_y = CameraFX.update_shake(dt)
        # Apply combined offsets to the camera
        try:
            self.controller.camera_pivot.y = 2 + self._bob_offset + shake_y
            self.controller.camera_pivot.x = shake_x
        except Exception:
            pass   # guard if camera_pivot is unavailable

        # ── Phase 7: Footstep audio ────────────────────────────────── #
        if self._audio and self.controller.grounded:
            if is_moving:
                # Choose interval based on sprint state
                interval = (FOOTSTEP_SPRINT_INTERVAL
                            if self.is_sprinting
                            else FOOTSTEP_WALK_INTERVAL)
                self._footstep_timer += dt
                if self._footstep_timer >= interval:
                    self._footstep_timer = 0.0
                    # Alternate footstep variants
                    sfx = random.choice([SFX_FOOTSTEP_1, SFX_FOOTSTEP_2])
                    self._audio.play_sfx(sfx)
            else:
                self._footstep_timer = 0.0   # reset when standing still

        # ── Phase 7: Jump / land detection ─────────────────────────── #
        if self._audio:
            grounded_now = self.controller.grounded
            if self._was_grounded and not grounded_now:
                # Just left the ground → jump
                self._audio.play_sfx(SFX_JUMP)
            elif not self._was_grounded and grounded_now:
                # Just landed → land
                self._audio.play_sfx(SFX_LAND)
            self._was_grounded = grounded_now

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
