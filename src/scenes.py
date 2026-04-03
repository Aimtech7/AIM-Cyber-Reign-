"""
scenes.py — Scene Manager Module (Phase 8)
=============================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Central SceneManager handling:
            • Menu / Settings / Game scenes
            • Hacking flow orchestration
            • Security drone spawning
            • Mission system & win/lose/restart (Phase 5)
            • Inventory, equipment, pickups, EMP (Phase 6)
            • Audio management — music + SFX (Phase 7)
            • Save/load system, camera shake, auto-save (Phase 8)
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    mouse, application, Entity, Text,
    time as ursina_time, color, camera, distance,
    destroy as ursina_destroy, held_keys,
)

# ── Project modules ────────────────────────────────────────────────────── #
from src.menu import MainMenu, HowToPlayMenu
from src.settings import SettingsMenu
from src.player import PlayerController
from src.environment import GameEnvironment
from src.ui import HUD
from src.interaction import InteractionSystem
from src.game_state import GameState
from src.hacking import HackingPanel
from src.enemies import SecurityDrone
from src.missions import MissionManager, create_sector_breach_mission
from src.inventory import Inventory, EquipmentManager   # Phase 6
from src.items import create_item                         # Phase 6
from src.audio import AudioManager                        # Phase 7
from src.effects import CameraFX, ParticleEmitter          # Phase 8
from src.save_system import (                              # Phase 8
    save_game, load_game, save_exists,
    apply_save_data, delete_save,
)
from src.config import (
    DRONE_SPECS, TERMINAL_SPECS,
    NEON_CYAN, NEON_MAGENTA, NEON_GREEN, NEON_YELLOW,
    MENU_BG,
    ITEM_PICKUP_DISTANCE,          # Phase 6 — auto‑pickup range
    ITEM_HACK_BOOSTER_TIME,        # Phase 6 — hack boost seconds
    INVENTORY_TOGGLE_KEY,          # Phase 6 — TAB key
    EQUIP_SLOT_Q, EQUIP_SLOT_R,    # Phase 6 — Q / R keys
    # Phase 7 — audio constants
    MUSIC_MENU_LOOP, MUSIC_CYBER_AMBIENT, MUSIC_TENSE_LOOP,
    SFX_TERMINAL_ON, SFX_HACK_SUCCESS, SFX_HACK_FAIL,
    SFX_PICKUP, SFX_EXTRACT, SFX_MISSION_COMPLETE, SFX_MISSION_FAIL,
    SFX_DRONE_DISABLED, SFX_CLICK, SFX_INVENTORY_TOGGLE,
    # Phase 8 — camera shake + save SFX
    CAMERA_SHAKE_EMP_INTENSITY, CAMERA_SHAKE_EMP_DURATION,
    CAMERA_SHAKE_DAMAGE_INTENSITY, CAMERA_SHAKE_DAMAGE_DURATION,
    SFX_DAMAGE_HIT, SFX_SAVE_GAME, SFX_LOAD_GAME,
    # Phase 8 — particle colours
    PARTICLE_EMP_COUNT,
    HUD_SECONDARY,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  _GameTicker — per‑frame game logic driver
# ══════════════════════════════════════════════════════════════════════════ #
class _GameTicker(Entity):
    """Invisible Entity that ticks health, alert, mission, pickups, equip."""

    def __init__(self, game_state, mission_manager, scene_manager,
                 equipment_manager=None):
        """
        Create the ticker.

        Args:
            game_state        : GameState
            mission_manager   : MissionManager
            scene_manager     : SceneManager
            equipment_manager : EquipmentManager (Phase 6)
        """
        super().__init__()
        self.game_state        = game_state
        self.mission_manager   = mission_manager
        self.scene_manager     = scene_manager
        self.equipment_manager = equipment_manager   # Phase 6

    def update(self):
        """Per‑frame updates for all game systems."""
        if self.game_state is None:
            return
        dt = ursina_time.dt

        # Health and alert decay
        self.game_state.update_health(dt)
        self.game_state.update_alert(dt)

        # Mission message timer
        if self.mission_manager:
            self.mission_manager.update_timer(dt)

        # Equipment cooldown timers (Phase 6)
        if self.equipment_manager:
            self.equipment_manager.update(dt)

        # Check mission failure (player dead)
        if self.mission_manager and self.mission_manager.check_failure(self.game_state):
            self.scene_manager._show_end_screen(False)

        # Auto‑pickup items (Phase 6)
        self.scene_manager._check_item_pickups()


# ══════════════════════════════════════════════════════════════════════════ #
#  SceneManager class
# ══════════════════════════════════════════════════════════════════════════ #
class SceneManager:
    """Orchestrates scenes, hacking, drones, missions, and inventory."""

    def __init__(self):
        """Initialise scene state dictionary."""
        # Phase 7 — create audio manager once (persists across scenes)
        self.audio = AudioManager()

        self.state = {
            'menu':        None,
            'settings':    None,
            'how_to_play': None,
            'environment': None,
            'player':      None,
            'hud':         None,
            'interaction': None,
            'game_state':  None,
            'hacking':     None,
            'ticker':      None,
            'drones':      [],
            'mission_mgr': None,       # Phase 5
            'end_screen':  [],         # Phase 5 — end overlay elements
            'inventory':   None,       # Phase 6 — Inventory instance
            'equip_mgr':   None,       # Phase 6 — EquipmentManager instance
            'tutorial':    [],         # Tutorial overlay elements
        }

    def _destroy_keys(self, keys):
        """Destroy one or more state entries by key."""
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
        """Show the main menu, destroying any active game."""
        self._destroy_keys([
            'environment', 'player', 'hud', 'interaction', 'settings', 'how_to_play',
            'game_state', 'hacking', 'ticker', 'drones', 'mission_mgr',
            'end_screen', 'inventory', 'equip_mgr', 'tutorial',
        ])
        mouse.locked = False
        # Phase 7 — play menu music
        self.audio.play_music(MUSIC_MENU_LOOP)
        self.state['menu'] = MainMenu(
            start_callback=self.start_game,
            settings_callback=self.show_settings,
            how_to_play_callback=self.show_how_to_play,
            exit_callback=application.quit,
            audio_manager=self.audio,            # Phase 7 — pass audio
            continue_callback=self.continue_game, # Phase 8 — pass continue
        )

    def show_settings(self):
        """Show the settings panel."""
        self._destroy_keys(['menu'])
        mouse.locked = False
        self.state['settings'] = SettingsMenu(
            back_callback=self.show_menu,
            audio_manager=self.audio,   # Phase 7 — pass audio
        )

    def show_how_to_play(self):
        """Show the How To Play panel."""
        self._destroy_keys(['menu'])
        mouse.locked = False
        self.state['how_to_play'] = HowToPlayMenu(
            back_callback=self.show_menu,
            audio_manager=self.audio,
        )

    # ================================================================== #
    #  GAME
    # ================================================================== #
    def start_game(self):
        """Set up and launch a full game session."""
        self._destroy_keys(['menu', 'settings', 'end_screen'])

        # Game state
        self.state['game_state'] = GameState(total_terminals=len(TERMINAL_SPECS))

        # Mission manager (Phase 5)
        mm = MissionManager()
        mm.load_mission(create_sector_breach_mission())
        self.state['mission_mgr'] = mm

        # Inventory and equipment (Phase 6)
        self.state['inventory'] = Inventory()
        self.state['equip_mgr'] = EquipmentManager()

        # Phase 7 — switch to in‑game ambient music
        self.audio.play_music(MUSIC_CYBER_AMBIENT)

        # Player (Phase 7 — pass audio for footsteps / jump)
        self.state['player'] = PlayerController(audio_manager=self.audio)

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

        # Drones (Phase 7 — pass audio for state sounds)
        drones = []
        for spawn in DRONE_SPECS:
            drones.append(SecurityDrone(
                spawn_pos=spawn,
                player_ref=self.state['player'],
                game_state=self.state['game_state'],
                audio_manager=self.audio,   # Phase 7
            ))
        self.state['drones'] = drones

        # Ticker — includes equipment manager (Phase 6)
        self.state['ticker'] = _GameTicker(
            self.state['game_state'],
            self.state['mission_mgr'],
            self,
            equipment_manager=self.state['equip_mgr'],   # Phase 6
        )

        # HUD — includes inventory and equipment refs (Phase 6)
        self.state['hud'] = HUD(
            player_ref=self.state['player'],
            game_state=self.state['game_state'],
            mission_manager=self.state['mission_mgr'],
            inventory=self.state['inventory'],              # Phase 6
            equipment_manager=self.state['equip_mgr'],     # Phase 6
        )

        mouse.locked = True

        # Show tutorial/controls overlay on first game start
        self._show_tutorial()

    # ================================================================== #
    #  ITEM PICKUP  (Phase 6)
    # ================================================================== #
    def _check_item_pickups(self):
        """
        Called each frame by _GameTicker.
        Auto‑collects nearby item pickups into the player's inventory.
        """
        env       = self.state.get('environment')
        player    = self.state.get('player')
        inventory = self.state.get('inventory')
        hud       = self.state.get('hud')

        if env is None or player is None or inventory is None:
            return   # nothing to check
        if player.controller is None:
            return   # player not initialised

        player_pos = player.controller.position

        # Check each pickup entity
        for pickup in list(env.item_pickups):
            if pickup.collected:
                continue   # already picked up

            dist = distance(player_pos, pickup.position)
            if dist < ITEM_PICKUP_DISTANCE:
                # Create the item from the pickup type
                item = create_item(pickup.item_type)
                if item is None:
                    continue   # unknown type — skip

                # Try to add to inventory
                added = inventory.add_item(item)
                if added:
                    pickup.collect()   # hide the pickup entity
                    # Phase 7 — pickup sound
                    self.audio.play_sfx(SFX_PICKUP)
                    # Show HUD feedback
                    if hud:
                        hud.show_item_message(
                            f'PICKED UP: {item.icon_char} {item.name}'
                        )

    # ================================================================== #
    #  EMP CALLBACK  (Phase 6)
    # ================================================================== #
    def _on_emp_fired(self, player_pos, radius, duration):
        """
        Disable all drones within radius of the player.

        Called by EMPPulseItem.use() via context['emp_callback'].

        Args:
            player_pos : Vec3  — player's world position
            radius     : float — effect radius
            duration   : float — disable duration (seconds)
        """
        for drone in self.state.get('drones', []):
            dist = distance(player_pos, drone.position)
            if dist <= radius:
                drone.apply_emp(duration)   # freeze the drone
        # Phase 7 — EMP sound effect
        self.audio.play_sfx(SFX_DRONE_DISABLED)
        # Phase 8 — camera shake on EMP blast
        CameraFX.trigger_shake(
            CAMERA_SHAKE_EMP_INTENSITY,
            CAMERA_SHAKE_EMP_DURATION,
        )
        # Phase 8 — EMP particle burst
        if player_pos:
            ParticleEmitter(
                position=player_pos,
                count=PARTICLE_EMP_COUNT,
                particle_color=NEON_CYAN,
                speed=5.0,
                direction='outward',
            )

    # ================================================================== #
    #  HACKING FLOW
    # ================================================================== #
    def _on_terminal_hack(self, label, security_level):
        """Start a hacking session when the player interacts with a terminal."""
        gs = self.state.get('game_state')
        if gs and gs.is_breached(label):
            return   # already hacked
        if self.state.get('hacking') is not None:
            return   # already hacking

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
        # Phase 7 — terminal activation sound
        self.audio.play_sfx(SFX_TERMINAL_ON)
        # Phase 7 — switch to tense music during hacking
        self.audio.play_music(MUSIC_TENSE_LOOP)

        self._hack_security = security_level

        # Phase 6 — check for hack boost
        time_bonus = 0.0
        if gs and getattr(gs, 'hack_boost_active', False):
            time_bonus = ITEM_HACK_BOOSTER_TIME
            gs.hack_boost_active = False   # consume the boost

        def on_complete(success):
            self._on_hack_result(label, success)

        self.state['hacking'] = HackingPanel(
            terminal_label=label,
            security_level=security_level,
            on_complete=on_complete,
            time_bonus=time_bonus,       # Phase 6 — pass the bonus
            audio_manager=self.audio,    # Phase 7 — pass audio
        )

    def _on_hack_result(self, label, success):
        """Handle the result of a hacking attempt."""
        env         = self.state.get('environment')
        gs          = self.state.get('game_state')
        interaction = self.state.get('interaction')
        mm          = self.state.get('mission_mgr')
        sec_level   = getattr(self, '_hack_security', 1)

        # Alert from hacking
        if gs:
            gs.alert_from_hack(success, sec_level)

        if success:
            # Phase 7 — hack success sound
            self.audio.play_sfx(SFX_HACK_SUCCESS)
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
            # Phase 8 — auto-save after successful breach
            self._auto_save()
        else:
            # Phase 7 — hack fail sound
            self.audio.play_sfx(SFX_HACK_FAIL)
            if env:
                env.set_terminal_color(label, 'locked')

        self.state['hacking'] = None
        # Phase 7 — restore ambient music after hacking
        self.audio.play_music(MUSIC_CYBER_AMBIENT)
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
            # Phase 7 — extraction success sound
            self.audio.play_sfx(SFX_EXTRACT)
            # Phase 8 — auto-save before showing end screen
            self._auto_save()
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
        bg = Entity(parent=camera.ui, model='quad', scale=(3, 3),
                     color=color.rgba(5, 3, 15, 200), z=0.5)
        elements.append(bg)

        # Phase 7 — mission result sound
        if victory:
            self.audio.play_sfx(SFX_MISSION_COMPLETE)
        else:
            self.audio.play_sfx(SFX_MISSION_FAIL)
        # Phase 7 — stop game music on end screen
        self.audio.stop_music()

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
    #  EQUIP ITEM  (Phase 6)
    # ================================================================== #
    def _equip_item_to_slot(self, slot_key, slot_index):
        """
        Equip an inventory item to a quick‑use slot.

        Args:
            slot_key   : str — 'q' or 'r'
            slot_index : int — inventory index (0‑based)
        """
        inventory = self.state.get('inventory')
        equip_mgr = self.state.get('equip_mgr')
        hud       = self.state.get('hud')

        if inventory is None or equip_mgr is None:
            return

        items = inventory.get_items()
        if slot_index < 0 or slot_index >= len(items):
            return   # out of range

        item, _count = items[slot_index]
        equip_mgr.equip(slot_key, item.item_type)

        if hud:
            hud.show_item_message(f'Equipped {item.name} to [{slot_key.upper()}]')

    # ================================================================== #
    #  USE EQUIPPED ITEM  (Phase 6)
    # ================================================================== #
    def _use_equipped_item(self, slot_key):
        """
        Use the item in the given equipment slot.

        Args:
            slot_key : str — 'q' or 'r'
        """
        inventory = self.state.get('inventory')
        equip_mgr = self.state.get('equip_mgr')
        gs        = self.state.get('game_state')
        player    = self.state.get('player')
        hud       = self.state.get('hud')

        if inventory is None or equip_mgr is None or gs is None:
            return

        # Build context for item use
        context = {
            'emp_callback': self._on_emp_fired,   # for EMP Pulse
            'player_pos': (player.controller.position
                           if player and player.controller else None),
        }

        msg = equip_mgr.use_slot(slot_key, inventory, gs, **context)
        if msg and hud:
            hud.show_item_message(msg)

    # ================================================================== #
    #  SAVE / LOAD  (Phase 8)
    # ================================================================== #
    def _auto_save(self):
        """
        Auto-save current game state to disk.
        Called after terminal breach and extraction success.
        """
        gs        = self.state.get('game_state')
        player    = self.state.get('player')
        inventory = self.state.get('inventory')
        mm        = self.state.get('mission_mgr')

        success = save_game(gs, player, inventory, mm)
        if success:
            self.audio.play_sfx(SFX_SAVE_GAME)
            hud = self.state.get('hud')
            if hud:
                hud.show_item_message('[ GAME SAVED ]', duration=1.5)

    def continue_game(self):
        """
        Load save data, start a fresh game, then apply saved state.
        Called from the menu when "Continue" is selected.
        """
        data = load_game()
        if data is None:
            return   # no save to load — do nothing

        # Start a normal game session first
        self.start_game()

        # Then overlay saved state
        gs        = self.state.get('game_state')
        player    = self.state.get('player')
        inventory = self.state.get('inventory')
        mm        = self.state.get('mission_mgr')
        env       = self.state.get('environment')

        apply_save_data(data, gs, player, inventory, mm)

        # Update terminal visuals for breached nodes
        if env and gs:
            for label in gs.breached_terminals:
                env.set_terminal_color(label, 'breached')

        self.audio.play_sfx(SFX_LOAD_GAME)

    # ================================================================== #
    #  INPUT
    # ================================================================== #
    def handle_input(self, key):
        """Global input handler — delegates to active scene."""
        # Hacking panel has its own input
        if self.state.get('hacking') is not None:
            return

        # Tutorial overlay — any key press dismisses it
        if self.state.get('tutorial'):
            self._dismiss_tutorial()
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

        # ── Phase 6: Inventory toggle ────────────────────────────────── #
        hud = self.state.get('hud')
        if key == INVENTORY_TOGGLE_KEY and hud and self.state.get('player'):
            # Phase 7 — inventory toggle sound
            self.audio.play_sfx(SFX_INVENTORY_TOGGLE)
            hud.toggle_inventory_panel()
            # Lock/unlock mouse based on panel state
            if hud.inventory_open:
                player = self.state.get('player')
                if player and player.controller:
                    player.controller.enabled = False
                mouse.locked = False
            else:
                player = self.state.get('player')
                if player and player.controller:
                    player.controller.enabled = True
                mouse.locked = True
            return

        # ── Phase 6: Equip items from inventory panel ────────────────── #
        if hud and hud.inventory_open:
            # Number keys 1-8 equip to Q slot
            # Shift + number keys equip to R slot
            for i in range(1, 9):
                if key == str(i):
                    self._equip_item_to_slot('q', i - 1)
                    hud._close_inventory_panel()
                    hud._open_inventory_panel()   # refresh display
                    return
            # Shift‑number isn't sent as separate keys in Ursina,
            # so we use shift+number detection differently:
            # When inventory is open, pressing a letter key equips to R
            return   # absorb all keys while inventory is open

        # ── Phase 6: Use equipped items (Q / R) ─────────────────────── #
        if self.state.get('player') is not None:
            if key == EQUIP_SLOT_Q:
                self._use_equipped_item('q')
                return
            # R key — only for equipment when not on end screen
            if key == EQUIP_SLOT_R:
                self._use_equipped_item('r')
                return

        if key == 'escape':
            if self.state.get('player') is not None:
                self.show_menu()

    # ================================================================== #
    #  TUTORIAL OVERLAY
    # ================================================================== #
    def _show_tutorial(self):
        """
        Display a tutorial/controls overlay when game starts.
        Dismissed by pressing any key or clicking.
        """
        # Pause the player while tutorial is showing
        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = False
        mouse.locked = False

        elements = []

        # Semi-transparent backdrop
        bg = Entity(parent=camera.ui, model='quad', scale=(3, 3),
                     color=color.rgba(*MENU_BG, 230), z=0.2)
        elements.append(bg)

        # Title
        title = Text(text='[ MISSION BRIEFING ]', parent=camera.ui,
                      position=(0, 0.38), origin=(0, 0),
                      scale=2.5, color=color.rgb(*NEON_CYAN),
                      font='VeraMono.ttf')
        elements.append(title)

        # Separator
        sep = Entity(parent=camera.ui, model='quad',
                      scale=(0.6, 0.002), position=(0, 0.33),
                      color=color.rgb(*NEON_CYAN), z=0)
        elements.append(sep)

        # Objective summary
        obj_text = Text(
            text='OBJECTIVE: Hack target terminals and reach\n'
                 'the extraction zone to complete the mission.',
            parent=camera.ui, position=(0, 0.27), origin=(0, 0),
            scale=1.1, color=color.rgb(*NEON_YELLOW),
            font='VeraMono.ttf',
        )
        elements.append(obj_text)

        # Controls section
        controls = [
            ('MOVEMENT',      'W A S D'),
            ('LOOK',          'Mouse'),
            ('SPRINT',        'Hold Left Shift'),
            ('JUMP',          'Space'),
            ('INTERACT/HACK', 'E  (near terminals)'),
            ('INVENTORY',     'TAB'),
            ('USE ITEM Q',    'Q'),
            ('USE ITEM R',    'R'),
            ('BACK TO MENU',  'ESC'),
        ]

        # Controls header
        ctrl_header = Text(
            text='─── CONTROLS ───', parent=camera.ui,
            position=(0, 0.17), origin=(0, 0),
            scale=1.2, color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        elements.append(ctrl_header)

        y_start = 0.12
        for i, (action, key_bind) in enumerate(controls):
            y = y_start - i * 0.04
            # Action label (left side)
            act = Text(text=f'{action}', parent=camera.ui,
                        position=(-0.22, y), origin=(0, 0),
                        scale=0.85, color=color.rgb(*HUD_SECONDARY),
                        font='VeraMono.ttf')
            elements.append(act)
            # Key binding (right side)
            kb = Text(text=f'{key_bind}', parent=camera.ui,
                       position=(0.12, y), origin=(0, 0),
                       scale=0.85, color=color.rgb(*NEON_GREEN),
                       font='VeraMono.ttf')
            elements.append(kb)

        # Tips
        sep2 = Entity(parent=camera.ui, model='quad',
                       scale=(0.6, 0.002), position=(0, -0.27),
                       color=color.rgb(*NEON_CYAN), z=0)
        elements.append(sep2)

        tips = Text(
            text='TIP: Avoid security drones. Pick up items\n'
                 'for healing and hacking boosts. Use EMP\n'
                 'pulses to disable drones temporarily.',
            parent=camera.ui, position=(0, -0.32), origin=(0, 0),
            scale=0.9, color=color.rgb(100, 100, 160),
            font='VeraMono.ttf',
        )
        elements.append(tips)

        # Dismiss hint
        dismiss = Text(
            text='>>> Press any key or click to start <<<',
            parent=camera.ui, position=(0, -0.43), origin=(0, 0),
            scale=1.3, color=color.rgb(*NEON_MAGENTA),
            font='VeraMono.ttf',
        )
        elements.append(dismiss)

        self.state['tutorial'] = elements

    def _dismiss_tutorial(self):
        """Remove the tutorial overlay and resume the game."""
        for e in self.state.get('tutorial', []):
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.state['tutorial'] = []

        # Resume player control
        player = self.state.get('player')
        if player and player.controller:
            player.controller.enabled = True
        mouse.locked = True
