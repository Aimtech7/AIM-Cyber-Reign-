"""
scenes.py — Scene Manager Module (Phase 2)
=============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Central SceneManager that handles switching between:
            • Main Menu
            • Settings Menu  (new in Phase 2)
            • Game Scene      (now with interaction system)

Changes in Phase 2:
    • Added show_settings() / return to menu from settings
    • InteractionSystem created alongside environment + player
    • Environment receives the interaction system for terminal registration
    • HUD receives the player reference for sprint indicator

How it connects:
    main.py creates one SceneManager, calls show_menu(), and delegates
    all key presses via handle_input().

Key concepts:
    • Scene state is a dictionary of live object references.
    • Switching scenes destroys old objects and creates new ones.
    • mouse.locked is toggled for menus vs gameplay.
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


# ══════════════════════════════════════════════════════════════════════════ #
#  SceneManager class
# ══════════════════════════════════════════════════════════════════════════ #
class SceneManager:
    """
    Orchestrates scene transitions for the entire game.

    Scenes:
        • menu     — Main Menu  (title screen)
        • settings — Settings   (volume, sensitivity, quality)
        • game     — Gameplay   (3D world + player + HUD + interaction)

    Usage:
        sm = SceneManager()
        sm.show_menu()
        sm.start_game()
        sm.show_settings()
        sm.handle_input(key)
    """

    def __init__(self):
        """Initialise the scene state dictionary with empty slots."""
        self.state = {
            'menu':        None,   # MainMenu instance
            'settings':    None,   # SettingsMenu instance
            'environment': None,   # GameEnvironment instance
            'player':      None,   # PlayerController instance
            'hud':         None,   # HUD instance
            'interaction': None,   # InteractionSystem instance
        }

    # ------------------------------------------------------------------ #
    #  _destroy_keys — helper to tear down a list of state keys
    # ------------------------------------------------------------------ #
    def _destroy_keys(self, keys):
        """
        Destroy objects stored under the given state keys.

        Args:
            keys : iterable of str — keys into self.state
        """
        for key in keys:
            obj = self.state.get(key)
            if obj is not None:
                obj.destroy()
                self.state[key] = None

    # ================================================================== #
    #  MENU SCENE
    # ================================================================== #
    def show_menu(self):
        """
        Tear down any active scene and display the main menu.

        Destroys: game objects, settings, interaction system.
        Creates : MainMenu with Start / Settings / Exit callbacks.
        """
        # Destroy everything that might be active
        self._destroy_keys([
            'environment', 'player', 'hud', 'interaction', 'settings',
        ])

        # Unlock the mouse for menu buttons
        mouse.locked = False

        # Create the main menu with three callbacks
        self.state['menu'] = MainMenu(
            start_callback=self.start_game,
            settings_callback=self.show_settings,
            exit_callback=application.quit,
        )

    # ================================================================== #
    #  SETTINGS SCENE  (Phase 2)
    # ================================================================== #
    def show_settings(self):
        """
        Tear down the main menu and display the settings panel.

        Destroys: menu.
        Creates : SettingsMenu with a Back callback that returns to menu.
        """
        # Remove the main menu
        self._destroy_keys(['menu'])

        # Unlock mouse (should already be unlocked, but be explicit)
        mouse.locked = False

        # Create settings panel
        self.state['settings'] = SettingsMenu(
            back_callback=self.show_menu,    # "Back" returns to main menu
        )

    # ================================================================== #
    #  GAME SCENE
    # ================================================================== #
    def start_game(self):
        """
        Tear down menus and build the game world with interaction.

        Destroys: menu, settings.
        Creates : PlayerController, InteractionSystem, GameEnvironment,
                  HUD.
        """
        # Remove any active menus
        self._destroy_keys(['menu', 'settings'])

        # ── Create the player ────────────────────────────────────────── #
        self.state['player'] = PlayerController()

        # ── Create the interaction system ────────────────────────────── #
        # Needs a reference to the player so it can measure distance.
        self.state['interaction'] = InteractionSystem(
            player_ref=self.state['player'],
        )

        # ── Build the environment ────────────────────────────────────── #
        # Pass the interaction system so terminals get registered.
        self.state['environment'] = GameEnvironment(
            interaction_system=self.state['interaction'],
        )

        # ── Create the HUD ───────────────────────────────────────────── #
        # Pass the player so the HUD can show sprint state.
        self.state['hud'] = HUD(
            player_ref=self.state['player'],
        )

        # ── Lock mouse for first‑person controls ────────────────────── #
        mouse.locked = True

    # ================================================================== #
    #  INPUT HANDLER
    # ================================================================== #
    def handle_input(self, key):
        """
        Global input handler called by main.py's ``input()`` function.

        ESC — returns to menu from the game scene.

        Args:
            key : str — the key that was pressed.
        """
        if key == 'escape':
            # If we are in the game scene, go back to menu
            if self.state.get('player') is not None:
                self.show_menu()
