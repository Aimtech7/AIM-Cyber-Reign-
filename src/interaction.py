"""
interaction.py — Interaction System Module (Phase 3)
======================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Reusable interaction framework.  Any 3D object can be registered
          as "interactable"; when the player walks close enough a prompt
          appears; pressing the interact key triggers a callback.

Phase 3 changes:
    • Added ``paused`` flag — when True, the system stops checking
      proximity and ignores input (used while the hacking panel is open).
    • Added ``update_prompt()`` to change an interactable's prompt text
      after registration (e.g. from "Press E to hack" to "BREACHED").

How it connects:
    • environment.py registers cyber terminals via add_interactable().
    • scenes.py creates the InteractionSystem and pauses/unpauses it
      around hacking sessions.
    • The system's update() runs every frame (inherits from Entity).
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Text,
    color,
    distance,
    destroy as ursina_destroy,
    time as ursina_time,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    INTERACT_DISTANCE,
    INTERACT_KEY,
    INTERACT_MSG_DURATION,
    NEON_YELLOW,
    NEON_GREEN,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  Interactable data holder
# ══════════════════════════════════════════════════════════════════════════ #
class Interactable:
    """
    Bundles an Ursina Entity with interaction metadata.

    Attributes:
        entity   : Entity   — the 3D object in the world
        prompt   : str      — text shown when the player is near
        message  : str      — text shown after interaction
        callback : callable — optional extra logic on interact
    """

    def __init__(self, entity, prompt="Press E to interact",
                 message="Accessed", callback=None):
        self.entity   = entity
        self.prompt   = prompt
        self.message  = message
        self.callback = callback


# ══════════════════════════════════════════════════════════════════════════ #
#  InteractionSystem
# ══════════════════════════════════════════════════════════════════════════ #
class InteractionSystem(Entity):
    """
    Checks every frame whether the player is near any registered
    Interactable, shows a prompt, and handles the interact key.

    Attributes:
        paused : bool — when True, proximity checks and input are skipped.
    """

    def __init__(self, player_ref, **kwargs):
        super().__init__(**kwargs)

        # Reference to the player controller
        self.player_ref = player_ref

        # List of registered Interactable objects
        self.interactables = []

        # Currently active (nearest) interactable, or None
        self._active = None

        # Pause flag — set True while the hacking panel is open
        self.paused = False

        # ── Prompt text (hidden by default) ──────────────────────────── #
        self.prompt_text = Text(
            text='',
            position=(0, -0.15),
            origin=(0, 0),
            scale=1.3,
            color=color.rgb(*NEON_YELLOW),
            font='VeraMono.ttf',
            visible=False,
        )

        # ── Feedback message text (hidden by default) ────────────────── #
        self.message_text = Text(
            text='',
            position=(0, -0.05),
            origin=(0, 0),
            scale=1.4,
            color=color.rgb(*NEON_GREEN),
            font='VeraMono.ttf',
            visible=False,
        )

        # Timer for the feedback message
        self._msg_timer = 0.0

    # ------------------------------------------------------------------ #
    #  Registration
    # ------------------------------------------------------------------ #
    def add_interactable(self, interactable):
        """Register an Interactable for tracking."""
        self.interactables.append(interactable)

    # ------------------------------------------------------------------ #
    #  Update prompt text of a registered interactable
    # ------------------------------------------------------------------ #
    def update_prompt(self, entity, new_prompt, new_message=None):
        """
        Change the prompt (and optionally message) for an interactable
        identified by its entity reference.

        Args:
            entity      : Entity — the 3D object originally registered
            new_prompt  : str    — replacement prompt text
            new_message : str or None — replacement message (optional)
        """
        for inter in self.interactables:
            if inter.entity is entity:
                inter.prompt = new_prompt
                if new_message is not None:
                    inter.message = new_message
                # Also disable the callback so it can't be hacked again
                inter.callback = None
                break

    # ------------------------------------------------------------------ #
    #  Per‑frame update
    # ------------------------------------------------------------------ #
    def update(self):
        """
        Each frame: find nearest interactable in range, show prompt.
        Skipped entirely when self.paused is True.
        """
        # Tick message timer regardless of pause
        if self._msg_timer > 0:
            self._msg_timer -= ursina_time.dt
            if self._msg_timer <= 0:
                self.message_text.visible = False

        # Skip proximity logic when paused (hacking panel is open)
        if self.paused:
            self.prompt_text.visible = False
            self._active = None
            return

        # Guard: need a player
        if self.player_ref is None or self.player_ref.controller is None:
            return

        player_pos = self.player_ref.controller.position

        # Find nearest in range
        nearest      = None
        nearest_dist = INTERACT_DISTANCE + 1

        for inter in self.interactables:
            dist = distance(player_pos, inter.entity.position)
            if dist < INTERACT_DISTANCE and dist < nearest_dist:
                nearest      = inter
                nearest_dist = dist

        # Update visibility
        if nearest is not None:
            self._active = nearest
            self.prompt_text.text    = nearest.prompt
            self.prompt_text.visible = True
        else:
            self._active = None
            self.prompt_text.visible = False

    # ------------------------------------------------------------------ #
    #  Input handler
    # ------------------------------------------------------------------ #
    def input(self, key):
        """Handle the interact key. Skipped when paused."""
        if self.paused:
            return  # hacking panel is handling input

        if key == INTERACT_KEY and self._active is not None:
            self.message_text.text    = self._active.message
            self.message_text.visible = True
            self._msg_timer = INTERACT_MSG_DURATION

            if self._active.callback:
                self._active.callback()

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove the system, prompt text, message text, and all refs."""
        try:
            ursina_destroy(self.prompt_text)
        except Exception:
            pass
        try:
            ursina_destroy(self.message_text)
        except Exception:
            pass
        self.interactables.clear()
        self.player_ref = None
        super().destroy()
