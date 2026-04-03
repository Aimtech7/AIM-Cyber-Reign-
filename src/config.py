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

Phase 8 changes:
    • Added visual effects constants (glow pulse, particles)
    • Added camera polish constants (head bob, camera shake)
    • Added save/load configuration
    • Rebalanced gameplay values (drones, hacking, health, alerts)
    • Updated audio volume levels and added new SFX constants
    • Bumped version to 0.8.0
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
HACK_TIME_LIMIT = 14.0       # Phase 8 — increased from 12.0 for more breathing room

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
#  Security Drone Settings  (Phase 4)
# ──────────────────────────────────────────────────────────────────────── #

# Spawn positions for security drones: (x, y, z)
DRONE_SPECS = [
    ( 10, 3, -10),    # near Access Node Alpha
    (-10, 3,  10),    # near Access Node Beta
    ( 20, 4,  20),    # far corner patrol
    (-15, 3, -20),    # near Data Terminal Gamma
]

# Patrol radius — how far a drone wanders from its spawn point
DRONE_PATROL_RADIUS = 8

# Detection radius — player within this range triggers suspicion / alert
DRONE_DETECT_RADIUS = 10     # Phase 8 — reduced from 12 for fairer gameplay

# Close-attack radius — player within this range takes damage
DRONE_DAMAGE_RADIUS = 3.5

# Movement speeds (world units per second)
DRONE_PATROL_SPEED = 2.0     # idle wander speed
DRONE_CHASE_SPEED  = 4.0     # Phase 8 — reduced from 4.5 for fairer gameplay

# Hover bob — vertical oscillation while patrolling
DRONE_BOB_SPEED  = 2.0       # oscillations per second
DRONE_BOB_AMOUNT = 0.3       # amplitude in world units

# Time a drone stays alert after losing sight of the player (seconds)
DRONE_ALERT_TIMEOUT = 6.0

# Rotation speed when facing the player (degrees per second)
DRONE_TURN_SPEED = 180

# Damage the drone inflicts per second when within damage radius
DRONE_DAMAGE_PER_SEC = 6     # Phase 8 — reduced from 8 for fairer gameplay

# Drone colours per state
DRONE_COLOR_IDLE       = NEON_CYAN
DRONE_COLOR_SUSPICIOUS = NEON_YELLOW
DRONE_COLOR_ALERT      = NEON_MAGENTA


# ──────────────────────────────────────────────────────────────────────── #
#  Alert System Settings  (Phase 4)
# ──────────────────────────────────────────────────────────────────────── #

# Alert levels: 0 = CALM, 1 = SUSPICIOUS, 2 = ALERT
ALERT_LEVEL_CALM       = 0
ALERT_LEVEL_SUSPICIOUS = 1
ALERT_LEVEL_ALERT      = 2

# How many seconds before the global alert decays by one level
ALERT_DECAY_TIME = 15.0      # Phase 8 — reduced from 20.0 for faster cooldown

# Alert increase when a hack fails (added to alert accumulator)
ALERT_ON_HACK_FAIL = 1.0

# Alert increase when a hack succeeds (proportional to security level)
ALERT_ON_HACK_SUCCESS_PER_LEVEL = 0.3

# Alert labels for HUD display
ALERT_LABELS = {0: 'CALM', 1: 'SUSPICIOUS', 2: 'ALERT'}

# Alert HUD colours
ALERT_COLORS = {
    0: NEON_GREEN,
    1: NEON_YELLOW,
    2: NEON_MAGENTA,
}


# ──────────────────────────────────────────────────────────────────────── #
#  Player Health / Shield Settings  (Phase 4)
# ──────────────────────────────────────────────────────────────────────── #

# Maximum player health points
PLAYER_MAX_HEALTH = 100

# Health regeneration rate when not taking damage (HP per second)
PLAYER_HEALTH_REGEN = 3.0    # Phase 8 — increased from 2.0 for faster recovery

# Seconds after last damage before regen starts
PLAYER_REGEN_DELAY = 3.0     # Phase 8 — reduced from 4.0 for shorter wait


# ──────────────────────────────────────────────────────────────────────── #
#  Mission System Settings  (Phase 5)
# ──────────────────────────────────────────────────────────────────────── #

# Extraction zone position and radius (world coords)
EXTRACTION_ZONE_POS    = (-20, 0, -20)    # far corner of the map
EXTRACTION_ZONE_RADIUS = 4.0              # player must be within this
EXTRACTION_ZONE_COLOR  = (0, 255, 180)    # teal‑green glow

# Highlight colour for mission‑required terminals (distinct from normal)
MISSION_TARGET_COLOR   = (255, 100, 0)    # orange glow on target terminals

# Mission feedback message display time (seconds)
MISSION_MSG_DURATION   = 4.0

# Labels of terminals required for "Sector Breach" mission
MISSION_REQUIRED_TERMINALS = ['Access Node Alpha', 'Data Terminal Gamma']


# ──────────────────────────────────────────────────────────────────────── #
#  Inventory & Equipment Settings  (Phase 6)
# ──────────────────────────────────────────────────────────────────────── #

# Maximum number of items the player can carry
INVENTORY_MAX_SLOTS = 8

# Distance at which items are automatically picked up (world units)
ITEM_PICKUP_DISTANCE = 3.0

# Cooldown between using equipped items (seconds)
EQUIPMENT_USE_COOLDOWN = 2.0

# Keybinds for the two equipment slots
EQUIP_SLOT_Q = 'q'   # first equipment slot
EQUIP_SLOT_R = 'r'   # second equipment slot (only outside hacking)

# Key to toggle the inventory panel overlay
INVENTORY_TOGGLE_KEY = 'tab'

# ── Item Statistics ────────────────────────────────────────────────────── #

# Energy Cell — restores this many HP when used
ITEM_ENERGY_CELL_HEAL = 40   # Phase 8 — increased from 30 for more impactful healing

# Hack Booster — adds this many seconds to hacking timer
ITEM_HACK_BOOSTER_TIME = 5.0

# EMP Pulse — disables drones within this radius (world units)
ITEM_EMP_RADIUS = 15.0

# EMP Pulse — duration of the disable effect (seconds)
ITEM_EMP_DURATION = 5.0

# ── Item Pickup Spawn Points ──────────────────────────────────────────── #
# Each tuple is (x, z, item_type)
# item_type: 'energy_cell', 'hack_booster', 'emp_pulse'

ITEM_PICKUP_SPECS = [
    ( 10,   5,  'energy_cell'),      # near Alpha terminal
    (-10,  -5,  'energy_cell'),      # near Beta terminal
    (  0,  -20, 'hack_booster'),     # near Gamma terminal
    ( 18,   0,  'hack_booster'),     # near Delta terminal
    (-15,  15,  'emp_pulse'),        # mid‑map west
    ( 20, -15,  'emp_pulse'),        # far east corner
]

# Glow colour for item pickups in the world (bright orange)
ITEM_PICKUP_COLOR = (255, 160, 0)

# Inventory panel background colour (dark overlay)
INVENTORY_PANEL_BG = (8, 5, 20)

# ──────────────────────────────────────────────────────────────────────── #
#  Audio Settings  (Phase 7)
# ──────────────────────────────────────────────────────────────────────── #

# Base directory for all audio files (relative to project root)
AUDIO_DIR = 'assets/audio'

# Volume channels (0.0 = silent, 1.0 = max)
AUDIO_MASTER_VOLUME = 0.8    # Phase 8 — raised from 0.7 for stronger presence
AUDIO_MUSIC_VOLUME  = 0.35   # Phase 8 — lowered from 0.4 to not overpower SFX
AUDIO_SFX_VOLUME    = 0.65   # Phase 8 — raised from 0.6 for clearer feedback

# ── Music tracks ───────────────────────────────────────────────────────── #
MUSIC_MENU_LOOP     = 'menu_loop'       # main menu background
MUSIC_CYBER_AMBIENT = 'cyber_ambient'   # in‑game ambient
MUSIC_TENSE_LOOP    = 'tense_loop'      # hacking / high‑security

# ── UI sound effects ──────────────────────────────────────────────────── #
SFX_CLICK            = 'click'           # menu button click
SFX_SLIDER           = 'slider'          # settings slider move
SFX_INVENTORY_TOGGLE = 'inventory_toggle'  # TAB open/close
SFX_PICKUP           = 'pickup'          # item picked up

# ── Hacking sound effects ─────────────────────────────────────────────── #
SFX_TERMINAL_ON  = 'terminal_on'   # terminal interaction starts
SFX_KEY_PRESS    = 'key_press'     # correct key in sequence
SFX_HACK_SUCCESS = 'hack_success'  # breach complete
SFX_HACK_FAIL    = 'hack_fail'     # wrong key or timeout

# ── Drone sound effects ───────────────────────────────────────────────── #
SFX_DRONE_ALERT    = 'drone_alert'     # IDLE → SUSPICIOUS
SFX_DRONE_CHASE    = 'drone_chase'     # SUSPICIOUS → ALERT
SFX_DRONE_HIT      = 'drone_hit'       # drone damages player
SFX_DRONE_DISABLED = 'drone_disabled'  # EMP hit

# ── Player sound effects ──────────────────────────────────────────────── #
SFX_FOOTSTEP_1 = 'footstep1'   # walk step variant 1
SFX_FOOTSTEP_2 = 'footstep2'   # walk step variant 2
SFX_JUMP       = 'jump'        # player jumps
SFX_LAND       = 'land'        # player lands

# ── Mission sound effects ─────────────────────────────────────────────── #
SFX_EXTRACT         = 'extract'          # extraction zone reached
SFX_MISSION_COMPLETE = 'mission_complete'  # mission success
SFX_MISSION_FAIL    = 'mission_fail'     # mission failure

# ── Footstep timing ───────────────────────────────────────────────────── #
FOOTSTEP_WALK_INTERVAL   = 0.5   # seconds between walk footsteps
FOOTSTEP_SPRINT_INTERVAL = 0.3   # seconds between sprint footsteps


# ──────────────────────────────────────────────────────────────────────── #
#  Phase 8 — Visual Effects Settings
# ──────────────────────────────────────────────────────────────────────── #

# GlowPulse effect — pulsing neon ring on terminals, extraction zone, etc.
GLOW_PULSE_SPEED     = 2.5     # slightly faster pulsing
GLOW_PULSE_MIN_SCALE = 0.90    # minimum scale factor during pulse
GLOW_PULSE_MAX_SCALE = 1.30    # much larger maximum scale factor
GLOW_PULSE_MIN_ALPHA = 50      # minimum alpha (0–255) during pulse
GLOW_PULSE_MAX_ALPHA = 240     # much brighter maximum alpha

# ParticleEmitter budgets — pumped up for better visual impact
PARTICLE_HACK_COUNT    = 15    # floating data glyphs during hacking
PARTICLE_EMP_COUNT     = 40    # massive expanding ring fragments on EMP
PARTICLE_ALERT_COUNT   = 15    # red sparks when drone goes ALERT
PARTICLE_EXTRACT_COUNT = 30    # upward teal sparkles at extraction zone
PARTICLE_LIFETIME      = 2.0   # seconds before a particle is recycled


# ──────────────────────────────────────────────────────────────────────── #
#  Phase 8 — Camera Polish Settings
# ──────────────────────────────────────────────────────────────────────── #

# Head bob — subtle vertical oscillation while walking
HEAD_BOB_SPEED            = 9.0    # oscillation frequency
HEAD_BOB_AMOUNT           = 0.08   # heavier vertical amplitude
HEAD_BOB_SPRINT_MULTIPLIER = 1.6   # intense sprint bobbing

# Camera shake — triggered on damage, EMP, etc.
CAMERA_SHAKE_DAMAGE_INTENSITY  = 0.3    # harsh shake strength on player hit
CAMERA_SHAKE_DAMAGE_DURATION   = 0.4    # shake duration (seconds)
CAMERA_SHAKE_EMP_INTENSITY     = 0.6    # massive shake for EMP blast
CAMERA_SHAKE_EMP_DURATION      = 0.7    # EMP shake duration
CAMERA_SHAKE_HACK_FAIL_INTENSITY = 0.15 # mild shake on wrong hack key
CAMERA_SHAKE_HACK_FAIL_DURATION  = 0.2  # wrong key shake duration

# Camera smoothing — lerp factor for mouselook (0=no smoothing, 1=instant)
CAMERA_SMOOTH_FACTOR = 0.85


# ──────────────────────────────────────────────────────────────────────── #
#  Phase 8 — Save / Load Settings
# ──────────────────────────────────────────────────────────────────────── #

# Save file path (relative to project root, Docker-compatible)
SAVE_DIR       = 'saves'
SAVE_FILE_NAME = 'savegame.json'


# ──────────────────────────────────────────────────────────────────────── #
#  Phase 8 — Additional SFX
# ──────────────────────────────────────────────────────────────────────── #

SFX_DAMAGE_HIT   = 'damage_hit'     # player takes damage
SFX_SAVE_GAME    = 'save_game'      # save confirmation beep
SFX_LOAD_GAME    = 'load_game'      # load confirmation beep


# ──────────────────────────────────────────────────────────────────────── #
#  Phase 8 — UI Animation Settings
# ──────────────────────────────────────────────────────────────────────── #

# Health bar lerp speed (how fast the bar catches up to real value)
HEALTH_BAR_LERP_SPEED  = 4.0    # units per second

# Damage vignette — red edge overlay on taking damage
VIGNETTE_FADE_SPEED    = 1.5    # slower fade so the pain lingers more
VIGNETTE_MAX_ALPHA     = 0.8    # much darker and aggressive on hit

# Alert flash — brief border flash when alert level changes
ALERT_FLASH_DURATION   = 0.3    # seconds the flash is visible

# Message slide-in speed (UI units per second)
MESSAGE_SLIDE_SPEED    = 2.0


# ──────────────────────────────────────────────────────────────────────── #
#  Metadata
# ──────────────────────────────────────────────────────────────────────── #

# Project metadata used by documentation generators and splash screens
PROJECT_NAME    = "AIM: Cyber Reign"
PROJECT_AUTHOR  = "Aimtech"
PROJECT_VERSION = "0.8.0"
PROJECT_PHASE   = "Phase 8 — Polish & Final Touches"

