"""
config.py — Global Configuration Module
=========================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : Stores all global constants, colour palettes, window settings,
          and gameplay parameters in one central place so every other
          module can import them without hard‑coding values.

Why this file exists:
    Centralising configuration avoids "magic numbers" scattered across
    the codebase and makes the game easy to tune or theme‑swap later.
"""

# ──────────────────────────────────────────────────────────────────────── #
#  Window / Application Settings
# ──────────────────────────────────────────────────────────────────────── #

# The title shown in the OS title‑bar
WINDOW_TITLE = "AIM: Cyber Reign"

# Default window dimensions (width × height in pixels)
WINDOW_WIDTH  = 1280   # horizontal resolution
WINDOW_HEIGHT = 720    # vertical resolution

# Whether to launch in full‑screen mode (True/False)
FULLSCREEN = False

# Whether to use borderless window mode (True/False)
BORDERLESS = False

# Hide Ursina's built‑in development overlays for a clean look
DEVELOPMENT_MODE = False


# ──────────────────────────────────────────────────────────────────────── #
#  Colour Palette — Cyberpunk Neon Theme
# ──────────────────────────────────────────────────────────────────────── #
# Colours are stored as (R, G, B) tuples so they can be converted
# to any format required by the engine.

# Primary accent — vivid cyan used for titles, HUD, grid lines
NEON_CYAN     = (0, 255, 255)

# Secondary accent — electric purple for buttons and highlights
NEON_PURPLE   = (160, 0, 255)

# Tertiary accent — hot magenta for hover / active states
NEON_MAGENTA  = (255, 0, 180)

# Lighter blue variant for subtle accents
NEON_BLUE     = (0, 200, 255)

# Deep violet for building edges and decorative elements
NEON_VIOLET   = (120, 0, 255)

# Warm neon yellow — used for interaction prompts and warnings
NEON_YELLOW   = (255, 255, 0)

# Neon green — used for positive status indicators
NEON_GREEN    = (0, 255, 120)

# Very dark background colour for the window clear colour
BG_DARK       = (2, 2, 10)

# Dark panel colour used behind the main menu
MENU_BG       = (5, 5, 15)

# Button base colour — very dark purple
BUTTON_COLOR  = (20, 0, 40)

# Subdued cyan for secondary HUD text
HUD_SECONDARY = (0, 180, 180)

# Settings panel background — slightly lighter than menu BG
SETTINGS_BG   = (10, 8, 25)


# ──────────────────────────────────────────────────────────────────────── #
#  Player Settings
# ──────────────────────────────────────────────────────────────────────── #

# Normal walk speed in world units per second
PLAYER_SPEED = 6

# Sprint speed multiplier — applied when holding Shift
PLAYER_SPRINT_MULTIPLIER = 1.8

# Jump height in world units
PLAYER_JUMP_HEIGHT = 2

# Mouse sensitivity as (x, y) — higher = faster look
PLAYER_MOUSE_SENSITIVITY = (80, 80)

# Starting position of the player in the world
PLAYER_START_POS = (0, 2, 0)


# ──────────────────────────────────────────────────────────────────────── #
#  Interaction Settings
# ──────────────────────────────────────────────────────────────────────── #

# Maximum distance (world units) for the player to interact with objects
INTERACT_DISTANCE = 5.0

# Key used to interact with objects
INTERACT_KEY = 'e'

# How long the interaction message stays on screen (seconds)
INTERACT_MSG_DURATION = 3.0


# ──────────────────────────────────────────────────────────────────────── #
#  Environment Settings
# ──────────────────────────────────────────────────────────────────────── #

# Size of the ground plane (width, 1, depth)
FLOOR_SCALE = (100, 1, 100)

# Floor base colour — very dark blue‑black
FLOOR_COLOR = (10, 10, 25)

# How many grid squares appear on the floor texture
FLOOR_GRID_DENSITY = 50

# Spacing between grid overlay lines (in world units)
GRID_LINE_SPACING = 2

# Alpha transparency for the grid lines (0–255)
GRID_LINE_ALPHA = 25


# ──────────────────────────────────────────────────────────────────────── #
#  Building Specifications
# ──────────────────────────────────────────────────────────────────────── #
# Each tuple is (x, z, width, height, depth) — placed symmetrically
# around the origin to form a small "city block".

BUILDING_SPECS = [
    (-12, -8,  3, 8,  3),
    (-8,  -15, 2, 12, 2),
    ( 5,  -10, 4, 6,  4),
    ( 15, -5,  3, 15, 3),
    (-18,  10, 2, 10, 2),
    ( 10,  12, 5, 7,  3),
    ( 20, -18, 3, 18, 3),
    (-6,   20, 4, 9,  4),
    ( 0,  -25, 2, 14, 2),
    (-22, -20, 3, 11, 3),
    ( 18,  22, 4, 6,  4),
    (-15,  25, 2, 16, 2),
]


# ──────────────────────────────────────────────────────────────────────── #
#  Pillar Specifications  (Phase 2)
# ──────────────────────────────────────────────────────────────────────── #
# Decorative neon pillars: (x, z, radius, height)

PILLAR_SPECS = [
    (-4,  -4,  0.3, 5),
    ( 4,  -4,  0.3, 5),
    (-4,   4,  0.3, 5),
    ( 4,   4,  0.3, 5),
    ( 0,  -8,  0.4, 7),
    ( 0,   8,  0.4, 7),
    (-8,   0,  0.3, 6),
    ( 8,   0,  0.3, 6),
]


# ──────────────────────────────────────────────────────────────────────── #
#  Wall Specifications  (Phase 2)
# ──────────────────────────────────────────────────────────────────────── #
# Boundary walls around the arena: (x, z, width, height, depth)

WALL_SPECS = [
    ( 0,  -30, 60, 4, 0.3),   # north wall
    ( 0,   30, 60, 4, 0.3),   # south wall
    (-30,  0,  0.3, 4, 60),   # west wall
    ( 30,  0,  0.3, 4, 60),   # east wall
]


# ──────────────────────────────────────────────────────────────────────── #
#  Platform Specifications  (Phase 2)
# ──────────────────────────────────────────────────────────────────────── #
# Elevated platforms: (x, z, width, height_above_ground, depth)

PLATFORM_SPECS = [
    (-16, -16, 6, 1.5, 6),
    ( 16, -16, 6, 1.5, 6),
    (-16,  16, 6, 1.5, 6),
    ( 16,  16, 6, 1.5, 6),
    ( 0,    0, 8, 0.5, 8),   # central low platform
]


# ──────────────────────────────────────────────────────────────────────── #
#  Terminal / Interactable Specifications  (Phase 2 → expanded Phase 3)
# ──────────────────────────────────────────────────────────────────────── #
# Cyber terminals: (x, z, label, security_level)
# security_level determines how many keys the hack sequence requires:
#   1 → 4 keys,  2 → 5 keys,  3 → 6 keys

TERMINAL_SPECS = [
    ( 6,  -6,  "Access Node Alpha",    1),
    (-6,   6,  "Access Node Beta",     1),
    ( 0,  -14, "Data Terminal Gamma",  2),
    ( 12,  0,  "Relay Point Delta",    3),
]


# ──────────────────────────────────────────────────────────────────────── #
#  Lighting Settings
# ──────────────────────────────────────────────────────────────────────── #

# Ambient light colour — tinted blue for night‑time cyberpunk mood
AMBIENT_COLOR = (30, 30, 50)

# Directional "sun" light colour — cold blue‑grey
SUN_COLOR     = (60, 60, 100)

# Sun rotation angles (pitch, yaw, roll)
SUN_ROTATION  = (45, -45, 0)


# ──────────────────────────────────────────────────────────────────────── #
#  HUD Defaults  (Phase 2)
# ──────────────────────────────────────────────────────────────────────── #

# Starting player energy percentage (0–100)
HUD_DEFAULT_ENERGY = 100

# Starting access level label
HUD_DEFAULT_ACCESS = "LEVEL 1"

# Starting zone name
HUD_DEFAULT_ZONE = "SECTOR 7-G"


# ──────────────────────────────────────────────────────────────────────── #
#  Menu Particle Settings  (Phase 2)
# ──────────────────────────────────────────────────────────────────────── #

# Number of floating background particles on the main menu
MENU_PARTICLE_COUNT = 30

# Speed range (min, max) for drifting particles
MENU_PARTICLE_SPEED = (0.2, 0.8)


# ──────────────────────────────────────────────────────────────────────── #
#  Hacking System Settings  (Phase 3)
# ──────────────────────────────────────────────────────────────────────── #

# Keys the player can be asked to press during a hack sequence
HACK_KEY_POOL = ['w', 'a', 's', 'd', 'q', 'r', 'f']

# Base sequence length for security level 1 (level N adds N‑1 extra keys)
HACK_BASE_LENGTH = 4

# How many seconds the player has to complete the entire sequence
HACK_TIME_LIMIT = 12.0

# Penalty: how many correct keys are lost on a wrong key press
HACK_WRONG_PENALTY = 1

# Colours for the hacking panel backdrop
HACK_PANEL_BG     = (8, 5, 20)
HACK_PANEL_BORDER = NEON_CYAN

# Terminal glow colours per state
TERMINAL_COLOR_LOCKED   = NEON_GREEN       # default — hackable
TERMINAL_COLOR_ACTIVE   = (255, 200, 0)    # yellow — hack in progress
TERMINAL_COLOR_BREACHED = NEON_CYAN        # cyan — already hacked


# ──────────────────────────────────────────────────────────────────────── #
#  Metadata
# ──────────────────────────────────────────────────────────────────────── #

# Project metadata used by documentation generators and splash screens
PROJECT_NAME    = "AIM: Cyber Reign"
PROJECT_AUTHOR  = "Aimtech"
PROJECT_VERSION = "0.3.0"
PROJECT_PHASE   = "Phase 3 — Hacking Core System"
