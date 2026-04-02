"""
inventory.py — Inventory, Equipment & Pickup Module
======================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Provides three classes:
            • Inventory       — stores items with stacking and a slot limit
            • EquipmentManager — two quick‑use slots (Q / R) with cooldowns
            • ItemPickup      — glowing 3D entity auto‑collected on proximity

How it connects:
    scenes.py creates Inventory + EquipmentManager on game start.
    environment.py spawns ItemPickup entities in the world.
    The _GameTicker checks proximity each frame for auto‑pickup.
    ui.py reads Inventory/EquipmentManager for the HUD display.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import math   # for pulsing glow effect on pickups

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Vec3,
    color,
    distance,
    destroy as ursina_destroy,
    time as ursina_time,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    INVENTORY_MAX_SLOTS,         # max items the player can carry
    EQUIPMENT_USE_COOLDOWN,      # seconds between item uses
    ITEM_PICKUP_COLOR,           # glow colour for pickup entities
)
from src.items import create_item   # factory to build Item instances


# ══════════════════════════════════════════════════════════════════════════ #
#  Inventory class
# ══════════════════════════════════════════════════════════════════════════ #
class Inventory:
    """
    Player inventory with stacking support and a slot limit.

    Each slot is a dict: {'item': Item, 'count': int}
    Stackable items share a slot; non‑stackable items take one slot each.

    Attributes:
        max_slots : int           — maximum number of slots
        slots     : list[dict]    — current inventory contents
    """

    def __init__(self, max_slots=INVENTORY_MAX_SLOTS):
        """
        Create an empty inventory.

        Args:
            max_slots : int — how many slots the player has.
        """
        self.max_slots = max_slots   # configurable capacity
        self.slots     = []           # start empty

    # ------------------------------------------------------------------ #
    def is_full(self):
        """Check if all slots are occupied (no room for a new item type)."""
        return len(self.slots) >= self.max_slots

    # ------------------------------------------------------------------ #
    def add_item(self, item):
        """
        Add an item to the inventory.  Stacks if possible.

        Args:
            item : Item — the item to add.

        Returns:
            bool — True if the item was added, False if inventory is full.
        """
        # Try stacking with an existing slot of the same type
        if item.stackable:
            for slot in self.slots:
                if (slot['item'].item_type == item.item_type
                        and slot['count'] < item.max_stack):
                    slot['count'] += 1   # increment stack
                    return True          # added successfully

        # No existing stack — need a new slot
        if self.is_full():
            return False   # inventory full — reject

        # Create a new slot for this item
        self.slots.append({'item': item, 'count': 1})
        return True   # added successfully

    # ------------------------------------------------------------------ #
    def remove_item(self, index):
        """
        Remove one item from a slot by index.

        Args:
            index : int — slot position (0‑based).

        Returns:
            Item or None — the removed item, or None if invalid.
        """
        if index < 0 or index >= len(self.slots):
            return None   # out of range

        slot = self.slots[index]
        item = slot['item']

        # Decrement count; remove the slot if empty
        slot['count'] -= 1
        if slot['count'] <= 0:
            self.slots.pop(index)   # slot is now empty — remove it

        return item   # return the consumed item

    # ------------------------------------------------------------------ #
    def use_item(self, index, game_state, **context):
        """
        Use an item at the given slot index.

        Calls the item's use() method; if successful, removes one
        from the stack.

        Args:
            index      : int       — slot position
            game_state : GameState — passed to item.use()
            **context  : dict      — extra refs (emp_callback etc.)

        Returns:
            bool — True if the item was used and consumed.
        """
        if index < 0 or index >= len(self.slots):
            return False   # invalid index

        slot = self.slots[index]
        item = slot['item']

        # Try to use the item
        success = item.use(game_state, **context)
        if success:
            self.remove_item(index)   # consume one from stack
        return success

    # ------------------------------------------------------------------ #
    def get_items(self):
        """
        Return a list of (item, count) tuples for display.

        Returns:
            list[tuple(Item, int)]
        """
        return [(s['item'], s['count']) for s in self.slots]

    # ------------------------------------------------------------------ #
    def find_index(self, item_type):
        """
        Find the slot index of an item by its type key.

        Args:
            item_type : str — e.g. 'energy_cell'

        Returns:
            int or -1 — slot index, or -1 if not found.
        """
        for i, slot in enumerate(self.slots):
            if slot['item'].item_type == item_type:
                return i   # found
        return -1   # not in inventory

    # ------------------------------------------------------------------ #
    def destroy(self):
        """Clear all slots."""
        self.slots.clear()


# ══════════════════════════════════════════════════════════════════════════ #
#  EquipmentManager class
# ══════════════════════════════════════════════════════════════════════════ #
class EquipmentManager:
    """
    Manages two quick‑use equipment slots mapped to keys Q and R.

    Each slot stores an item_type string referencing an inventory item.
    Using a slot triggers the item's effect with a cooldown.

    Attributes:
        slots     : dict — {'q': item_type or None, 'r': item_type or None}
        cooldowns : dict — {'q': float, 'r': float} — remaining cooldown
    """

    def __init__(self):
        """Create empty equipment slots with zero cooldown."""
        self.slots = {
            'q': None,   # first equip slot (Q key)
            'r': None,   # second equip slot (R key)
        }
        self.cooldowns = {
            'q': 0.0,    # no cooldown at start
            'r': 0.0,    # no cooldown at start
        }

    # ------------------------------------------------------------------ #
    def equip(self, slot_key, item_type):
        """
        Assign an item type to an equipment slot.

        Args:
            slot_key  : str — 'q' or 'r'
            item_type : str — e.g. 'energy_cell', or None to unequip
        """
        if slot_key in self.slots:
            self.slots[slot_key] = item_type   # set or clear the slot

    # ------------------------------------------------------------------ #
    def unequip(self, slot_key):
        """
        Remove the item from an equipment slot.

        Args:
            slot_key : str — 'q' or 'r'
        """
        if slot_key in self.slots:
            self.slots[slot_key] = None   # clear the slot

    # ------------------------------------------------------------------ #
    def use_slot(self, slot_key, inventory, game_state, **context):
        """
        Activate the item in the given equipment slot.

        Checks cooldown, finds the item in inventory, and uses it.

        Args:
            slot_key   : str       — 'q' or 'r'
            inventory  : Inventory — player's inventory
            game_state : GameState — for item effects
            **context  : dict      — extra refs

        Returns:
            str or None — feedback message, or None if nothing happened.
        """
        # Guard: invalid slot or nothing equipped
        if slot_key not in self.slots or self.slots[slot_key] is None:
            return None

        # Guard: still on cooldown
        if self.cooldowns[slot_key] > 0:
            return None   # cooldown active — ignore

        # Find the item in inventory
        item_type = self.slots[slot_key]
        idx = inventory.find_index(item_type)
        if idx < 0:
            # Item no longer in inventory — auto‑unequip
            self.slots[slot_key] = None
            return 'Item depleted — slot cleared'

        # Use the item
        success = inventory.use_item(idx, game_state, **context)
        if success:
            # Start cooldown
            self.cooldowns[slot_key] = EQUIPMENT_USE_COOLDOWN
            # Get the item name for feedback
            item_name = item_type.replace('_', ' ').title()

            # If the item stack is now empty, auto‑unequip
            if inventory.find_index(item_type) < 0:
                self.slots[slot_key] = None

            return f'Used {item_name}!'
        else:
            return 'Cannot use that now'

    # ------------------------------------------------------------------ #
    def update(self, dt):
        """
        Tick cooldown timers each frame.

        Args:
            dt : float — seconds since last frame.
        """
        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] = max(0.0, self.cooldowns[key] - dt)

    # ------------------------------------------------------------------ #
    def get_slot_info(self, slot_key):
        """
        Return display info for a slot.

        Args:
            slot_key : str — 'q' or 'r'

        Returns:
            dict — {item_type, cooldown, ready}
        """
        return {
            'item_type': self.slots.get(slot_key),           # what's equipped
            'cooldown':  self.cooldowns.get(slot_key, 0.0),  # remaining cd
            'ready':     self.cooldowns.get(slot_key, 0.0) <= 0,  # usable?
        }

    # ------------------------------------------------------------------ #
    def destroy(self):
        """Reset equipment slots."""
        self.slots     = {'q': None, 'r': None}
        self.cooldowns = {'q': 0.0, 'r': 0.0}


# ══════════════════════════════════════════════════════════════════════════ #
#  ItemPickup — world entity for auto‑collection
# ══════════════════════════════════════════════════════════════════════════ #
class ItemPickup(Entity):
    """
    A glowing 3D cube in the world that the player auto‑collects
    when they walk within ITEM_PICKUP_DISTANCE.

    Attributes:
        item_type   : str     — type key (e.g. 'energy_cell')
        glow_ring   : Entity  — decorative glow underneath
        collected   : bool    — True once picked up (pending destroy)
        _bob_phase  : float   — for vertical bob animation
    """

    def __init__(self, position, item_type):
        """
        Spawn an item pickup in the world.

        Args:
            position  : tuple(x, z) — world coordinates (placed at y=0.5)
            item_type : str         — which item this pickup gives
        """
        x, z = position   # unpack spawn coordinates

        # Main pickup body — small glowing cube
        super().__init__(
            model='cube',
            scale=(0.4, 0.4, 0.4),          # small cube
            position=Vec3(x, 0.8, z),        # floating above ground
            color=color.rgb(*ITEM_PICKUP_COLOR),  # bright orange
            unlit=True,                      # always bright
        )

        # Store the item type
        self.item_type = item_type   # e.g. 'energy_cell'
        self.collected = False       # not yet picked up

        # ── Glow ring underneath ─────────────────────────────────────── #
        self.glow_ring = Entity(
            parent=self,                     # child of pickup body
            model='cube',
            scale=(2.0, 0.1, 2.0),          # flat wide ring
            position=(0, -0.5, 0),           # below the cube
            color=color.rgba(*ITEM_PICKUP_COLOR, 100),  # semi‑transparent
            unlit=True,
        )

        # ── Label text above the pickup ──────────────────────────────── #
        # Create a friendly name from the type key
        display_name = item_type.replace('_', ' ').upper()
        self.label = Entity(
            parent=self,
            model='quad',
            scale=(0, 0, 0),   # invisible quad (just for Text child)
        )

        # Bob animation phase (random offset so pickups aren't in sync)
        import random
        self._bob_phase = random.uniform(0, math.pi * 2)
        self._base_y    = 0.8   # nominal hover height

    # ------------------------------------------------------------------ #
    def update(self):
        """Gentle vertical bob and rotation animation."""
        if self.collected:
            return   # stop animating once collected

        dt = ursina_time.dt

        # Vertical bob
        self._bob_phase += 2.0 * dt   # bob speed
        self.y = self._base_y + math.sin(self._bob_phase) * 0.15

        # Slow rotation
        self.rotation_y += 60 * dt   # 60 degrees per second

    # ------------------------------------------------------------------ #
    def collect(self):
        """Mark as collected and hide (cleanup done by scene manager)."""
        self.collected = True
        self.visible  = False         # hide immediately
        if self.glow_ring:
            self.glow_ring.visible = False

    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove pickup and children from the scene."""
        try:
            ursina_destroy(self.glow_ring)
        except Exception:
            pass
        try:
            ursina_destroy(self.label)
        except Exception:
            pass
        self.glow_ring = None
        self.label     = None
        super().destroy()
