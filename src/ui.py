"""
ui.py — Heads‑Up Display (HUD) Module (Phase 5)
==================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : In‑game overlay.  Phase 5 adds mission panel
          (title, objective, progress, status, feedback messages).
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import Entity, Text, color, destroy as ursina_destroy, camera

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN, NEON_GREEN, NEON_YELLOW, NEON_MAGENTA,
    HUD_SECONDARY, PROJECT_NAME, PROJECT_VERSION,
    HUD_DEFAULT_ZONE, PLAYER_MAX_HEALTH,
    ALERT_LABELS, ALERT_COLORS,
)


# ══════════════════════════════════════════════════════════════════════════ #
#  HUD class
# ══════════════════════════════════════════════════════════════════════════ #
class HUD(Entity):
    """
    In‑game HUD with:
      Left   : system status, access level, breached nodes
      Right  : zone, sprint, alert, health
      Bottom : mission panel (Phase 5)
      Centre : detection warning, mission feedback
    """

    def __init__(self, player_ref=None, game_state=None, mission_manager=None):
        super().__init__()
        self.player_ref      = player_ref
        self.game_state      = game_state
        self.mission_manager = mission_manager
        self.elements        = []

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

    # ------------------------------------------------------------------ #
    def _t(self, text, x, y, scale, clr):
        c = color.rgb(*clr) if isinstance(clr, tuple) else clr
        t = Text(text=text, position=(x, y), scale=scale,
                 color=c, font='VeraMono.ttf')
        self.elements.append(t)
        return t

    # ------------------------------------------------------------------ #
    def update(self):
        """Refresh dynamic HUD values each frame."""
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

    # ------------------------------------------------------------------ #
    def destroy(self):
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
        for e in self.elements:
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.elements.clear()
        self.player_ref      = None
        self.game_state      = None
        self.mission_manager = None
        super().destroy()
