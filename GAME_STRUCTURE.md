# GAME_STRUCTURE.md — AIM: Cyber Reign

> Architecture reference — v0.7.0

---

## 📁 Structure

```
cyberpunk_game/
├── main.py
├── generate_placeholder_audio.py   ← Phase 7
├── src/
│   ├── __init__.py, config.py
│   ├── menu.py, settings.py, player.py
│   ├── environment.py, interaction.py
│   ├── ui.py, scenes.py
│   ├── game_state.py, hacking.py
│   ├── enemies.py         ← Phase 4
│   ├── missions.py        ← Phase 5
│   ├── items.py           ← Phase 6
│   ├── inventory.py       ← Phase 6
│   └── audio.py           ← Phase 7
├── assets/
│   ├── audio/             ← Phase 7 (22 .wav files)
│   ├── fonts/, textures/
├── docs/
└── Dockerfile, README.md, GAME_STRUCTURE.md, AI_PROGRESS.md
```

## 📄 File Purposes

| File | Purpose |
|---|---|
| `config.py` | All constants (~500 lines) |
| `menu.py` | Animated main menu (with click SFX) |
| `player.py` | FPS controller + sprint + footsteps/jump/land |
| `environment.py` | 3D world + terminals + extraction zone + item pickups |
| `interaction.py` | Proximity interaction + pause |
| `ui.py` | Full HUD: status, health, alert, mission, inventory, equipment |
| `scenes.py` | Scene transitions + hacking + drones + missions + inventory + audio |
| `settings.py` | Settings panel (volume slider wired to audio) |
| `game_state.py` | Breaches, health, alert, hack boost tracking |
| `hacking.py` | Key-sequence mini-game (with key/success/fail SFX) |
| `enemies.py` | SecurityDrone AI (with state-change + hit SFX) |
| `missions.py` | Mission, Objective, MissionManager |
| `items.py` | Item base class + 3 item types |
| `inventory.py` | Inventory, EquipmentManager, ItemPickup |
| `audio.py` | AudioManager — music, SFX, volume control |

---

## 🎮 Game Systems

### Audio System (Phase 7)
```
AudioManager created once in SceneManager
  → Menu scene → menu_loop music
  → Game scene → cyber_ambient music
  → Hacking  → tense_loop music + key/success/fail SFX
  → Drones   → alert / chase / hit / EMP SFX
  → Player   → footstep / jump / land SFX
  → UI       → click / inventory toggle / pickup SFX
  → Settings → volume slider → set_volume('master', ...)
```

### Inventory & Equipment (Phase 6)
```
Items spawn → auto-collect → TAB inventory → equip Q/R → use items
```

### Mission System (Phase 5)
```
SECTOR BREACH: hack 2 terminals → extract → MISSION COMPLETE
```

### Security (Phase 4)
Drones patrol → detect → chase → damage.  EMP disables drones.

### Hacking (Phase 3)
Terminal interaction → key-sequence challenge → breach/fail → state update.

---

## 🗺 Roadmap

| Phase | Status |
|---|---|
| 1–7 | ✅ |
| **8 — Polish** | 🔲 |

---
© Aimtech — AIM: Cyber Reign
