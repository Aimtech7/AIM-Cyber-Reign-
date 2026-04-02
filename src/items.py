"""
items.py — Item Definitions Module
=====================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Defines the Item base class and three concrete item types
          used by the inventory and equipment systems.

Item types:
    EnergyCellItem   — restores player health
    HackBoosterItem  — adds bonus time to the next hack attempt
    EMPPulseItem     — temporarily disables nearby security drones

How it connects:
    inventory.py creates instances of these classes.
    Each item's use() method interacts with game_state, hacking,
    or enemies via passed references and callbacks.
"""

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    ITEM_ENERGY_CELL_HEAL,     # HP restored by Energy Cell
    ITEM_HACK_BOOSTER_TIME,    # bonus seconds for Hack Booster
    ITEM_EMP_RADIUS,           # EMP disable radius
    ITEM_EMP_DURATION,         # EMP disable duration
)


# ══════════════════════════════════════════════════════════════════════════ #
#  Item base class
# ══════════════════════════════════════════════════════════════════════════ #
class Item:
    """
    Abstract base class for all inventory items.

    Attributes:
        name        : str  — display name (e.g. "Energy Cell")
        description : str  — short tooltip text
        icon_char   : str  — single character for HUD display
        item_type   : str  — unique type key for stacking/lookup
        stackable   : bool — whether duplicates stack in one slot
        max_stack   : int  — maximum count per stack
    """

    def __init__(self, name, description, icon_char, item_type,
                 stackable=True, max_stack=5):
        """
        Initialise an item.

        Args:
            name        : str  — human‑readable name
            description : str  — tooltip text
            icon_char   : str  — HUD icon character
            item_type   : str  — type key (e.g. 'energy_cell')
            stackable   : bool — can items of this type stack?
            max_stack   : int  — max per stack
        """
        self.name        = name          # display name
        self.description = description   # short description
        self.icon_char   = icon_char     # single‑char icon
        self.item_type   = item_type     # unique type identifier
        self.stackable   = stackable     # stacking allowed?
        self.max_stack   = max_stack     # max per slot

    def use(self, game_state, **context):
        """
        Activate the item's effect.

        Args:
            game_state : GameState — central game data
            **context  : dict      — extra refs (emp_callback, etc.)

        Returns:
            bool — True if the item was successfully consumed.
        """
        return False   # base class does nothing — subclasses override


# ══════════════════════════════════════════════════════════════════════════ #
#  Energy Cell — restores player health
# ══════════════════════════════════════════════════════════════════════════ #
class EnergyCellItem(Item):
    """
    Consumable that restores player health.

    When used, heals the player by ITEM_ENERGY_CELL_HEAL HP.
    Has no effect if the player is already at full health.
    """

    def __init__(self):
        """Create an Energy Cell item."""
        super().__init__(
            name='Energy Cell',                           # display name
            description=f'Restores {ITEM_ENERGY_CELL_HEAL} HP',  # tooltip
            icon_char='⚡',                               # HUD icon
            item_type='energy_cell',                      # type key
            stackable=True,                               # can stack
            max_stack=5,                                   # up to 5
        )

    def use(self, game_state, **context):
        """
        Heal the player.

        Returns:
            bool — True if healing was applied (player not full HP).
        """
        if game_state is None:
            return False   # safety guard

        # Check if player is already at full health
        from src.config import PLAYER_MAX_HEALTH   # avoid circular import
        if game_state.health >= PLAYER_MAX_HEALTH:
            return False   # no effect — already full

        # Apply healing via game_state helper
        game_state.heal(ITEM_ENERGY_CELL_HEAL)
        return True   # item consumed


# ══════════════════════════════════════════════════════════════════════════ #
#  Hack Booster — adds bonus time to the next hacking attempt
# ══════════════════════════════════════════════════════════════════════════ #
class HackBoosterItem(Item):
    """
    Consumable that buffs the next hack attempt.

    When used, sets a flag on game_state so the next HackingPanel
    receives extra seconds on its countdown timer.
    """

    def __init__(self):
        """Create a Hack Booster item."""
        super().__init__(
            name='Hack Booster',                                    # display name
            description=f'+{ITEM_HACK_BOOSTER_TIME:.0f}s hack time',  # tooltip
            icon_char='◈',                                          # HUD icon
            item_type='hack_booster',                               # type key
            stackable=True,                                         # can stack
            max_stack=3,                                             # up to 3
        )

    def use(self, game_state, **context):
        """
        Activate the hack boost flag.

        Returns:
            bool — True if the boost was set (not already active).
        """
        if game_state is None:
            return False   # safety guard

        # Don't waste if already active
        if getattr(game_state, 'hack_boost_active', False):
            return False   # already boosted — don't consume

        # Set the boost flag — consumed by the next hack
        game_state.hack_boost_active = True
        return True   # item consumed


# ══════════════════════════════════════════════════════════════════════════ #
#  EMP Pulse — disables nearby drones temporarily
# ══════════════════════════════════════════════════════════════════════════ #
class EMPPulseItem(Item):
    """
    Consumable that emits an electromagnetic pulse.

    When used, disables all security drones within EMP_RADIUS
    for EMP_DURATION seconds.  Requires an 'emp_callback' in context.
    """

    def __init__(self):
        """Create an EMP Pulse item."""
        super().__init__(
            name='EMP Pulse',                                       # display name
            description=f'Disables drones for {ITEM_EMP_DURATION:.0f}s',  # tooltip
            icon_char='◉',                                          # HUD icon
            item_type='emp_pulse',                                   # type key
            stackable=True,                                          # can stack
            max_stack=3,                                              # up to 3
        )

    def use(self, game_state, **context):
        """
        Trigger the EMP effect.

        Expects context['emp_callback'] = callable(player_pos, radius, duration)
        and context['player_pos'] = Vec3 of the player.

        Returns:
            bool — True if the EMP was fired.
        """
        # Retrieve the callback from context
        emp_cb     = context.get('emp_callback')
        player_pos = context.get('player_pos')

        if emp_cb is None or player_pos is None:
            return False   # missing references — can't fire

        # Fire the EMP — the callback handles drone iteration
        emp_cb(player_pos, ITEM_EMP_RADIUS, ITEM_EMP_DURATION)
        return True   # item consumed


# ══════════════════════════════════════════════════════════════════════════ #
#  Factory function — create item by type key
# ══════════════════════════════════════════════════════════════════════════ #
def create_item(item_type):
    """
    Create and return a new Item instance by its type key.

    Args:
        item_type : str — one of 'energy_cell', 'hack_booster', 'emp_pulse'

    Returns:
        Item — a new item instance, or None if the type is unknown.
    """
    # Mapping of type keys to item classes
    _ITEM_CLASSES = {
        'energy_cell':  EnergyCellItem,     # health restore
        'hack_booster': HackBoosterItem,    # hack time bonus
        'emp_pulse':    EMPPulseItem,        # disable drones
    }
    cls = _ITEM_CLASSES.get(item_type)   # look up class
    if cls is None:
        return None   # unknown type
    return cls()   # instantiate and return
