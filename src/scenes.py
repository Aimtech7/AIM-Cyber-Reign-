"""
scenes.py — Scene Manager Module (Phase 5)
=============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Central SceneManager handling:
            • Menu / Settings / Game scenes
            • Hacking flow orchestration
            • Security drone spawning
            • Mission system & win/lose/restart (Phase 5)
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    mouse, application, Entity, Text,
    time as ursina_time, color, camera,
    destroy as ursina_destroy,
)

# ── Project modules ────────────────────────────────────────────────────── #
from src.menu import MainMenu
from src.settings import SettingsMenu
from src.player import PlayerController
from src.environment import GameEnvironment
from src.ui import HUD
from src.interaction import InteractionSystem
from src.game_state import GameState
from src.hacking import HackingPanel
from src.enemies import SecurityDrone
from src.missions import MissionManager, create_sector_breach_mission
from src.config import (
    DRONE_SPECS, TERMINAL_SPECS,
    NEON_CYAN, NEON_MAGENTA, NEON_GREEN,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  _GameTicker — per‑frame game logic driver
# ══════════════════════════════════════════════════════════════════════════ #
class _GameTicker(Entity):
    """Invisible Entity that ticks health, alert, and mission checks."""

    def __init__(self, game_state, mission_manager, scene_manager):
        super().__init__()
        self.game_state      = game_state
        self.mission_manager = mission_manager
        self.scene_manager   = scene_manager

    def update(self):
        if self.game_state is None:
            return
        dt = ursina_time.dt
        self.game_state.update_health(dt)
        self.game_state.update_alert(dt)

        # Update mission message timer
        if self.mission_manager:
            self.mission_manager.update_timer(dt)

        # Check mission failure (player dead)
        if self.mission_manager and self.mission_manager.check_failure(self.game_state):
            # Mission just failed — show result overlay
            self.scene_manager._show_end_screen(False)


# ══════════════════════════════════════════════════════════════════════════ #
#  SceneManager class
# ══════════════════════════════════════════════════════════════════════════ #
class SceneManager:
    """Orchestrates scenes, hacking, drones, and missions."""

    def __init__(self):
        self.state = {
            'menu':        None,
            'settings':    None,
            'environment': None,
            'player':      None,
            'hud':         None,
            'interaction': None,
            'game_state':  None,
            'hacking':     None,
            'ticker':      None,
            'drones':      [],
            'mission_mgr': None,     # Phase 5
            'end_screen':  [],       # Phase 5 — end overlay elements
        }

    def _destroy_keys(self, keys):
        for key in keys:
            obj = self.state.get(key)
            if obj is None:
                continue
            if isinstance(obj, list):
                for item in obj:
                    try:
                        item.destroy()
                    except Exception:
                        pass
                self.state[key] = []
            else:
                try:
                    obj.destroy()
                except Exception:
                    pass
                self.state[key] = None

    # ================================================================== #
    #  MENU
    # ================================================================== #
    def show_menu(self):
        self._destroy_keys([
            'environment', 'player', 'hud', 'interaction', 'settings',
            'game_state', 'hacking', 'ticker', 'drones', 'mission_mgr',
            'end_screen',
        ])
        mouse.locked = False
        self.state['menu'] = MainMenu(
            start_callback=self.start_game,
            settings_callback=self.show_settings,
            exit_callback=application.quit,
        )

    def show_settings(self):
        self._destroy_keys(['menu'])
        mouse.locked = False
        self.state['settings'] = SettingsMenu(back_callback=self.show_menu)

    # ================================================================== #
    #  GAME
    # ================================================================== #
    def start_game(self):
        self._destroy_keys(['menu', 'settings', 'end_screen'])

        # Game state
        self.state['game_state'] = GameState(total_terminals=len(TERMINAL_SPECS))

        # Mission manager (Phase 5)
        mm = MissionManager()
        mm.load_mission(create_sector_breach_mission())
        self.state['mission_mgr'] = mm

        # Player
        self.state['player'] = PlayerController()

        # Interaction
        self.state['interaction'] = InteractionSystem(
            player_ref=self.state['player'],
        )

        # Environment — with extraction callback
        self.state['environment'] = GameEnvironment(
            interaction_system=self.state['interaction'],
            hack_callback=self._on_terminal_hack,
            extraction_callback=self._on_extraction,
        )

        # Drones
        drones = []
        for spawn in DRONE_SPECS:
            drones.append(SecurityDrone(
                spawn_pos=spawn,
                player_ref=self.state['player'],
                game_state=self.state['game_state'],
            ))
        self.state['drones'] = drones

        # Ticker
        self.state['ticker'] = _GameTicker(
            self.state['game_state'],
            self.state['mission_mgr'],
            self,
        )

        # HUD
        self.state['hud'] = HUD(
            player_ref=self.state['player'],
            game_state=self.state['game_state'],
            mission_manager=self.state['mission_mgr'],
        )

        mouse.locked = True

    # ================================================================== #
    #  HACKING FLOW
    # ================================================================== #
    def _on_terminal_hack(self, label, security_level):
        gs = self.state.get('game_state')
        if gs and gs.is_breached(label):
            return
        if self.state.get('hacking') is not None:
            return

        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = False
        mouse.locked = False

        interaction = self.state.get('interaction')
        if interaction:
            interaction.paused = True

        env = self.state.get('environment')
        if env:
            env.set_terminal_color(label, 'active')

        self._hack_security = security_level

        def on_complete(success):
            self._on_hack_result(label, success)

        self.state['hacking'] = HackingPanel(
            terminal_label=label,
            security_level=security_level,
            on_complete=on_complete,
        )

    def _on_hack_result(self, label, success):
        env         = self.state.get('environment')
        gs          = self.state.get('game_state')
        interaction = self.state.get('interaction')
        mm          = self.state.get('mission_mgr')
        sec_level   = getattr(self, '_hack_security', 1)

        # Alert from hacking
        if gs:
            gs.alert_from_hack(success, sec_level)

        if success:
            if gs:
                gs.breach_terminal(label)
            if env:
                env.set_terminal_color(label, 'breached')
            if interaction and env:
                parts = env.terminal_parts.get(label)
                if parts:
                    interaction.update_prompt(
                        parts['base'],
                        new_prompt=f'{label} — BREACHED',
                        new_message=f'[ {label} — already breached ]',
                    )
            # Notify mission manager (Phase 5)
            if mm:
                mm.on_terminal_breached(label)
        else:
            if env:
                env.set_terminal_color(label, 'locked')

        self.state['hacking'] = None
        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = True
        mouse.locked = True
        if interaction:
            interaction.paused = False

    # ================================================================== #
    #  EXTRACTION (Phase 5)
    # ================================================================== #
    def _on_extraction(self):
        """Called when the player presses E while in the extraction zone."""
        mm = self.state.get('mission_mgr')
        if mm is None:
            return

        result = mm.check_extraction()
        if result == 'complete':
            self._show_end_screen(True)

    # ================================================================== #
    #  END SCREEN — win / lose overlay (Phase 5)
    # ================================================================== #
    def _show_end_screen(self, victory):
        """
        Display a full‑screen result overlay.
        Press R to restart or ESC for menu.
        """
        # Freeze player and drones
        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = False
        mouse.locked = False

        # Disable interaction
        interaction = self.state.get('interaction')
        if interaction:
            interaction.paused = True

        # Overlay elements
        elements = []

        # Dark backdrop
        bg = Entity(parent=camera.ui, model='quad', scale=(2, 1),
                     color=color.rgba(5, 3, 15, 200), z=0.5)
        elements.append(bg)

        # Result text
        if victory:
            result_text = '[ MISSION COMPLETE ]'
            result_clr  = color.rgb(*NEON_GREEN)
        else:
            result_text = '[ MISSION FAILED ]'
            result_clr  = color.rgb(*NEON_MAGENTA)

        title = Text(text=result_text, parent=camera.ui,
                     position=(0, 0.1), origin=(0, 0),
                     scale=3.0, color=result_clr, font='VeraMono.ttf')
        elements.append(title)

        # Instructions
        hint = Text(text='Press R to Restart  |  ESC for Menu',
                    parent=camera.ui, position=(0, -0.05), origin=(0, 0),
                    scale=1.2, color=color.rgb(*NEON_CYAN), font='VeraMono.ttf')
        elements.append(hint)

        self.state['end_screen'] = elements

    def _clear_end_screen(self):
        """Remove end screen overlay elements."""
        for e in self.state.get('end_screen', []):
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.state['end_screen'] = []

    # ================================================================== #
    #  INPUT
    # ================================================================== #
    def handle_input(self, key):
        # Hacking panel has its own input
        if self.state.get('hacking') is not None:
            return

        # End screen controls
        if self.state.get('end_screen'):
            if key == 'r':
                self._clear_end_screen()
                self.start_game()       # restart the mission
            elif key == 'escape':
                self._clear_end_screen()
                self.show_menu()
            return

        if key == 'escape':
            if self.state.get('player') is not None:
                self.show_menu()
