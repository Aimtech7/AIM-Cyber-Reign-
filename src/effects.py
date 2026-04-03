"""
effects.py — Visual Effects Module (Phase 8)
===============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides lightweight, reusable visual effects to polish the
          game feel without heavy post-processing shaders.

Three effect systems:
    • GlowPulse       — oscillates scale/alpha on an entity (neon glow)
    • ParticleEmitter  — spawns and manages short-lived particle bursts
    • CameraFX        — static helpers for camera shake and head bob

How it connects:
    environment.py attaches GlowPulse to terminals and extraction zones.
    scenes.py calls ParticleEmitter for EMP / hack / alert events.
    player.py uses CameraFX for head bob each frame.
    game_state.py triggers CameraFX.shake on damage.

Design notes:
    Ursina doesn't have built-in bloom/glow shaders, so we simulate
    glow with unlit entities whose scale and alpha pulse over time.
    This is cheap and looks great on all hardware.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import math     # sine wave for pulse animations
import random   # random offsets for particles

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    camera,
    color,
    time as ursina_time,
    destroy as ursina_destroy,
    Vec3,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    GLOW_PULSE_SPEED,
    GLOW_PULSE_MIN_SCALE,
    GLOW_PULSE_MAX_SCALE,
    GLOW_PULSE_MIN_ALPHA,
    GLOW_PULSE_MAX_ALPHA,
    PARTICLE_LIFETIME,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  GlowPulse — oscillating neon glow on any entity
# ══════════════════════════════════════════════════════════════════════════ #
class GlowPulse(Entity):
    """
    Attaches to a parent entity and pulses its scale and alpha in a
    sine wave pattern, creating a breathing neon-glow effect.

    Args:
        parent_entity : Entity — the object to pulse around
        base_scale    : tuple  — (x, y, z) resting scale
        glow_color    : tuple  — (R, G, B) colour for the glow ring
        speed         : float  — oscillation speed (overrides config)
        offset        : float  — phase offset so multiple glows aren't in sync

    Usage:
        glow = GlowPulse(terminal_entity, (1.2, 0.1, 1.2), NEON_CYAN)
        glow.destroy()   # remove when done
    """

    def __init__(self, parent_entity, base_scale, glow_color,
                 speed=None, offset=None):
        """Create the glow ring as a child of the parent entity."""
        # Use config speed if not overridden
        self._speed = speed or GLOW_PULSE_SPEED

        # Random phase offset so glows aren't synchronised
        self._phase = offset if offset is not None else random.uniform(0, math.pi * 2)

        # Store the base scale components
        self._base_sx = base_scale[0]
        self._base_sy = base_scale[1]
        self._base_sz = base_scale[2]

        # Store colour for alpha pulsing
        self._r = glow_color[0]
        self._g = glow_color[1]
        self._b = glow_color[2]

        # Create the glow ring entity as a child of the parent
        super().__init__(
            parent=parent_entity,
            model='cube',
            scale=base_scale,
            position=(0, -0.3, 0),   # slightly below the parent
            color=color.rgba(self._r, self._g, self._b, GLOW_PULSE_MAX_ALPHA),
            unlit=True,              # always bright — ignore scene lighting
        )

    def update(self):
        """Per-frame: oscillate scale and alpha using a sine wave."""
        self._phase += self._speed * ursina_time.dt

        # Sine value mapped to 0–1 range
        t = (math.sin(self._phase) + 1.0) * 0.5

        # Interpolate scale between min and max
        scale_factor = GLOW_PULSE_MIN_SCALE + t * (GLOW_PULSE_MAX_SCALE - GLOW_PULSE_MIN_SCALE)
        self.scale_x = self._base_sx * scale_factor
        self.scale_z = self._base_sz * scale_factor
        # Keep Y (height) constant for a flat ring effect

        # Interpolate alpha between min and max
        alpha = int(GLOW_PULSE_MIN_ALPHA + t * (GLOW_PULSE_MAX_ALPHA - GLOW_PULSE_MIN_ALPHA))
        self.color = color.rgba(self._r, self._g, self._b, alpha)


# ══════════════════════════════════════════════════════════════════════════ #
#  ParticleEmitter — lightweight burst particle system
# ══════════════════════════════════════════════════════════════════════════ #
class ParticleEmitter:
    """
    Spawns a group of small entities that drift outward then fade
    and self-destruct after PARTICLE_LIFETIME seconds.

    This is a one-shot system — create it, it plays, it cleans itself up.

    Args:
        position     : Vec3 or tuple — world position of the burst centre
        count        : int           — number of particles
        particle_color : tuple       — (R, G, B) base colour
        speed        : float         — outward drift speed
        spread       : float         — random spread angle
        direction    : str           — 'outward' (ring) or 'upward' (fountain)
        lifetime     : float         — seconds before cleanup (default from config)

    Usage:
        ParticleEmitter(Vec3(0, 1, 0), 10, (0, 255, 255), direction='upward')
    """

    def __init__(self, position, count, particle_color,
                 speed=3.0, spread=1.0, direction='outward',
                 lifetime=None):
        """Spawn all particles immediately."""
        self.particles = []
        self._lifetime = lifetime or PARTICLE_LIFETIME
        self._elapsed  = 0.0

        # Convert position to Vec3 if needed
        if not isinstance(position, Vec3):
            position = Vec3(*position)

        # Spawn particles
        for _ in range(count):
            # Random direction vector
            if direction == 'upward':
                # Fountain: mostly Y-up with slight XZ spread
                vx = random.uniform(-spread * 0.3, spread * 0.3)
                vy = random.uniform(0.5, 1.0)
                vz = random.uniform(-spread * 0.3, spread * 0.3)
            else:
                # Outward ring: spread in XZ, slight Y
                vx = random.uniform(-spread, spread)
                vy = random.uniform(-0.2, 0.4)
                vz = random.uniform(-spread, spread)

            # Normalise and apply speed
            vel = Vec3(vx, vy, vz).normalized() * speed

            # Random size
            size = random.uniform(0.05, 0.15)

            # Random alpha for variety
            alpha = random.randint(120, 220)

            # Create the particle entity
            p = _Particle(
                position=position,
                velocity=vel,
                size=size,
                particle_color=particle_color,
                alpha=alpha,
                lifetime=self._lifetime,
            )
            self.particles.append(p)


class _Particle(Entity):
    """
    A single particle — drifts along its velocity, shrinks, then
    auto-destroys after its lifetime expires.

    This is an internal class used by ParticleEmitter; don't create
    directly.
    """

    def __init__(self, position, velocity, size, particle_color,
                 alpha, lifetime):
        """Spawn a tiny glowing quad at the given position."""
        super().__init__(
            model='quad',
            scale=(size, size),
            position=position,
            color=color.rgba(*particle_color, alpha),
            unlit=True,
            billboard=True,   # always faces the camera
        )
        self._velocity  = velocity       # drift direction
        self._lifetime  = lifetime       # total lifetime
        self._elapsed   = 0.0            # time alive
        self._start_scale = size         # for shrink animation
        self._alpha     = alpha          # starting alpha
        # Random initial rotation and spin speed
        self.rotation_z = random.uniform(0, 360)
        self._spin_speed = random.uniform(-180, 180)

    def update(self):
        """Move, shrink, spin, fade, and auto-destroy."""
        dt = ursina_time.dt
        self._elapsed += dt

        # Normalised age (0 → 1)
        t = min(self._elapsed / self._lifetime, 1.0)

        # Drift along velocity (slow down over time)
        speed_factor = 1.0 - t * 0.7   # decelerates
        self.position += self._velocity * speed_factor * dt

        # Spin around local Z axis
        self.rotation_z += self._spin_speed * dt

        # Shrink toward zero
        current_scale = self._start_scale * (1.0 - t)
        self.scale = (current_scale, current_scale)

        # Fade alpha
        current_alpha = int(self._alpha * (1.0 - t))
        self.color = color.rgba(
            self.color.r * 255,
            self.color.g * 255,
            self.color.b * 255,
            max(0, current_alpha),
        )

        # Auto-destroy when lifetime is up
        if self._elapsed >= self._lifetime:
            ursina_destroy(self)


# ══════════════════════════════════════════════════════════════════════════ #
#  CameraFX — static camera effects (shake, head bob)
# ══════════════════════════════════════════════════════════════════════════ #
class CameraFX:
    """
    Static methods for camera effects.  These don't create entities —
    they modify camera position/rotation directly from the caller's
    update loop.

    Shake state is stored as class variables so it persists between frames.
    """

    # ── Shake state (class-level) ────────────────────────────────────── #
    _shake_intensity = 0.0     # current shake amplitude
    _shake_duration  = 0.0     # remaining shake time
    _shake_elapsed   = 0.0     # time since shake started
    _shake_total     = 0.0     # total shake duration (for decay)

    @classmethod
    def trigger_shake(cls, intensity, duration):
        """
        Start a camera shake effect.

        Args:
            intensity : float — maximum offset (world units)
            duration  : float — how long the shake lasts (seconds)
        """
        cls._shake_intensity = intensity
        cls._shake_duration  = duration
        cls._shake_elapsed   = 0.0
        cls._shake_total     = duration

    @classmethod
    def update_shake(cls, dt):
        """
        Apply the current shake offset to the camera.
        Call this every frame from the player's update loop.

        Args:
            dt : float — seconds since last frame

        Returns:
            tuple(float, float) — (offset_x, offset_y) to add to camera
        """
        if cls._shake_duration <= 0:
            return 0.0, 0.0   # no active shake

        cls._shake_elapsed += dt
        cls._shake_duration -= dt

        # Decay: intensity reduces as shake progresses
        decay = max(0.0, 1.0 - (cls._shake_elapsed / cls._shake_total))
        current = cls._shake_intensity * decay

        # Random offset within current intensity
        offset_x = random.uniform(-current, current)
        offset_y = random.uniform(-current, current)

        return offset_x, offset_y

    @staticmethod
    def head_bob(phase, dt, is_moving, is_sprinting, bob_speed, bob_amount,
                 sprint_multiplier):
        """
        Calculate a vertical head-bob offset for natural walking feel.

        Args:
            phase             : float — current oscillation phase (radians)
            dt                : float — frame delta time
            is_moving         : bool  — is the player walking?
            is_sprinting      : bool  — is the player running?
            bob_speed         : float — oscillation frequency
            bob_amount        : float — vertical amplitude
            sprint_multiplier : float — speed multiplier when sprinting

        Returns:
            tuple(float, float) — (new_phase, y_offset)
        """
        if not is_moving:
            # Smoothly return to zero when standing still
            return phase, 0.0

        # Apply sprint speed boost
        speed = bob_speed
        amount = bob_amount
        if is_sprinting:
            speed *= sprint_multiplier
            amount *= sprint_multiplier * 0.8   # slightly bigger bob

        # Advance the phase
        phase += speed * dt

        # Calculate the vertical offset using a sine wave
        y_offset = math.sin(phase) * amount

        return phase, y_offset
