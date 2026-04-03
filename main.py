"""
main.py — Application Entry Point
====================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Initialises the Ursina application, configures the window,
          creates the SceneManager, and starts the game loop.

How to run:
    Local  : python main.py
    Docker : docker run aim-cyber-reign

This file should stay small.  All game logic lives in the ``src/``
package; main.py just wires everything together and starts the engine.
"""

# ── Ursina engine ──────────────────────────────────────────────────────── #
from ursina import Ursina, window, color

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import (
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FULLSCREEN,
    BORDERLESS,
    DEVELOPMENT_MODE,
    BG_DARK,
)
from src.scenes import SceneManager


# ══════════════════════════════════════════════════════════════════════════ #
#  Application initialisation
# ══════════════════════════════════════════════════════════════════════════ #

# Create the Ursina application with window settings from config
app = Ursina(
    title=WINDOW_TITLE,                # "AIM: Cyber Reign"
    borderless=BORDERLESS,             # windowed with borders
    fullscreen=FULLSCREEN,             # not full‑screen by default
    development_mode=DEVELOPMENT_MODE, # hide dev overlay
    size=(WINDOW_WIDTH, WINDOW_HEIGHT),  # 1280 × 720
)

# ── Window cosmetics ──────────────────────────────────────────────────── #
window.color = color.rgb(*BG_DARK)     # very dark clear colour
try:
    window.clearColor = (BG_DARK[0]/255, BG_DARK[1]/255, BG_DARK[2]/255, 1)
except Exception:
    pass  # fallback if clearColor isn't available in this Ursina version
window.exit_button.visible = False     # hide Ursina's default exit button
window.fps_counter.enabled = False     # hide FPS counter for clean UI


# ══════════════════════════════════════════════════════════════════════════ #
#  Scene Manager
# ══════════════════════════════════════════════════════════════════════════ #

# Create the central scene manager that handles menu ↔ game transitions
scene_manager = SceneManager()


# ══════════════════════════════════════════════════════════════════════════ #
#  Global input handler
# ══════════════════════════════════════════════════════════════════════════ #
def input(key):
    """
    Ursina calls this function on every key‑press / key‑release.

    We delegate to the SceneManager so scene‑specific logic stays
    out of main.py.

    Args:
        key : str — the key that was pressed, e.g. 'escape', 'w', etc.
    """
    scene_manager.handle_input(key)  # let the scene manager decide


# ══════════════════════════════════════════════════════════════════════════ #
#  Launch
# ══════════════════════════════════════════════════════════════════════════ #

# Show the main menu first — the player clicks "Start Game" to play
scene_manager.show_menu()

# Enter the Ursina game loop (blocks until the window is closed)
app.run()
