"""
scenes.py — Scene Manager Module (Phase 3)
=============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Central SceneManager that handles switching between:
            • Main Menu
            • Settings Menu
            • Game Scene (now with hacking flow)

Phase 3 changes:
    • Creates a GameState when entering the game scene.
    • Passes a ``hack_callback`` to the environment so terminals
      trigger the hacking panel.
    • Orchestrates hacking flow: freeze player → open panel → handle
      result → update terminal colour / game state → unfreeze player.
    • HUD receives both player ref and game_state ref.

How it connects:
    main.py creates one SceneManager, calls show_menu(), and delegates
    all key presses via handle_input().
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import mouse, application

# ── Project modules ────────────────────────────────────────────────────── #
from src.menu import MainMenu
from src.settings import SettingsMenu
from src.player import PlayerController
from src.environment import GameEnvironment
from src.ui import HUD
from src.interaction import InteractionSystem
from src.game_state import GameState
from src.hacking import HackingPanel


# ══════════════════════════════════════════════════════════════════════════ #
#  SceneManager class
# ══════════════════════════════════════════════════════════════════════════ #
class SceneManager:
    """
    Orchestrates scene transitions and the hacking gameplay flow.

    Scenes:
        • menu     — Main Menu
        • settings — Settings
        • game     — Gameplay (3D world + player + HUD + hacking)
    """

    def __init__(self):
        """Initialise scene state with empty slots."""
        self.state = {
            'menu':        None,   # MainMenu instance
            'settings':    None,   # SettingsMenu instance
            'environment': None,   # GameEnvironment instance
            'player':      None,   # PlayerController instance
            'hud':         None,   # HUD instance
            'interaction': None,   # InteractionSystem instance
            'game_state':  None,   # GameState instance
            'hacking':     None,   # HackingPanel instance (while hacking)
        }

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #
    def _destroy_keys(self, keys):
        """Destroy objects stored under the given state keys."""
        for key in keys:
            obj = self.state.get(key)
            if obj is not None:
                obj.destroy()
                self.state[key] = None

    # ================================================================== #
    #  MENU SCENE
    # ================================================================== #
    def show_menu(self):
        """Display the main menu — tear down everything else."""
        self._destroy_keys([
            'environment', 'player', 'hud', 'interaction', 'settings',
            'game_state', 'hacking',
        ])

        mouse.locked = False

        self.state['menu'] = MainMenu(
            start_callback=self.start_game,
            settings_callback=self.show_settings,
            exit_callback=application.quit,
        )

    # ================================================================== #
    #  SETTINGS SCENE
    # ================================================================== #
    def show_settings(self):
        """Display the settings panel."""
        self._destroy_keys(['menu'])
        mouse.locked = False

        self.state['settings'] = SettingsMenu(
            back_callback=self.show_menu,
        )

    # ================================================================== #
    #  GAME SCENE
    # ================================================================== #
    def start_game(self):
        """Build the game world with interaction + hacking support."""
        self._destroy_keys(['menu', 'settings'])

        # ── Game state ───────────────────────────────────────────────── #
        from src.config import TERMINAL_SPECS  # avoid circular at module level
        self.state['game_state'] = GameState(
            total_terminals=len(TERMINAL_SPECS),
        )

        # ── Player ───────────────────────────────────────────────────── #
        self.state['player'] = PlayerController()

        # ── Interaction system ───────────────────────────────────────── #
        self.state['interaction'] = InteractionSystem(
            player_ref=self.state['player'],
        )

        # ── Environment — pass hack callback ─────────────────────────── #
        self.state['environment'] = GameEnvironment(
            interaction_system=self.state['interaction'],
            hack_callback=self._on_terminal_hack,     # ← hacking entry point
        )

        # ── HUD — pass player ref AND game state ─────────────────────── #
        self.state['hud'] = HUD(
            player_ref=self.state['player'],
            game_state=self.state['game_state'],
        )

        # Lock mouse for FPS controls
        mouse.locked = True

    # ================================================================== #
    #  HACKING FLOW  (Phase 3)
    # ================================================================== #
    def _on_terminal_hack(self, label, security_level):
        """
        Called when the player presses E on a terminal.
        Opens the hacking panel and freezes the player.

        Args:
            label          : str — terminal label
            security_level : int — difficulty tier (1–3)
        """
        game_state = self.state.get('game_state')

        # If already breached, do nothing
        if game_state and game_state.is_breached(label):
            return

        # If a hacking panel is already open, do nothing
        if self.state.get('hacking') is not None:
            return

        # ── Freeze the player ────────────────────────────────────────── #
        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = False   # disable movement
        mouse.locked = False                     # unlock mouse for panel UI

        # ── Pause the interaction system ─────────────────────────────── #
        interaction = self.state.get('interaction')
        if interaction:
            interaction.paused = True

        # ── Set terminal to "active" colour while hacking ────────────── #
        env = self.state.get('environment')
        if env:
            env.set_terminal_color(label, 'active')

        # ── Open the hacking panel ───────────────────────────────────── #
        def on_hack_complete(success):
            """Callback from the hacking panel."""
            self._on_hack_result(label, success)

        self.state['hacking'] = HackingPanel(
            terminal_label=label,
            security_level=security_level,
            on_complete=on_hack_complete,
        )

    # ------------------------------------------------------------------ #
    #  Hacking result handler
    # ------------------------------------------------------------------ #
    def _on_hack_result(self, label, success):
        """
        Called when the hacking panel finishes (success or failure).

        Args:
            label   : str  — which terminal was hacked
            success : bool — True if the player completed the sequence
        """
        env        = self.state.get('environment')
        game_state = self.state.get('game_state')
        interaction = self.state.get('interaction')

        if success:
            # ── Mark as breached ─────────────────────────────────────── #
            if game_state:
                game_state.breach_terminal(label)

            # ── Update terminal appearance to "breached" ─────────────── #
            if env:
                env.set_terminal_color(label, 'breached')

            # ── Update the interactable prompt ───────────────────────── #
            if interaction and env:
                parts = env.terminal_parts.get(label)
                if parts:
                    interaction.update_prompt(
                        parts['base'],
                        new_prompt=f'{label} — BREACHED',
                        new_message=f'[ {label} — already breached ]',
                    )
        else:
            # ── Hack failed — revert terminal to locked ──────────────── #
            if env:
                env.set_terminal_color(label, 'locked')

        # ── Clean up the hacking panel reference ─────────────────────── #
        self.state['hacking'] = None

        # ── Unfreeze the player ──────────────────────────────────────── #
        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = True    # re‑enable movement
        mouse.locked = True                      # re‑lock mouse for FPS

        # ── Unpause interaction system ───────────────────────────────── #
        if interaction:
            interaction.paused = False

    # ================================================================== #
    #  INPUT HANDLER
    # ================================================================== #
    def handle_input(self, key):
        """
        Global input handler — ESC returns to menu (unless hacking).

        Args:
            key : str — the key that was pressed.
        """
        # Don't allow ESC to return to menu while hacking is active
        if self.state.get('hacking') is not None:
            return   # hacking panel handles its own ESC

        if key == 'escape':
            if self.state.get('player') is not None:
                self.show_menu()
