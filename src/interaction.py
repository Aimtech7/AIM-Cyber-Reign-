"""
interaction.py — Interaction System Module
=============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides a reusable interaction framework.  Any 3D object
          can be registered as "interactable"; when the player walks
          close enough, a prompt appears, and pressing the interact
          key triggers a callback.

How it connects:
    • environment.py registers cyber terminals via add_interactable().
    • scenes.py creates the InteractionSystem when entering the game
      scene and passes it a reference to the player controller.
    • The system's update() runs every frame (it inherits from Entity).

Key concepts:
    • ``Interactable`` is a data class that bundles an entity with its
      prompt text and callback function.
    • ``InteractionSystem`` inherits from Ursina ``Entity`` so its
      ``update()`` method is called automatically each frame.
    • Distance checks use ``distance()`` between the player position
      and each interactable's world position.

Why a separate file:
    Keeping interaction logic isolated means new interactable types
    (doors, loot boxes, NPCs) can be added without modifying existing
    code — just call ``system.add_interactable(...)``.
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,       # base class — gives us update() each frame
    Text,         # on‑screen prompt text
    color,        # colour helpers
    distance,     # distance between two entities / positions
    destroy as ursina_destroy,
    time as ursina_time,    # delta‑time access
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
        """
        Args:
            entity   : the world‑space Entity to interact with
            prompt   : hint text displayed near the crosshair
            message  : confirmation text shown after pressing E
            callback : optional function called on interaction
        """
        self.entity   = entity    # the 3D object
        self.prompt   = prompt    # "Press E to …"
        self.message  = message   # "Access Node Connected"
        self.callback = callback  # extra logic (or None)


# ══════════════════════════════════════════════════════════════════════════ #
#  InteractionSystem
# ══════════════════════════════════════════════════════════════════════════ #
class InteractionSystem(Entity):
    """
    Checks every frame whether the player is near any registered
    Interactable, shows a prompt, and handles the interact key.

    Usage:
        system = InteractionSystem(player_ref=my_player_controller)
        system.add_interactable(Interactable(entity, prompt, message))
        # … later …
        system.destroy()
    """

    def __init__(self, player_ref, **kwargs):
        """
        Args:
            player_ref : PlayerController — reference to the active player
        """
        # Initialise the Entity base (invisible, no model)
        super().__init__(**kwargs)

        # Store reference to the player so we can check distance
        self.player_ref = player_ref

        # List of registered Interactable objects
        self.interactables = []

        # Currently active (nearest) interactable, or None
        self._active = None

        # ── Prompt text (hidden by default) ──────────────────────────── #
        self.prompt_text = Text(
            text='',                           # initially empty
            position=(0, -0.15),               # centre‑bottom of screen
            origin=(0, 0),                     # centred anchor
            scale=1.3,                         # readable size
            color=color.rgb(*NEON_YELLOW),     # neon yellow for visibility
            font='VeraMono.ttf',
            visible=False,                     # hidden until needed
        )

        # ── Feedback message text (hidden by default) ────────────────── #
        self.message_text = Text(
            text='',
            position=(0, -0.05),               # just above prompt area
            origin=(0, 0),
            scale=1.4,
            color=color.rgb(*NEON_GREEN),      # neon green = success
            font='VeraMono.ttf',
            visible=False,
        )

        # Timer controlling how long the feedback message stays visible
        self._msg_timer = 0.0

    # ------------------------------------------------------------------ #
    #  Registration
    # ------------------------------------------------------------------ #
    def add_interactable(self, interactable):
        """
        Register an Interactable so the system starts tracking it.

        Args:
            interactable : Interactable instance
        """
        self.interactables.append(interactable)

    # ------------------------------------------------------------------ #
    #  Per‑frame update (called automatically by Ursina)
    # ------------------------------------------------------------------ #
    def update(self):
        """
        Each frame:
          1. Find the nearest interactable within range.
          2. Show / hide the prompt accordingly.
          3. Count down the feedback message timer.
        """
        # ── Tick message timer ───────────────────────────────────────── #
        if self._msg_timer > 0:
            self._msg_timer -= ursina_time.dt     # subtract elapsed time
            if self._msg_timer <= 0:
                self.message_text.visible = False  # hide when timer expires

        # ── Guard: need a player to check distance ───────────────────── #
        if self.player_ref is None or self.player_ref.controller is None:
            return

        # Player world position (from the FPS controller)
        player_pos = self.player_ref.controller.position

        # ── Find nearest interactable in range ───────────────────────── #
        nearest     = None
        nearest_dist = INTERACT_DISTANCE + 1  # start beyond max range

        for inter in self.interactables:
            dist = distance(player_pos, inter.entity.position)  # 3D dist
            if dist < INTERACT_DISTANCE and dist < nearest_dist:
                nearest      = inter
                nearest_dist = dist

        # ── Update prompt visibility ─────────────────────────────────── #
        if nearest is not None:
            self._active = nearest
            self.prompt_text.text = nearest.prompt   # e.g. "Press E …"
            self.prompt_text.visible = True
        else:
            self._active = None
            self.prompt_text.visible = False

    # ------------------------------------------------------------------ #
    #  Input handler (called automatically by Ursina)
    # ------------------------------------------------------------------ #
    def input(self, key):
        """
        Listen for the interact key.  If an interactable is active,
        trigger it and display the feedback message.

        Args:
            key : str — key that was pressed
        """
        if key == INTERACT_KEY and self._active is not None:
            # Show feedback message
            self.message_text.text = self._active.message
            self.message_text.visible = True
            self._msg_timer = INTERACT_MSG_DURATION   # start countdown

            # Run the optional callback (if any)
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
        super().destroy()   # remove the Entity itself
