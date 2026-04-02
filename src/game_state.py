"""
game_state.py — Game State Tracking Module (Phase 4)
======================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Tracks global game progress: breached terminals, access
          level, player health, global alert level, and aggregate stats.

Phase 4 additions:
    • Player health system with damage, regen, and regen delay
    • Global alert level (CALM / SUSPICIOUS / ALERT) with decay timer
    • Alert escalation from hacking outcomes
"""

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    PLAYER_MAX_HEALTH,
    PLAYER_HEALTH_REGEN,
    PLAYER_REGEN_DELAY,
    ALERT_LEVEL_CALM,
    ALERT_LEVEL_SUSPICIOUS,
    ALERT_LEVEL_ALERT,
    ALERT_DECAY_TIME,
    ALERT_ON_HACK_FAIL,
    ALERT_ON_HACK_SUCCESS_PER_LEVEL,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  GameState class
# ══════════════════════════════════════════════════════════════════════════ #
class GameState:
    """
    Centralised tracker for all gameplay‑critical data.

    Attributes — Terminals:
        total_terminals   : int
        breached_labels   : set
        access_level      : int

    Attributes — Health (Phase 4):
        health            : float  — current HP (0–PLAYER_MAX_HEALTH)
        _damage_cooldown  : float  — countdown before regen starts

    Attributes — Alert (Phase 4):
        alert_accumulator : float  — raw alert value
        alert_level       : int    — 0=CALM, 1=SUSPICIOUS, 2=ALERT
        _alert_decay      : float  — countdown before alert drops
    """

    def __init__(self, total_terminals=0):
        """Initialise game state with full health and calm alert."""
        # ── Terminal tracking (Phase 3) ──────────────────────────────── #
        self.total_terminals = total_terminals
        self.breached_labels = set()
        self.access_level    = 1

        # ── Player health (Phase 4) ──────────────────────────────────── #
        self.health          = PLAYER_MAX_HEALTH   # start at full HP
        self._damage_cooldown = 0.0                 # time since last damage

        # ── Alert system (Phase 4) ───────────────────────────────────── #
        self.alert_accumulator = 0.0   # raw alert score
        self.alert_level       = ALERT_LEVEL_CALM   # derived level
        self._alert_decay      = 0.0   # countdown timer

        # ── Inventory integration (Phase 6) ──────────────────────────── #
        self.hack_boost_active = False   # set True by Hack Booster item

    # ================================================================== #
    #  TERMINAL METHODS  (Phase 3 — unchanged)
    # ================================================================== #
    def breach_terminal(self, label):
        """Mark a terminal as breached. Returns True if new breach."""
        if label in self.breached_labels:
            return False
        self.breached_labels.add(label)
        self.access_level = 1 + len(self.breached_labels) // 2
        return True

    def is_breached(self, label):
        """Check whether a terminal has already been hacked."""
        return label in self.breached_labels

    def get_stats(self):
        """Return a dict of stats for the HUD."""
        return {
            'total':            self.total_terminals,
            'breached':         len(self.breached_labels),
            'access_level':     self.access_level,
            'labels':           self.breached_labels.copy(),
            'health':           self.health,
            'max_health':       PLAYER_MAX_HEALTH,
            'alert_level':      self.alert_level,
        }

    # ================================================================== #
    #  HEALTH METHODS  (Phase 4)
    # ================================================================== #
    def take_damage(self, amount):
        """
        Reduce player health by *amount*.  Clamps at 0.

        Args:
            amount : float — HP to subtract.

        Returns:
            bool — True if the player is still alive.
        """
        self.health = max(0.0, self.health - amount)
        self._damage_cooldown = PLAYER_REGEN_DELAY   # reset regen delay
        return self.health > 0

    def heal(self, amount):
        """
        Restore player health by *amount*.  Clamps at max.

        Args:
            amount : float — HP to add.

        Phase 6 — called by EnergyCellItem.
        """
        self.health = min(PLAYER_MAX_HEALTH, self.health + amount)

    def is_alive(self):
        """Check if the player still has health remaining."""
        return self.health > 0

    def update_health(self, dt):
        """
        Called each frame.  Handles regeneration after a delay.

        Args:
            dt : float — seconds since last frame.
        """
        if self.health >= PLAYER_MAX_HEALTH:
            return  # already full — skip

        # Count down the damage cooldown
        if self._damage_cooldown > 0:
            self._damage_cooldown -= dt
            return  # still cooling down — no regen yet

        # Regenerate health
        self.health = min(PLAYER_MAX_HEALTH,
                          self.health + PLAYER_HEALTH_REGEN * dt)

    # ================================================================== #
    #  ALERT METHODS  (Phase 4)
    # ================================================================== #
    def raise_alert(self, amount):
        """
        Increase the global alert score and recalculate the level.

        Args:
            amount : float — how much to add to the raw accumulator.
        """
        self.alert_accumulator = min(2.0, self.alert_accumulator + amount)
        self._alert_decay = ALERT_DECAY_TIME   # reset the decay timer
        self._recalc_alert()

    def alert_from_hack(self, success, security_level):
        """
        Raise alert based on a hacking outcome.

        Args:
            success        : bool — True if breach succeeded
            security_level : int  — 1–3
        """
        if success:
            # Small alert proportional to terminal difficulty
            self.raise_alert(ALERT_ON_HACK_SUCCESS_PER_LEVEL * security_level)
        else:
            # Failed hack is much noisier
            self.raise_alert(ALERT_ON_HACK_FAIL)

    def update_alert(self, dt):
        """
        Called each frame.  Decays the alert level over time when
        no new alerts are raised.

        Args:
            dt : float — seconds since last frame.
        """
        if self.alert_accumulator <= 0:
            return  # already calm — nothing to do

        # Count down the decay timer
        if self._alert_decay > 0:
            self._alert_decay -= dt
            return  # still within the hold window

        # Decay the accumulator
        self.alert_accumulator = max(0.0, self.alert_accumulator - dt * 0.15)
        self._recalc_alert()

    def _recalc_alert(self):
        """Derive the integer alert level from the raw accumulator."""
        if self.alert_accumulator >= 1.5:
            self.alert_level = ALERT_LEVEL_ALERT        # 2
        elif self.alert_accumulator >= 0.5:
            self.alert_level = ALERT_LEVEL_SUSPICIOUS   # 1
        else:
            self.alert_level = ALERT_LEVEL_CALM         # 0

    # ================================================================== #
    #  CLEANUP
    # ================================================================== #
    def destroy(self):
        """Reset all state. Called on scene exit."""
        self.breached_labels.clear()
        self.access_level      = 1
        self.total_terminals   = 0
        self.health            = PLAYER_MAX_HEALTH
        self._damage_cooldown  = 0.0
        self.alert_accumulator = 0.0
        self.alert_level       = ALERT_LEVEL_CALM
        self._alert_decay      = 0.0
        self.hack_boost_active = False   # Phase 6 — reset boost flag
