"""
settings.py — Settings Menu Module
=====================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Renders a settings panel with placeholder controls for
          volume, mouse sensitivity, and graphics quality.
          The controls are visual only in Phase 2; real logic will
          be wired in a future phase.

How it connects:
    The SceneManager (scenes.py) creates a SettingsMenu when the
    player clicks "Settings" from the main menu, and calls destroy()
    when the player clicks "Back".

Key concepts:
    • The settings panel is drawn on ``camera.ui`` (2D overlay).
    • Ursina's ``Slider`` is used for volume and sensitivity.
    • A simple button‑group toggles graphics quality.
    • A "Back" button returns to the main menu.
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import (
    Entity,
    Text,
    Button,
    Slider,
    camera,
    color,
    destroy as ursina_destroy,
)

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    NEON_CYAN,
    NEON_PURPLE,
    NEON_MAGENTA,
    SETTINGS_BG,
    BUTTON_COLOR,
    SFX_CLICK,   # Phase 7 — click sound constant
)


# ══════════════════════════════════════════════════════════════════════════ #
#  SettingsMenu class
# ══════════════════════════════════════════════════════════════════════════ #
class SettingsMenu:
    """
    Full‑screen settings panel with placeholder controls.

    Parameters:
        back_callback : callable
            Function to invoke when the player clicks "Back".

    Usage:
        settings = SettingsMenu(back_callback=show_menu)
        settings.destroy()
    """

    def __init__(self, back_callback, audio_manager=None):
        """
        Build the settings panel UI.

        Args:
            back_callback : called when "BACK" is clicked.
            audio_manager : AudioManager (Phase 7) — optional
        """
        # Store audio reference (Phase 7)
        self._audio = audio_manager
        self._back_callback = back_callback
        # Master list of every UI entity — used by destroy()
        self.elements = []

        # ── Full‑screen dark backdrop ────────────────────────────────── #
        bg = Entity(
            parent=camera.ui,
            model='quad',
            scale=(3, 3),
            color=color.rgb(*SETTINGS_BG),
            z=1,
        )
        self.elements.append(bg)

        # ── Title ────────────────────────────────────────────────────── #
        title = Text(
            text='[ SETTINGS ]',
            parent=camera.ui,
            position=(0, 0.40),
            origin=(0, 0),
            scale=2.5,
            color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        self.elements.append(title)

        # ── Separator ─────────────────────────────────────────────────── #
        sep = Entity(
            parent=camera.ui,
            model='quad',
            scale=(0.5, 0.002),
            position=(0, 0.34),
            color=color.rgb(*NEON_CYAN),
        )
        self.elements.append(sep)

        # ── Volume slider ────────────────────────────────────────────── #
        vol_label = Text(
            text='Volume',
            parent=camera.ui,
            position=(-0.22, 0.25),
            origin=(0, 0),
            scale=1.1,
            color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        self.elements.append(vol_label)

        vol_slider = Slider(
            min=0, max=100, default=75,        # 0–100 range
            parent=camera.ui,
            position=(0.08, 0.25),
            scale=0.8,
            dynamic=True,                       # updates while dragging
            color=color.rgb(*BUTTON_COLOR),
            knob_color=color.rgb(*NEON_MAGENTA),
        )
        # Phase 7 — wire volume slider to audio manager
        vol_slider.on_value_changed = self._on_volume_changed
        self.elements.append(vol_slider)

        # ── Sensitivity slider ───────────────────────────────────────── #
        sens_label = Text(
            text='Mouse Sensitivity',
            parent=camera.ui,
            position=(-0.22, 0.15),
            origin=(0, 0),
            scale=1.1,
            color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        self.elements.append(sens_label)

        sens_slider = Slider(
            min=10, max=200, default=80,
            parent=camera.ui,
            position=(0.08, 0.15),
            scale=0.8,
            dynamic=True,
            color=color.rgb(*BUTTON_COLOR),
            knob_color=color.rgb(*NEON_MAGENTA),
        )
        self.elements.append(sens_slider)

        # ── Graphics quality buttons ─────────────────────────────────── #
        gfx_label = Text(
            text='Graphics Quality',
            parent=camera.ui,
            position=(-0.22, 0.03),
            origin=(0, 0),
            scale=1.1,
            color=color.rgb(*NEON_CYAN),
            font='VeraMono.ttf',
        )
        self.elements.append(gfx_label)

        # Three quality preset buttons
        quality_names = ['LOW', 'MEDIUM', 'HIGH']
        for i, qname in enumerate(quality_names):
            x_pos = 0.02 + i * 0.14   # space them out horizontally
            btn = Button(
                text=qname,
                parent=camera.ui,
                scale=(0.12, 0.04),
                position=(x_pos, 0.03),
                color=color.rgb(*BUTTON_COLOR),
                highlight_color=color.rgb(*NEON_MAGENTA),
                pressed_color=color.rgb(*NEON_PURPLE),
                text_color=color.rgb(*NEON_CYAN),
            )
            btn.text_entity.font = 'VeraMono.ttf'
            self.elements.append(btn)

        # ── "Note: placeholder" reminder ─────────────────────────────── #
        note = Text(
            text='* Drag volume slider to adjust game audio',
            parent=camera.ui,
            position=(0, -0.12),
            origin=(0, 0),
            scale=0.8,
            color=color.rgb(80, 80, 100),
            font='VeraMono.ttf',
        )
        self.elements.append(note)

        # ── Back button ──────────────────────────────────────────────── #
        back_btn = Button(
            text='>> BACK <<',
            parent=camera.ui,
            scale=(0.3, 0.06),
            position=(0, -0.28),
            color=color.rgb(*BUTTON_COLOR),
            highlight_color=color.rgb(*NEON_MAGENTA),
            pressed_color=color.rgb(*NEON_PURPLE),
            text_color=color.rgb(*NEON_CYAN),
            on_click=self._on_back_click,   # Phase 7 — wrapped callback
        )
        back_btn.text_entity.font = 'VeraMono.ttf'
        self.elements.append(back_btn)

    # ------------------------------------------------------------------ #
    #  Volume slider callback  (Phase 7)
    # ------------------------------------------------------------------ #
    def _on_volume_changed(self):
        """Update master volume when the slider moves."""
        if self._audio:
            # Slider value is 0–100 → convert to 0.0–1.0
            # Access the slider value from the elements list
            for el in self.elements:
                if isinstance(el, Slider) and hasattr(el, 'value'):
                    self._audio.set_volume('master', el.value / 100.0)
                    break

    # ------------------------------------------------------------------ #
    #  Back button with SFX  (Phase 7)
    # ------------------------------------------------------------------ #
    def _on_back_click(self):
        """Play click sound then return to menu."""
        if self._audio:
            self._audio.play_sfx(SFX_CLICK)
        if self._back_callback:
            self._back_callback()

    # ------------------------------------------------------------------ #
    #  Cleanup
    # ------------------------------------------------------------------ #
    def destroy(self):
        """Remove every settings element from the screen."""
        for element in self.elements:
            try:
                ursina_destroy(element)
            except Exception:
                pass
        self.elements.clear()
