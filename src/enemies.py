"""
enemies.py — Security Drone Module (Phase 8)
===============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Implements the SecurityDrone — a floating patrol entity with
          three behaviour states: IDLE, SUSPICIOUS, and ALERT.

Phase 8 changes:
    • Distance-based LOD — drones beyond 50 units skip full update
    • Frame-skip for IDLE drones — only update every other frame
    • These optimizations reduce CPU cost with many drones

Behaviour overview:
    IDLE        — hovers around its spawn point with a gentle bob.
    SUSPICIOUS  — player detected at medium range; drone slows and
                  turns to look at the player.
    ALERT       — chases the player aggressively.  Deals damage when
                  close enough.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import random   # random patrol target selection
import math     # sine wave for hover bob

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Vec3,
    color,
    distance,
    time as ursina_time,
    destroy as ursina_destroy,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    DRONE_COLOR_IDLE,
    DRONE_COLOR_SUSPICIOUS,
    DRONE_COLOR_ALERT,
    DRONE_PATROL_SPEED,
    DRONE_CHASE_SPEED,
    DRONE_DETECT_RADIUS,
    DRONE_DAMAGE_RADIUS,
    DRONE_DAMAGE_PER_SEC,
    DRONE_BOB_SPEED,
    DRONE_BOB_AMOUNT,
    DRONE_PATROL_RADIUS,
    DRONE_ALERT_TIMEOUT,
    ALERT_LEVEL_ALERT,
    # Phase 7 — drone SFX constants
    SFX_DRONE_ALERT,
    SFX_DRONE_CHASE,
    SFX_DRONE_HIT,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  State constants
# ══════════════════════════════════════════════════════════════════════════ #
STATE_IDLE       = 'idle'
STATE_SUSPICIOUS = 'suspicious'
STATE_ALERT      = 'alert'


# ══════════════════════════════════════════════════════════════════════════ #
#  SecurityDrone class
# ══════════════════════════════════════════════════════════════════════════ #
class SecurityDrone(Entity):
    """
    A floating security drone with patrol / detect / chase AI.

    Args:
        spawn_pos  : tuple(x, y, z) — initial position in the world.
        player_ref : PlayerController — reference to the player.
        game_state : GameState — reference for damage and alert.

    Usage:
        drone = SecurityDrone((10, 3, -10), player, gs)
        drone.destroy()
    """

    def __init__(self, spawn_pos, player_ref, game_state, audio_manager=None):
        """Build the drone visuals and initialise AI state."""
        # Initialise the Entity base — dark body cube
        super().__init__(
            model='cube',
            scale=(0.8, 0.35, 0.8),
            position=Vec3(*spawn_pos),
            color=color.rgb(15, 12, 30),   # dark body
        )

        # ── Store references ─────────────────────────────────────────── #
        self.player_ref = player_ref       # for distance / position checks
        self.game_state = game_state       # for damage + alert escalation
        self.spawn_pos  = Vec3(*spawn_pos) # home position to return to
        self._audio     = audio_manager    # Phase 7 — audio manager

        # ── Glowing ring underneath (visual indicator) ───────────────── #
        self.glow_ring = Entity(
            parent=self,             # child of drone body
            model='cube',
            scale=(1.3, 0.15, 1.3),  # wider + thinner than body
            position=(0, -0.3, 0),   # below the body
            color=color.rgb(*DRONE_COLOR_IDLE),
            unlit=True,              # always bright
        )

        # ── Small top antenna ────────────────────────────────────────── #
        self.antenna = Entity(
            parent=self,
            model='cube',
            scale=(0.08, 0.4, 0.08),
            position=(0, 0.3, 0),
            color=color.rgb(*DRONE_COLOR_IDLE),
            unlit=True,
        )

        # ── AI state ────────────────────────────────────────────────── #
        self.state = STATE_IDLE           # current behaviour state
        self._patrol_target = None         # next point to wander towards
        self._alert_timer   = 0.0          # countdown to return to idle
        self._suspicious_timer = 0.0       # time in suspicious before alert
        self._bob_phase     = random.uniform(0, math.pi * 2)  # bob offset
        self._base_y        = spawn_pos[1]  # nominal hover height

        # ── EMP disable state (Phase 6) ───────────────────────────── #
        self.emp_disabled = False          # True when hit by EMP
        self._emp_timer   = 0.0            # countdown before reactivation

        # ── Audio throttle (Phase 7) ─────────────────────────────── #
        self._hit_sfx_cooldown = 0.0       # prevents hit spam

        # ── Phase 8: Performance optimization ─────────────────────── #
        self._frame_counter = random.randint(0, 1)  # stagger frame-skips
        self._lod_distance  = 50.0   # beyond this, skip full update

        # Pick an initial patrol target
        self._pick_patrol_target()

    # ================================================================== #
    #  PATROL TARGET
    # ================================================================== #
    def _pick_patrol_target(self):
        """Choose a random point near the spawn position to wander to."""
        offset_x = random.uniform(-DRONE_PATROL_RADIUS, DRONE_PATROL_RADIUS)
        offset_z = random.uniform(-DRONE_PATROL_RADIUS, DRONE_PATROL_RADIUS)
        self._patrol_target = Vec3(
            self.spawn_pos.x + offset_x,
            self._base_y,
            self.spawn_pos.z + offset_z,
        )

    # ================================================================== #
    #  STATE‑COLOUR UPDATE
    # ================================================================== #
    def _set_state_color(self):
        """Update glow ring and antenna colour based on current state."""
        if self.state == STATE_ALERT:
            clr = color.rgb(*DRONE_COLOR_ALERT)
        elif self.state == STATE_SUSPICIOUS:
            clr = color.rgb(*DRONE_COLOR_SUSPICIOUS)
        else:
            clr = color.rgb(*DRONE_COLOR_IDLE)

        self.glow_ring.color = clr
        self.antenna.color   = clr

    # ================================================================== #
    #  UPDATE — main AI loop (called every frame by Ursina)
    # ================================================================== #
    def update(self):
        """Per‑frame AI: detect player, switch states, move, damage."""
        dt = ursina_time.dt  # seconds since last frame

        # ── Phase 8: Frame-skip for IDLE drones (performance) ─────── #
        self._frame_counter += 1
        if (self.state == STATE_IDLE
                and not self.emp_disabled
                and self._frame_counter % 2 != 0):
            return   # skip every other frame when idling

        # ── EMP disable check (Phase 6) ─────────────────────────── #── #
        if self.emp_disabled:
            self._emp_timer -= dt
            if self._emp_timer <= 0:
                # EMP effect expired — reactivate drone
                self.emp_disabled = False
                self.state = STATE_IDLE
                self._set_state_color()   # restore normal colour
            return   # skip all AI while disabled

        # Guard — need a player with a controller
        if (self.player_ref is None
                or self.player_ref.controller is None
                or self.game_state is None):
            return

        player_pos = self.player_ref.controller.position
        dist       = distance(self.position, player_pos)

        # ── Phase 8: Distance LOD — skip full AI for far-away drones ── #
        if dist > self._lod_distance and self.state == STATE_IDLE:
            # Only do minimal bob animation, skip detection logic
            self._bob_phase += DRONE_BOB_SPEED * dt
            self.y = self._base_y + math.sin(self._bob_phase) * DRONE_BOB_AMOUNT
            return

        # ── Global alert override: all drones go ALERT ───────────────── #
        if self.game_state.alert_level >= ALERT_LEVEL_ALERT:
            if self.state != STATE_ALERT:
                self.state = STATE_ALERT
                self._set_state_color()

        # ────────────────────────────────────────────────────────────── #
        #  STATE MACHINE
        # ────────────────────────────────────────────────────────────── #
        if self.state == STATE_IDLE:
            self._do_idle(dt, dist)

        elif self.state == STATE_SUSPICIOUS:
            self._do_suspicious(dt, dist, player_pos)

        elif self.state == STATE_ALERT:
            self._do_alert(dt, dist, player_pos)

    # ================================================================== #
    #  IDLE behaviour
    # ================================================================== #
    def _do_idle(self, dt, dist):
        """Gently hover toward patrol target. Enter suspicious if detected."""
        # ── Hover bob ────────────────────────────────────────────────── #
        self._bob_phase += DRONE_BOB_SPEED * dt
        self.y = self._base_y + math.sin(self._bob_phase) * DRONE_BOB_AMOUNT

        # ── Move toward patrol target ────────────────────────────────── #
        if self._patrol_target is not None:
            direction = (self._patrol_target - self.position).normalized()
            self.position += direction * DRONE_PATROL_SPEED * dt

            # If close enough to the target, pick a new one
            if distance(self.position, self._patrol_target) < 1.0:
                self._pick_patrol_target()

        # ── Detection check ──────────────────────────────────────────── #
        if dist < DRONE_DETECT_RADIUS:
            self.state = STATE_SUSPICIOUS
            self._suspicious_timer = 0.0
            self._set_state_color()
            # Phase 7 — detection alert sound
            if self._audio:
                self._audio.play_sfx(SFX_DRONE_ALERT)

    # ================================================================== #
    #  SUSPICIOUS behaviour
    # ================================================================== #
    def _do_suspicious(self, dt, dist, player_pos):
        """Slow turn toward player. Escalate or calm down."""
        # Hover bob (slower)
        self._bob_phase += DRONE_BOB_SPEED * 0.5 * dt
        self.y = self._base_y + math.sin(self._bob_phase) * DRONE_BOB_AMOUNT

        # Look toward the player (rotate slowly)
        self.look_at(player_pos)

        # Count time spent suspicious
        self._suspicious_timer += dt

        if dist > DRONE_DETECT_RADIUS * 1.3:
            # Player moved out of range — calm down
            self.state = STATE_IDLE
            self._set_state_color()
        elif self._suspicious_timer > 2.0 or dist < DRONE_DAMAGE_RADIUS * 2:
            # Stayed too long or too close — escalate
            self.state = STATE_ALERT
            self._alert_timer = DRONE_ALERT_TIMEOUT
            self._set_state_color()
            # Phase 7 — alert escalation sound
            if self._audio:
                self._audio.play_sfx(SFX_DRONE_CHASE)
            # Raise global alert if not already high
            if self.game_state.alert_level < ALERT_LEVEL_ALERT:
                self.game_state.raise_alert(0.6)

    # ================================================================== #
    #  ALERT behaviour
    # ================================================================== #
    def _do_alert(self, dt, dist, player_pos):
        """Chase the player and deal damage when close."""
        # ── Chase movement ───────────────────────────────────────────── #
        if dist > DRONE_DAMAGE_RADIUS * 0.5:
            direction = (player_pos - self.position).normalized()
            self.position += direction * DRONE_CHASE_SPEED * dt

        # Keep looking at the player
        self.look_at(player_pos)

        # Maintain hover height roughly
        self.y = max(self._base_y - 1, self.y)

        # ── Deal damage if close ───────────────────────────────────── #
        if dist < DRONE_DAMAGE_RADIUS:
            self.game_state.take_damage(DRONE_DAMAGE_PER_SEC * dt)
            # Phase 7 — throttled hit sound (max 1/sec)
            self._hit_sfx_cooldown -= dt
            if self._hit_sfx_cooldown <= 0 and self._audio:
                self._audio.play_sfx(SFX_DRONE_HIT)
                self._hit_sfx_cooldown = 1.0   # reset cooldown

        # ── Check if player escaped ──────────────────────────────────── #
        if dist > DRONE_DETECT_RADIUS * 1.5:
            self._alert_timer -= dt
            if self._alert_timer <= 0:
                # Lost sight — return home
                self.state = STATE_IDLE
                self._patrol_target = Vec3(self.spawn_pos)
                self._set_state_color()
        else:
            # Player still in range — keep chasing
            self._alert_timer = DRONE_ALERT_TIMEOUT

    # ================================================================== #
    #  EMP DISABLE  (Phase 6)
    # ================================================================== #
    def apply_emp(self, duration):
        """
        Disable this drone for *duration* seconds.

        Args:
            duration : float — how long the drone stays disabled.
        """
        self.emp_disabled = True       # freeze AI
        self._emp_timer   = duration   # countdown
        self.state = STATE_IDLE        # reset to idle state
        # Visual: grey out the glow ring while disabled
        self.glow_ring.color = color.rgb(60, 60, 60)   # dim grey
        self.antenna.color   = color.rgb(60, 60, 60)   # dim grey

    # ================================================================== #
    #  CLEANUP
    # ================================================================== #
    def destroy(self):
        """Remove drone and its children from the scene."""
        try:
            ursina_destroy(self.glow_ring)
        except Exception:
            pass
        try:
            ursina_destroy(self.antenna)
        except Exception:
            pass
        self.player_ref = None
        self.game_state = None
        super().destroy()
