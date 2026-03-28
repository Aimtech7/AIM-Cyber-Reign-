# GAME_STRUCTURE.md — AIM: Cyber Reign

> Complete project documentation and architecture reference.

---

## 🎮 Game Information

| Field | Value |
|---|---|
| **Name** | AIM: Cyber Reign |
| **Author** | Aimtech |
| **Genre** | Cyberpunk / Sci-Fi / First-Person Exploration & Hacking |
| **Concept** | A dark, neon-lit futuristic world where the player navigates a digital cityscape, hacks cyber terminals via a key-sequence mini-game, and progresses through access levels. |
| **Engine** | Ursina (Python, built on Panda3D) |
| **Language** | Python 3.11+ |
| **Container** | Docker (python:3.11-slim base) |
| **Current Phase** | Phase 3 — Hacking Core System |

---

## 📁 Folder Structure

```
cyberpunk_game/
├── main.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
├── GAME_STRUCTURE.md       ← you are here
├── AI_PROGRESS.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── menu.py
│   ├── player.py
│   ├── environment.py
│   ├── ui.py
│   ├── scenes.py
│   ├── settings.py
│   ├── interaction.py
│   ├── game_state.py        ← new in Phase 3
│   └── hacking.py           ← new in Phase 3
├── assets/
│   ├── textures/
│   ├── models/
│   ├── audio/
│   └── fonts/
└── docs/
    └── phase_notes.md
```

---

## 📄 File Purposes

### Root Files

| File | Purpose |
|---|---|
| `main.py` | Entry point — initialises Ursina, creates SceneManager, starts event loop |
| `requirements.txt` | Python dependencies (`ursina`) |
| `Dockerfile` | Container build — OS deps + Python deps, runs main.py |
| `.dockerignore` | Excludes caches, venvs, IDE files |
| `README.md` | User-facing overview, setup, run instructions |
| `GAME_STRUCTURE.md` | This file — architecture documentation |
| `AI_PROGRESS.md` | Step-by-step AI development log |

### src/ Package

| File | Purpose |
|---|---|
| `__init__.py` | Package init; project metadata |
| `config.py` | All constants: window, colours, player, sprint, interaction, environment, hacking, HUD, metadata |
| `menu.py` | `MainMenu` — animated particles, title, Start/Settings/Exit buttons |
| `player.py` | `PlayerController` — WASD + mouse look + sprint (Left Shift) |
| `environment.py` | `GameEnvironment` — floor, buildings, pillars, walls, platforms, hackable terminals with state colours |
| `ui.py` | `HUD` — system status, energy, access level, zone, sprint indicator, breached node count |
| `scenes.py` | `SceneManager` — menu/settings/game transitions, hacking flow orchestration |
| `settings.py` | `SettingsMenu` — volume, sensitivity, quality (visual placeholders) |
| `interaction.py` | `Interactable` + `InteractionSystem` — proximity, prompts, pause support |
| `game_state.py` | `GameState` — tracks breached terminals, access level progression, stats API |
| `hacking.py` | `HackingPanel` — key-sequence mini-game, timer, success/failure callbacks |

---

## 🎮 Game Systems

### Scene System
`SceneManager` handles three scenes: **Menu**, **Settings**, **Game**. State dictionary tracks live objects; `_destroy_keys()` cleans up on transitions.

### Hacking System (Phase 3)
Complete gameplay loop:
1. Player approaches a terminal → "Press E to hack [name]"
2. Press E → Player freezes, mouse unlocks, hacking panel opens
3. Panel shows terminal name, security level, and a random key sequence
4. Player presses keys in order; correct → highlight; wrong → penalty roll-back
5. Timer counts down (12s); bar changes colour (cyan → yellow → magenta)
6. **Success** → terminal marked breached (cyan glow), access level may increase, prompt becomes "BREACHED"
7. **Failure / timeout** → terminal reverts to locked (green glow), can retry
8. **ESC** → abort without penalty
9. Player unfreezes, interaction system resumes

### Terminal States
| State | Glow Colour | Cause |
|---|---|---|
| Locked | Green | Default — hackable |
| Active | Yellow | Hack in progress |
| Breached | Cyan | Successfully hacked |

### Game State Tracking
`GameState` tracks:
- `total_terminals` — count from config
- `breached_labels` — set of hacked terminal names
- `access_level` — starts at 1, increases by 1 every 2 breaches

### Sprint System
`PlayerController.update()` checks `held_keys['left shift']` each frame. Speed multiplies by 1.8× while held.

### Interaction System
Proximity-based with pause support. During hacking, `paused=True` freezes all proximity checks and input handling. `update_prompt()` permanently marks breached terminals.

### HUD System
Two columns: left (status, energy, access level, breached count) and right (zone, sprint, target). Reads `GameState.get_stats()` each frame for live updates.

---

## 🏃 How to Run

### Locally
```bash
pip install -r requirements.txt
python main.py
```

### Controls
| Key | Action |
|---|---|
| W / A / S / D | Move |
| Mouse | Look around |
| Space | Jump |
| Left Shift | Sprint |
| E | Interact / Hack terminals |
| ESC | Return to menu (or abort hack) |

### In Docker
```bash
docker build -t aim-cyber-reign .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix aim-cyber-reign
```

---

## 🗺 Phase Roadmap

| Phase | Status | Focus |
|---|---|---|
| **1 — Foundation** | ✅ | Structure, menu, player, environment, HUD, Docker |
| **2 — Visual Upgrade** | ✅ | Animated menu, settings, sprint, expanded world, interaction |
| **3 — Hacking Core** | ✅ | Key-sequence mini-game, terminal states, game state tracking |
| 4 — Enemy AI & Combat | 🔲 | Opponents, weapons, damage |
| 5 — Missions | 🔲 | Objectives, quests |
| 6 — Inventory | 🔲 | Items, equipment |
| 7 — Audio | 🔲 | SFX, music |
| 8 — Polish | 🔲 | Particles, save/load |

---

## 📐 Coding Conventions

1. One class per file — single responsibility.
2. Config-driven — all tunables in `config.py`.
3. Comment everything — inline + docstrings.
4. Cleanup pattern — `destroy()` on every scene object.
5. Snake_case variables, PascalCase classes.

---

## 🤖 AI Collaboration Rules

1. Update `AI_PROGRESS.md` after every major step.
2. Never leave broken imports.
3. `py_compile` all files before marking complete.
4. Use `config.py` for new constants.
5. Keep `main.py` minimal.
6. Write beginner-friendly comments.

---

© Aimtech — AIM: Cyber Reign
