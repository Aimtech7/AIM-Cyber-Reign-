"""
menu.py — Main Menu Module (Phase 2)
======================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Renders the full‑screen cyberpunk main menu with animated
          floating particles, a neon title, subtitle, "by Aimtech"
          credit, and three buttons: Start Game, Settings, Exit.

Changes in Phase 2:
    • Added animated background particles that drift across the screen
    • Added a "Settings" button
    • Improved visual layout with more decorative elements

How it connects:
    The SceneManager (scenes.py) creates a MainMenu when the game
    starts or when the player presses ESC.  Callbacks are provided
    for Start, Settings, and Exit actions.

Key concepts:
    • MenuParticle is an Entity subclass whose update() makes it
      drift slowly across the screen, creating a living background.
    • All menu elements are parented to camera.ui (2D overlay).
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
    MENU_BG,
    BUTTON_COLOR,
    MENU_PARTICLE_COUNT,
    MENU_PARTICLE_SPEED,
    SFX_CLICK,         # Phase 7 — button click sound name
)


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

    def __init__(self, start_callback, settings_callback, exit_callback,
                 audio_manager=None):
        """
        Build every visual element of the main menu.

        Args:
            start_callback    : called when "START GAME" is clicked
            settings_callback : called when "SETTINGS" is clicked
            exit_callback     : called when "EXIT" is clicked
            audio_manager     : AudioManager (Phase 7) — optional
        """
        # Store audio reference for button clicks (Phase 7)
        self._audio = audio_manager
        # Master list of all UI entities — used by destroy()
        self.elements = []

        # ── Full‑screen dark backdrop ────────────────────────────────── #
        bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(2, 1),
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
            text='v0.7.0  //  Phase 7',
            parent=camera.ui,
            position=(0, 0.14),
            origin=(0, 0),
            scale=0.8,
            color=color.rgb(60, 60, 100),
            font='VeraMono.ttf',
        )
        self.elements.append(version)

        # ── Buttons ──────────────────────────────────────────────────── #
        self._make_button('>> START GAME <<', y_pos=0.04,  callback=start_callback)
        self._make_button('>> SETTINGS <<',   y_pos=-0.06, callback=settings_callback)
        self._make_button('>> EXIT <<',       y_pos=-0.16, callback=exit_callback)

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
    def _make_button(self, label, y_pos, callback):
        """
        Create a single neon‑styled menu button.

        Args:
            label    : str      — text displayed on the button
            y_pos    : float    — vertical position (screen coords)
            callback : callable — function called on click
        """
        btn = Button(
            text=label,
            parent=camera.ui,
            scale=(0.4, 0.06),
            position=(0, y_pos),
            color=color.rgb(*BUTTON_COLOR),
            highlight_color=color.rgb(*NEON_MAGENTA),
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
