"""
game_state.py — Game State Tracking Module
=============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Tracks global game progress: which terminals have been
          breached, the player's access level, and aggregate stats.
          Any module can query or update the state through this class.

How it connects:
    • scenes.py creates a GameState when entering the game scene.
    • hacking.py calls breach_terminal() on a successful hack.
    • ui.py reads get_stats() to display breached node count.
    • environment.py reads is_breached() to colour terminals.

Why a separate file:
    Keeping game state isolated from rendering and input means
    future systems (missions, inventory, save/load) can all read
    and write the same state without circular dependencies.
"""


# ══════════════════════════════════════════════════════════════════════════ #
#  GameState class
# ══════════════════════════════════════════════════════════════════════════ #
class GameState:
    """
    Centralised tracker for all gameplay‑critical data.

    Attributes:
        total_terminals   : int  — how many terminals exist in the level
        breached_labels   : set  — labels of successfully hacked terminals
        access_level      : int  — current player access tier (starts at 1)

    Usage:
        gs = GameState(total_terminals=4)
        gs.breach_terminal("Access Node Alpha")
        stats = gs.get_stats()
    """

    def __init__(self, total_terminals=0):
        """
        Initialise the game state.

        Args:
            total_terminals : int — number of terminals in the level.
        """
        # Total number of hackable terminals placed in the environment
        self.total_terminals = total_terminals

        # Set of terminal labels that have been successfully breached
        self.breached_labels = set()

        # Player's current access level — increases with breaches
        self.access_level = 1

    # ------------------------------------------------------------------ #
    #  Breach a terminal
    # ------------------------------------------------------------------ #
    def breach_terminal(self, label):
        """
        Mark a terminal as breached and upgrade access level.

        Args:
            label : str — the unique label of the breached terminal.

        Returns:
            bool — True if this was a new breach, False if already done.
        """
        # If this terminal was already breached, no change
        if label in self.breached_labels:
            return False   # duplicate breach — no reward

        # Record the breach
        self.breached_labels.add(label)

        # Upgrade access level every 2 breaches (1 → 2 → 3 → …)
        self.access_level = 1 + len(self.breached_labels) // 2

        return True   # new breach — success

    # ------------------------------------------------------------------ #
    #  Check if a specific terminal is breached
    # ------------------------------------------------------------------ #
    def is_breached(self, label):
        """
        Check whether a terminal has already been hacked.

        Args:
            label : str — the terminal label to check.

        Returns:
            bool — True if breached, False otherwise.
        """
        return label in self.breached_labels

    # ------------------------------------------------------------------ #
    #  Get aggregate statistics
    # ------------------------------------------------------------------ #
    def get_stats(self):
        """
        Return a dictionary of current game stats for the HUD.

        Returns:
            dict with keys:
                'total'         — total terminal count
                'breached'      — number breached
                'access_level'  — current tier
                'labels'        — set of breached labels
        """
        return {
            'total':        self.total_terminals,
            'breached':     len(self.breached_labels),
            'access_level': self.access_level,
            'labels':       self.breached_labels.copy(),
        }

    # ------------------------------------------------------------------ #
    #  Cleanup (for symmetry with other modules)
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Reset all state. Called on scene exit."""
        self.breached_labels.clear()
        self.access_level = 1
        self.total_terminals = 0
