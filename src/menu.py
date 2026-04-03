"""
menu.py — Main Menu Module (Phase 8)
======================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Renders the full‑screen cyberpunk main menu with animated
          floating particles, a neon title, subtitle, "by Aimtech"
          credit, and buttons: Continue (if save exists), Start Game,
          Settings, Exit.

Phase 8 changes:
    • Added "CONTINUE" button (only shown when a save file exists)
    • Updated version tag to v0.8.0
"""

# ── Standard library ───────────────────────────────────────────────────── #
import random  # random positions and speeds for particles

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Text,
    Button,
    camera,
    color,
    time as ursina_time,
    destroy as ursina_destroy,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN,
    NEON_PURPLE,
    NEON_MAGENTA,
    NEON_BLUE,
    NEON_GREEN,              # Phase 8 — for Continue button
    MENU_BG,
    BUTTON_COLOR,
    MENU_PARTICLE_COUNT,
    MENU_PARTICLE_SPEED,
    SFX_CLICK,               # Phase 7 — button click sound name
    PROJECT_VERSION,         # Phase 8 — dynamic version display
    PROJECT_PHASE,           # Phase 8 — dynamic phase display
)
from src.save_system import save_exists   # Phase 8 — check for save file


# ══════════════════════════════════════════════════════════════════════════ #
#  MenuParticle — drifting background dot
# ══════════════════════════════════════════════════════════════════════════ #
class MenuParticle(Entity):
    """
    A tiny glowing quad that drifts upward across the menu background.
    When it leaves the top of the screen it wraps back to the bottom,
    creating continuous ambient motion.
    """

    def __init__(self):
        """Create one particle with random position, speed, and colour."""
        # Pick a random starting position across the screen (UI coords)
        start_x = random.uniform(-0.9, 0.9)    # horizontal spread
        start_y = random.uniform(-0.6, 0.6)     # vertical spread

        # Pick a random size (very small)
        size = random.uniform(0.003, 0.008)

        # Pick a random neon colour from a small palette
        clr = random.choice([
            color.rgb(*NEON_CYAN),
            color.rgb(*NEON_PURPLE),
            color.rgb(*NEON_MAGENTA),
            color.rgb(*NEON_BLUE),
        ])

        # Initialise the Entity as a tiny glowing quad
        super().__init__(
            parent=camera.ui,
            model='quad',
            scale=(size, size),
            position=(start_x, start_y),
            color=color.rgba(clr.r * 255, clr.g * 255, clr.b * 255, 120),
            z=0.5,          # between background and UI elements
            unlit=True,     # ignore lighting
        )

        # Random drift speed (units per second)
        self.speed_y = random.uniform(*MENU_PARTICLE_SPEED)
        # Slight horizontal sway speed
        self.speed_x = random.uniform(-0.05, 0.05)

    def update(self):
        """Move the particle upward each frame; wrap when off‑screen."""
        # Move upward and sway horizontally
        self.y += self.speed_y * ursina_time.dt   # vertical drift
        self.x += self.speed_x * ursina_time.dt   # horizontal sway

        # Wrap to bottom when it drifts above the top edge
        if self.y > 0.6:
            self.y = -0.6                          # reset to bottom
            self.x = random.uniform(-0.9, 0.9)    # new random x


# ══════════════════════════════════════════════════════════════════════════ #
#  MainMenu class
# ══════════════════════════════════════════════════════════════════════════ #
class MainMenu:
    """
    Full‑screen cyberpunk main menu with animated particles.

    Parameters:
        start_callback    : callable — "Start Game" action
        settings_callback : callable — "Settings" action
        exit_callback     : callable — "Exit" action

    Usage:
        menu = MainMenu(start_callback, settings_callback, exit_callback)
        menu.destroy()
    """

    def __init__(self, start_callback, settings_callback, how_to_play_callback, exit_callback,
                 audio_manager=None, continue_callback=None):
        """
        Build every visual element of the main menu.

        Args:
            start_callback       : called when "START GAME" is clicked
            settings_callback    : called when "SETTINGS" is clicked
            how_to_play_callback : called when "HOW TO PLAY" is clicked
            exit_callback        : called when "EXIT" is clicked
            audio_manager        : AudioManager (Phase 7) — optional
            continue_callback    : called when "CONTINUE" is clicked (Phase 8)
        """
        # Store audio reference for button clicks (Phase 7)
        self._audio = audio_manager
        # Store continue callback for Phase 8
        self._continue_callback = continue_callback
        # Master list of all UI entities — used by destroy()
        self.elements = []

        # ── Full‑screen dark backdrop ────────────────────────────────── #
        bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(3, 3),
            color=color.rgb(*MENU_BG),
            z=1,                    # furthest back
        )
        self.elements.append(bg)

        # ── Animated background particles ────────────────────────────── #
        self.particles = []
        for _ in range(MENU_PARTICLE_COUNT):
            p = MenuParticle()      # each particle animates itself
            self.particles.append(p)
            self.elements.append(p)

        # ── Decorative neon lines ────────────────────────────────────── #
        # Top line above the title
        self._add_line(y=0.32, width=0.7)
        # Line between title and buttons
        self._add_line(y=0.12, width=0.5)
        # Line below the buttons
        self._add_line(y=-0.22, width=0.5)

        # ── Title text ───────────────────────────────────────────────── #
        title = Text(
            text='AIM: CYBER REIGN',
            parent=camera.ui,
            position=(0, 0.26),
            origin=(0, 0),
            scale=3.2,                          # slightly larger than Phase 1
            color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        self.elements.append(title)

        # ── Subtitle / tagline ───────────────────────────────────────── #
        subtitle = Text(
            text='ENTER THE DIGITAL FRONTIER',
            parent=camera.ui,
            position=(0, 0.18),
            origin=(0, 0),
            scale=1.0,
            color=color.rgb(0, 180, 200),
            font='VeraMono.ttf',
        )
        self.elements.append(subtitle)

        # ── Version tag ──────────────────────────────────────────────── #
        version = Text(
            text=f'v{PROJECT_VERSION}  //  {PROJECT_PHASE}',
            parent=camera.ui,
            position=(0, 0.14),
            origin=(0, 0),
            scale=0.8,
            color=color.rgb(60, 60, 100),
            font='VeraMono.ttf',
        )
        self.elements.append(version)

        # ── Buttons ──────────────────────────────────────────────────── #
        # Phase 8 — show Continue button if a save file exists
        btn_y = 0.06
        if save_exists() and self._continue_callback:
            self._make_button(
                '>> CONTINUE <<', y_pos=btn_y,
                callback=self._continue_callback,
                highlight_clr=NEON_GREEN,
            )
            btn_y -= 0.10

        self._make_button('>> START GAME <<', y_pos=btn_y,  callback=start_callback)
        btn_y -= 0.10
        self._make_button('>> SETTINGS <<',   y_pos=btn_y, callback=settings_callback)
        btn_y -= 0.10
        self._make_button('>> HOW TO PLAY <<',y_pos=btn_y, callback=how_to_play_callback)
        btn_y -= 0.10
        self._make_button('>> EXIT <<',       y_pos=btn_y, callback=exit_callback)

        # ── Author credit ────────────────────────────────────────────── #
        author = Text(
            text='by Aimtech',
            parent=camera.ui,
            position=(0, -0.38),
            origin=(0, 0),
            scale=0.9,
            color=color.rgb(0, 140, 160),
            font='VeraMono.ttf',
        )
        self.elements.append(author)

    # ------------------------------------------------------------------ #
    #  Decorative line helper
    # ------------------------------------------------------------------ #
    def _add_line(self, y, width=0.6):
        """Add a thin horizontal neon line at the given y position."""
        line = Entity(
            parent=camera.ui,
            model='quad',
            scale=(width, 0.002),
            position=(0, y),
            color=color.rgb(*NEON_CYAN),
            z=0,
        )
        self.elements.append(line)

    # ------------------------------------------------------------------ #
    #  Button factory helper
    # ------------------------------------------------------------------ #
    def _make_button(self, label, y_pos, callback, highlight_clr=None):
        """
        Create a single neon‑styled menu button.

        Args:
            label         : str      — text displayed on the button
            y_pos         : float    — vertical position (screen coords)
            callback      : callable — function called on click
            highlight_clr : tuple    — optional hover colour override
        """
        h_clr = color.rgb(*highlight_clr) if highlight_clr else color.rgb(*NEON_MAGENTA)
        btn = Button(
            text=label,
            parent=camera.ui,
            scale=(0.4, 0.06),
            position=(0, y_pos),
            color=color.rgb(*BUTTON_COLOR),
            highlight_color=h_clr,
            pressed_color=color.rgb(*NEON_PURPLE),
            text_color=color.rgb(*NEON_CYAN),
            on_click=lambda cb=callback: self._on_btn_click(cb),  # Phase 7
        )
        btn.text_entity.font = 'VeraMono.ttf'
        self.elements.append(btn)

    # ------------------------------------------------------------------ #
    #  Button click with SFX  (Phase 7)
    # ------------------------------------------------------------------ #
    def _on_btn_click(self, callback):
        """Play click sound then fire the original callback."""
        if self._audio:
            self._audio.play_sfx(SFX_CLICK)   # Phase 7 — click SFX
        if callback:
            callback()

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove every menu element (including particles) from screen."""
        for element in self.elements:
            try:
                ursina_destroy(element)
            except Exception:
                pass
        self.elements.clear()
        self.particles.clear()


# ══════════════════════════════════════════════════════════════════════════ #
#  HowToPlayMenu class
# ══════════════════════════════════════════════════════════════════════════ #
class HowToPlayMenu:
    """
    Shows game instructions and controls before starting.
    """

    def __init__(self, back_callback, audio_manager=None):
        self._audio = audio_manager
        self.elements = []

        # Backdrop
        bg = Entity(parent=camera.ui, model='quad', scale=(3, 3),
                     color=color.rgb(*MENU_BG), z=1)
        self.elements.append(bg)

        # Title
        title = Text(text='[ HOW TO PLAY ]', parent=camera.ui,
                      position=(0, 0.38), origin=(0, 0),
                      scale=2.5, color=color.rgb(*NEON_CYAN),
                      font='VeraMono.ttf')
        self.elements.append(title)

        sep = Entity(parent=camera.ui, model='quad',
                      scale=(0.6, 0.002), position=(0, 0.33),
                      color=color.rgb(*NEON_CYAN), z=0)
        self.elements.append(sep)

        # Objective
        obj_text = Text(
            text='OBJECTIVE: Hack target terminals and reach\n'
                 'the extraction zone to complete the mission.',
            parent=camera.ui, position=(0, 0.27), origin=(0, 0),
            scale=1.1, color=color.rgb(*NEON_YELLOW),
            font='VeraMono.ttf',
        )
        self.elements.append(obj_text)

        # Controls section
        controls = [
            ('MOVEMENT',      'W A S D'),
            ('LOOK',          'Mouse'),
            ('SPRINT',        'Hold Left Shift'),
            ('JUMP',          'Space'),
            ('INTERACT/HACK', 'E'),
            ('INVENTORY',     'TAB'),
            ('USE ITEM Q/R',  'Q / R'),
        ]

        ctrl_header = Text(
            text='─── CONTROLS ───', parent=camera.ui,
            position=(0, 0.17), origin=(0, 0),
            scale=1.2, color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        self.elements.append(ctrl_header)

        y_start = 0.12
        for i, (action, key_bind) in enumerate(controls):
            y = y_start - i * 0.05
            act = Text(text=f'{action}', parent=camera.ui,
                        position=(-0.22, y), origin=(0, 0),
                        scale=0.85, color=color.rgb(0, 180, 180),
                        font='VeraMono.ttf')
            self.elements.append(act)
            kb = Text(text=f'{key_bind}', parent=camera.ui,
                       position=(0.12, y), origin=(0, 0),
                       scale=0.85, color=color.rgb(*NEON_GREEN),
                       font='VeraMono.ttf')
            self.elements.append(kb)

        # Back Button
        from ursina import Button
        btn = Button(
            text='>> BACK <<',
            parent=camera.ui,
            position=(0, -0.35),
            scale=(0.3, 0.06),
            color=color.rgb(*BUTTON_COLOR),
            highlight_color=color.rgb(*NEON_PURPLE),
        )
        btn.text_entity.font = 'VeraMono.ttf'
        btn.text_entity.color = color.rgb(200, 200, 200)

        def click_wrapper():
            if self._audio:
                self._audio.play_sfx(SFX_CLICK)
            back_callback()
            
        btn.on_click = click_wrapper
        self.elements.append(btn)

    def destroy(self):
        for e in self.elements:
            try:
                ursina_destroy(e)
            except Exception:
                pass
        self.elements.clear()
