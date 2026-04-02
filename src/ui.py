"""
ui.py — Heads‑Up Display (HUD) Module (Phase 6)
==================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : In‑game overlay.  Phase 6 adds:
            • Inventory panel (toggle with TAB)
            • Equipment slot display (Q / R)
            • Item pickup feedback messages
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import Entity, Text, color, destroy as ursina_destroy, camera

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_MAGENTA,
    HUD_SECONDARY, PROJECT_NAME, PROJECT_VERSION,
    HUD_DEFAULT_ZONE, PLAYER_MAX_HEALTH,
    ALERT_LABELS, ALERT_COLORS,
    INVENTORY_PANEL_BG,          # Phase 6 — panel background colour
)


# ══════════════════════════════════════════════════════════════════════════ #
#  HUD class
# ══════════════════════════════════════════════════════════════════════════ #
class HUD(Entity):
    """
    In‑game HUD with:
      Left   : system status, access level, breached nodes
      Right  : zone, sprint, alert, health, equipment slots
      Bottom : mission panel (Phase 5)
      Centre : detection warning, mission feedback, item messages
      Overlay: inventory panel (Phase 6 — toggled with TAB)
    """

    def __init__(self, player_ref=None, game_state=None,
                 mission_manager=None, inventory=None,
                 equipment_manager=None):
        """
        Create the HUD.

        Args:
            player_ref        : PlayerController
            game_state        : GameState
            mission_manager   : MissionManager
            inventory         : Inventory      (Phase 6)
            equipment_manager : EquipmentManager (Phase 6)
        """
        super().__init__()
        self.player_ref        = player_ref
        self.game_state        = game_state
        self.mission_manager   = mission_manager
        self.inventory         = inventory           # Phase 6
        self.equipment_manager = equipment_manager   # Phase 6
        self.elements          = []

        # Inventory panel visibility state (Phase 6)
        self._inv_panel_visible = False
        self._inv_elements      = []   # UI elements for the inventory overlay
        self._item_msg_timer    = 0.0  # item feedback message timer

        left_x  = -0.85
        right_x =  0.55

        # ── LEFT: System Status ──────────────────────────────────────── #
        self._t('[ SYSTEM ONLINE ]', left_x, 0.45, 1.2, NEON_CYAN)
        self._t('─' * 22, left_x, 0.42, 0.9, (0, 200, 200))
        self._t(f'{PROJECT_NAME}  v{PROJECT_VERSION}',
                left_x, 0.39, 0.8, HUD_SECONDARY)

        self._t('ACCESS', left_x, 0.33, 0.9, HUD_SECONDARY)
        self.access_text = self._t('LEVEL 1', left_x + 0.09, 0.33, 0.9, NEON_CYAN)

        self._t('NODES', left_x, 0.27, 0.9, HUD_SECONDARY)
        self.nodes_text = self._t('0 / 0 BREACHED', left_x + 0.09, 0.27, 0.9, NEON_GREEN)

        # ── RIGHT: Zone, Sprint, Alert, Health ───────────────────────── #
        self._t('ZONE', right_x, 0.45, 0.9, HUD_SECONDARY)
        self._t(HUD_DEFAULT_ZONE, right_x, 0.42, 1.0, NEON_CYAN)
        self._t('─' * 16, right_x, 0.39, 0.9, (0, 200, 200))

        self.sprint_text = Text(text='', position=(right_x, 0.35), scale=0.9,
                                color=color.rgb(*NEON_YELLOW), font='VeraMono.ttf')
        self.elements.append(self.sprint_text)

        self._t('ALERT', right_x, 0.29, 0.9, HUD_SECONDARY)
        self.alert_text = self._t('CALM', right_x + 0.07, 0.29, 1.0, NEON_GREEN)

        self._t('HEALTH', right_x, 0.23, 0.9, HUD_SECONDARY)
        hbar_bg = Entity(parent=camera.ui, model='quad',
                         scale=(0.18, 0.015), position=(right_x + 0.09, 0.205),
                         color=color.rgb(20, 20, 30))
        self.elements.append(hbar_bg)
        self.health_bar = Entity(parent=camera.ui, model='quad',
                                 scale=(0.18, 0.013),
                                 position=(right_x + 0.09, 0.205),
                                 origin=(-0.5, 0), color=color.rgb(*NEON_GREEN))
        self.elements.append(self.health_bar)
        self.health_text = self._t('100', right_x + 0.20, 0.23, 0.8, NEON_GREEN)

        # ── CENTRE: Detection warning ────────────────────────────────── #
        self.warning_text = Text(text='', position=(0, 0.38), origin=(0, 0),
                                 scale=1.8, color=color.rgb(*NEON_MAGENTA),
                                 font='VeraMono.ttf', visible=False)
        self.elements.append(self.warning_text)

        # ── BOTTOM: Mission panel (Phase 5) ──────────────────────────── #
        self._t('─' * 30, -0.85, -0.34, 0.8, (0, 200, 200))
        self.mission_title = self._t('MISSION: --', -0.85, -0.37, 1.1, NEON_CYAN)
        self.mission_obj   = self._t('', -0.85, -0.40, 0.9, HUD_SECONDARY)
        self.mission_prog  = self._t('', -0.85, -0.43, 0.9, NEON_YELLOW)
        self.mission_status = self._t('', -0.85, -0.46, 0.9, NEON_GREEN)

        # Mission feedback message (centre screen)
        self.mission_msg = Text(text='', position=(0, -0.15), origin=(0, 0),
                                scale=1.5, color=color.rgb(*NEON_CYAN),
                                font='VeraMono.ttf', visible=False)
        self.elements.append(self.mission_msg)

        # ── BOTTOM-RIGHT: Equipment slots (Phase 6) ─────────────────── #
        self._t('─' * 16, right_x, 0.14, 0.8, (0, 200, 200))
        self._t('EQUIPMENT', right_x, 0.11, 0.9, HUD_SECONDARY)
        self.equip_q_text = self._t('[Q] ---', right_x, 0.07, 0.85, NEON_CYAN)
        self.equip_r_text = self._t('[R] ---', right_x, 0.03, 0.85, NEON_CYAN)

        # ── CENTRE: Item feedback message (Phase 6) ──────────────────── #
        self.item_msg = Text(text='', position=(0, -0.25), origin=(0, 0),
                             scale=1.3, color=color.rgb(*NEON_GREEN),
                             font='VeraMono.ttf', visible=False)
        self.elements.append(self.item_msg)

    # ------------------------------------------------------------------ #
    def _t(self, text, x, y, scale, clr):
        """Create a Text element and track it for cleanup."""
        c = color.rgb(*clr) if isinstance(clr, tuple) else clr
        t = Text(text=text, position=(x, y), scale=scale,
                 color=c, font='VeraMono.ttf')
        self.elements.append(t)
        return t

    # ------------------------------------------------------------------ #
    def show_item_message(self, text, duration=2.0):
        """
        Show a brief item‑related feedback message.

        Args:
            text     : str   — message to display (e.g. "Picked up Energy Cell")
            duration : float — how long to show (seconds)
        """
        self.item_msg.text    = text
        self.item_msg.visible = True
        self._item_msg_timer  = duration

    # ================================================================== #
    #  INVENTORY PANEL  (Phase 6 — toggled with TAB)
    # ================================================================== #
    def toggle_inventory_panel(self):
        """Open or close the inventory overlay panel."""
        if self._inv_panel_visible:
            self._close_inventory_panel()
        else:
            self._open_inventory_panel()

    def _open_inventory_panel(self):
        """Build and display the inventory overlay."""
        self._close_inventory_panel()   # ensure clean state

        self._inv_panel_visible = True
        elements = []

        # Dark semi‑transparent backdrop
        bg = Entity(parent=camera.ui, model='quad', scale=(0.55, 0.55),
                     position=(0, 0.05),
                     color=color.rgba(*INVENTORY_PANEL_BG, 220), z=0.3)
        elements.append(bg)

        # Title
        title = Text(text='[ INVENTORY ]', parent=camera.ui,
                      position=(0, 0.28), origin=(0, 0),
                      scale=1.5, color=color.rgb(*NEON_CYAN), font='VeraMono.ttf')
        elements.append(title)

        # Separator
        sep = Text(text='─' * 24, parent=camera.ui,
                    position=(0, 0.24), origin=(0, 0),
                    scale=0.8, color=color.rgb(0, 200, 200), font='VeraMono.ttf')
        elements.append(sep)

        # Item list
        if self.inventory:
            items = self.inventory.get_items()
            if not items:
                empty = Text(text='[ EMPTY ]', parent=camera.ui,
                              position=(0, 0.15), origin=(0, 0),
                              scale=1.0, color=color.rgb(100, 100, 140),
                              font='VeraMono.ttf')
                elements.append(empty)
            else:
                eq_q = None  # currently equipped in Q slot
                eq_r = None  # currently equipped in R slot
                if self.equipment_manager:
                    eq_q = self.equipment_manager.slots.get('q')
                    eq_r = self.equipment_manager.slots.get('r')

                for idx, (item, count) in enumerate(items):
                    y_pos = 0.18 - idx * 0.05

                    # Check if this item is equipped
                    equip_tag = ''
                    if item.item_type == eq_q:
                        equip_tag = ' [Q]'
                    elif item.item_type == eq_r:
                        equip_tag = ' [R]'

                    # Item line: icon + name x count + equip tag
                    line_text = f'{item.icon_char} {item.name} x{count}{equip_tag}'
                    clr = NEON_GREEN if equip_tag else NEON_CYAN

                    t = Text(text=line_text, parent=camera.ui,
                              position=(-0.18, y_pos), origin=(0, 0),
                              scale=0.9, color=color.rgb(*clr), font='VeraMono.ttf')
                    elements.append(t)

        # Capacity footer
        if self.inventory:
            used  = len(self.inventory.slots)
            total = self.inventory.max_slots
            cap = Text(text=f'Slots: {used}/{total}', parent=camera.ui,
                        position=(0, -0.18), origin=(0, 0),
                        scale=0.8, color=color.rgb(*HUD_SECONDARY), font='VeraMono.ttf')
            elements.append(cap)

        # Hint
        hint = Text(text='[TAB] Close  |  [1-8] Equip Q  |  [SHIFT+1-8] Equip R',
                     parent=camera.ui, position=(0, -0.22), origin=(0, 0),
                     scale=0.7, color=color.rgb(80, 80, 100), font='VeraMono.ttf')
        elements.append(hint)

        self._inv_elements = elements

    def _close_inventory_panel(self):
        """Remove the inventory overlay."""
        for e in self._inv_elements:
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self._inv_elements.clear()
        self._inv_panel_visible = False

    @property
    def inventory_open(self):
        """Whether the inventory panel is currently visible."""
        return self._inv_panel_visible

    # ------------------------------------------------------------------ #
    def update(self):
        """Refresh dynamic HUD values each frame."""
        # ── Item message timer (Phase 6) ─────────────────────────────── #
        if self._item_msg_timer > 0:
            self._item_msg_timer -= 0.016   # approximate dt
            if self._item_msg_timer <= 0:
                self.item_msg.visible = False

        # Sprint
        if self.player_ref and hasattr(self.player_ref, 'is_sprinting'):
            self.sprint_text.text = '>> SPRINT <<' if self.player_ref.is_sprinting else ''

        if self.game_state:
            stats = self.game_state.get_stats()

            # Nodes
            b, t = stats['breached'], stats['total']
            self.nodes_text.text  = f'{b} / {t} BREACHED'
            self.nodes_text.color = (color.rgb(*NEON_MAGENTA)
                                     if b >= t and t > 0
                                     else color.rgb(*NEON_GREEN))
            self.access_text.text = f'LEVEL {stats["access_level"]}'

            # Health
            hp = stats['health']
            frac = hp / PLAYER_MAX_HEALTH
            self.health_text.text = f'{int(hp)}'
            self.health_bar.scale_x = 0.18 * frac
            if frac > 0.5:
                hc = NEON_GREEN
            elif frac > 0.25:
                hc = NEON_YELLOW
            else:
                hc = NEON_MAGENTA
            self.health_bar.color  = color.rgb(*hc)
            self.health_text.color = color.rgb(*hc)

            # Alert
            al = stats['alert_level']
            self.alert_text.text  = ALERT_LABELS.get(al, 'CALM')
            self.alert_text.color = color.rgb(*ALERT_COLORS.get(al, NEON_GREEN))
            if al >= 2:
                self.warning_text.text = '⚠ SECURITY ALERT ⚠'
                self.warning_text.visible = True
            elif al >= 1:
                self.warning_text.text = '[ SUSPICIOUS ACTIVITY ]'
                self.warning_text.visible = True
            else:
                self.warning_text.visible = False

        # ── Mission panel (Phase 5) ──────────────────────────────────── #
        if self.mission_manager:
            info = self.mission_manager.get_hud_info()
            self.mission_title.text  = f'MISSION: {info["mission_name"]}'
            self.mission_obj.text    = f'OBJ: {info["objective"]}'
            self.mission_prog.text   = info['progress']
            self.mission_status.text = info['status']

            # Status colour
            if 'COMPLETE' in info['status']:
                self.mission_status.color = color.rgb(*NEON_GREEN)
            elif 'FAILED' in info['status']:
                self.mission_status.color = color.rgb(*NEON_MAGENTA)
            else:
                self.mission_status.color = color.rgb(*NEON_CYAN)

            # Feedback message
            if info['show_message'] and info['message']:
                self.mission_msg.text    = info['message']
                self.mission_msg.visible = True
            else:
                self.mission_msg.visible = False

        # ── Equipment slots (Phase 6) ────────────────────────────────── #
        if self.equipment_manager:
            q_info = self.equipment_manager.get_slot_info('q')
            r_info = self.equipment_manager.get_slot_info('r')

            # Q slot display
            if q_info['item_type']:
                q_name = q_info['item_type'].replace('_', ' ').title()
                if q_info['ready']:
                    self.equip_q_text.text  = f'[Q] {q_name}'
                    self.equip_q_text.color = color.rgb(*NEON_CYAN)
                else:
                    cd = q_info['cooldown']
                    self.equip_q_text.text  = f'[Q] {q_name} ({cd:.1f}s)'
                    self.equip_q_text.color = color.rgb(*NEON_YELLOW)
            else:
                self.equip_q_text.text  = '[Q] ---'
                self.equip_q_text.color = color.rgb(80, 80, 100)

            # R slot display
            if r_info['item_type']:
                r_name = r_info['item_type'].replace('_', ' ').title()
                if r_info['ready']:
                    self.equip_r_text.text  = f'[R] {r_name}'
                    self.equip_r_text.color = color.rgb(*NEON_CYAN)
                else:
                    cd = r_info['cooldown']
                    self.equip_r_text.text  = f'[R] {r_name} ({cd:.1f}s)'
                    self.equip_r_text.color = color.rgb(*NEON_YELLOW)
            else:
                self.equip_r_text.text  = '[R] ---'
                self.equip_r_text.color = color.rgb(80, 80, 100)

    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove all HUD elements."""
        self._close_inventory_panel()   # Phase 6 — cleanup inv panel
        try:
            ursina_destroy(self.sprint_text)
        except Exception:
            pass
        try:
            ursina_destroy(self.warning_text)
        except Exception:
            pass
        try:
            ursina_destroy(self.mission_msg)
        except Exception:
            pass
        try:
            ursina_destroy(self.item_msg)
        except Exception:
            pass
        for e in self.elements:
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.elements.clear()
        self.player_ref        = None
        self.game_state        = None
        self.mission_manager   = None
        self.inventory         = None
        self.equipment_manager = None
        super().destroy()
