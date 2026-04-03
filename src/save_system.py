"""
save_system.py — Save / Load Module (Phase 8)
================================================
Project : AIM: Cyber Reign
Author  : Aimtech
Purpose : JSON-based game state persistence.  Saves and loads:
            • Player position and health
            • Breached terminals
            • Inventory contents
            • Mission progress
            • Alert level

How it connects:
    SceneManager calls save_game() on key events (terminal breach,
    mission complete) and load_game() when the player chooses Continue.
    The save file lives in SAVE_DIR (default: ./saves/) for Docker
    compatibility.

Design notes:
    • JSON format for human-readability and easy debugging.
    • One save slot — overwritten on each save.
    • Gracefully handles missing/corrupt save files.
"""

# ── Standard library ───────────────────────────────────────────────────── #
import json     # JSON serialisation
import os       # file and directory operations

# ── Project imports ────────────────────────────────────────────────────── #
from src.config import SAVE_DIR, SAVE_FILE_NAME


# ══════════════════════════════════════════════════════════════════════════ #
#  Public API
# ══════════════════════════════════════════════════════════════════════════ #

def get_save_path():
    """
    Return the full path to the save file, creating the directory
    if it doesn't exist.

    Returns:
        str — absolute path to savegame.json
    """
    os.makedirs(SAVE_DIR, exist_ok=True)
    return os.path.join(SAVE_DIR, SAVE_FILE_NAME)


def save_exists():
    """
    Check whether a save file exists on disk.

    Returns:
        bool — True if a save file is present
    """
    return os.path.isfile(get_save_path())


def save_game(game_state, player, inventory, mission_manager):
    """
    Serialise current game state to a JSON file.

    Args:
        game_state      : GameState      — health, alert, breached nodes
        player          : PlayerController — position
        inventory       : Inventory      — item slots
        mission_manager : MissionManager — current objectives

    Returns:
        bool — True on success, False on failure
    """
    try:
        data = {}

        # ── Player position ────────────────────────────────────────── #
        if player and player.controller:
            pos = player.controller.position
            data['player_position'] = [pos.x, pos.y, pos.z]
        else:
            data['player_position'] = [0, 1, 0]   # fallback

        # ── Game state ─────────────────────────────────────────────── #
        if game_state:
            data['health']            = game_state.health
            data['alert_level']       = game_state.alert_level
            data['alert_accumulator'] = game_state.alert_accumulator
            data['breached']          = list(game_state.breached_terminals)
            data['access_level']      = game_state.access_level
        else:
            data['health']       = 100
            data['alert_level']  = 0
            data['breached']     = []
            data['access_level'] = 1

        # ── Inventory ──────────────────────────────────────────────── #
        if inventory:
            inv_data = []
            for item_type, count in inventory.slots.items():
                inv_data.append({'type': item_type, 'count': count})
            data['inventory'] = inv_data
        else:
            data['inventory'] = []

        # ── Mission progress ───────────────────────────────────────── #
        if mission_manager and mission_manager.current_mission:
            mission = mission_manager.current_mission
            data['mission'] = {
                'name':  mission.name,
                'state': mission.state,
                'current_objective_idx': mission_manager._obj_index,
            }
        else:
            data['mission'] = None

        # ── Write to disk ──────────────────────────────────────────── #
        path = get_save_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f'[SaveSystem] ERROR saving game: {e}')
        return False


def load_game():
    """
    Read and parse the save file from disk.

    Returns:
        dict or None — parsed save data, or None if no save or corrupt
    """
    path = get_save_path()

    if not os.path.isfile(path):
        return None   # no save file

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    except (json.JSONDecodeError, OSError) as e:
        print(f'[SaveSystem] WARNING: corrupt save file — {e}')
        return None


def delete_save():
    """
    Remove the save file from disk.

    Returns:
        bool — True if deleted, False if not found or error
    """
    path = get_save_path()
    try:
        if os.path.isfile(path):
            os.remove(path)
            return True
        return False
    except OSError as e:
        print(f'[SaveSystem] ERROR deleting save: {e}')
        return False


def apply_save_data(data, game_state, player, inventory, mission_manager):
    """
    Apply loaded save data to live game objects.

    This is called after start_game() to restore the player to their
    saved position and state.

    Args:
        data            : dict            — parsed save data from load_game()
        game_state      : GameState       — live game state
        player          : PlayerController — live player
        inventory       : Inventory       — live inventory
        mission_manager : MissionManager  — live mission manager
    """
    if data is None:
        return   # nothing to apply

    # ── Restore player position ────────────────────────────────────── #
    if player and player.controller and 'player_position' in data:
        pos = data['player_position']
        player.controller.position = (pos[0], pos[1], pos[2])

    # ── Restore health and alert ───────────────────────────────────── #
    if game_state:
        game_state.health            = data.get('health', 100)
        game_state.alert_level       = data.get('alert_level', 0)
        game_state.alert_accumulator = data.get('alert_accumulator', 0.0)
        game_state.access_level      = data.get('access_level', 1)

        # Restore breached terminals
        for label in data.get('breached', []):
            game_state.breach_terminal(label)

    # ── Restore inventory ──────────────────────────────────────────── #
    if inventory and 'inventory' in data:
        # Import here to avoid circular imports
        from src.items import create_item
        inventory.slots.clear()
        for entry in data['inventory']:
            item_type = entry.get('type')
            count     = entry.get('count', 1)
            if item_type:
                inventory.slots[item_type] = count

    # ── Restore mission progress ───────────────────────────────────── #
    if mission_manager and data.get('mission'):
        m_data = data['mission']
        if mission_manager.current_mission:
            mission_manager.current_mission.state = m_data.get(
                'state', 'active'
            )
            obj_idx = m_data.get('current_objective_idx', 0)
            mission_manager._obj_index = min(
                obj_idx,
                len(mission_manager.current_mission.objectives) - 1,
            )
