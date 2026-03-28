# GAME_STRUCTURE.md — AIM: Cyber Reign

> Complete project documentation and architecture reference.

---

## 🎮 Game Information

| Field | Value |
|---|---|
| **Name** | AIM: Cyber Reign |
| **Author** | Aimtech |
| **Genre** | Cyberpunk / Sci-Fi / First-Person Exploration |
| **Concept** | A dark, neon-lit futuristic world where the player navigates a digital cityscape, interacts with cyber terminals, and prepares for combat missions. |
| **Engine** | Ursina (Python, built on Panda3D) |
| **Language** | Python 3.11+ |
| **Container** | Docker (python:3.11-slim base) |
| **Current Phase** | Phase 2 — Visual Upgrade & Interaction |

---

## 🛠 Tools & Libraries

| Tool | Role |
|---|---|
| Python 3.11+ | Core programming language |
| Ursina | 3D game engine — rendering, physics, input, UI |
| Panda3D | Low-level 3D backend (wrapped by Ursina) |
| Docker | Application containerisation |
| pip | Python package manager |

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
│   ├── settings.py         ← new in Phase 2
│   └── interaction.py      ← new in Phase 2
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
| `requirements.txt` | Lists Python dependencies (currently: `ursina`) |
| `Dockerfile` | Container build recipe — installs OS deps + Python deps, runs main.py |
| `.dockerignore` | Excludes caches, venvs, and IDE files from Docker builds |
| `README.md` | User-facing project overview, setup guide, run instructions |
| `GAME_STRUCTURE.md` | This file — deep architecture documentation |
| `AI_PROGRESS.md` | Step-by-step tracking log for AI-assisted development |

### src/ Package

| File | Purpose |
|---|---|
| `__init__.py` | Marks `src/` as a Python package; exposes metadata |
| `config.py` | All global constants: window, colours, player, sprint, interaction, environment specs, HUD defaults, menu particles, metadata |
| `menu.py` | `MainMenu` class — animated particles, title, subtitle, version tag, Start/Settings/Exit buttons with neon hover effects |
| `player.py` | `PlayerController` (Entity subclass) — WASD + mouse look + Left Shift sprint with per-frame speed adjustment |
| `environment.py` | `GameEnvironment` class — floor grid, 12 buildings, 8 pillars, 4 walls, 5 platforms, 4 interactive terminals, lighting |
| `ui.py` | `HUD` (Entity subclass) — "SYSTEM ONLINE", energy bar, access level, zone name, dynamic sprint indicator |
| `scenes.py` | `SceneManager` class — orchestrates menu / settings / game transitions, wires interaction system to environment and player ref to HUD |
| `settings.py` | `SettingsMenu` class — volume slider, sensitivity slider, quality buttons (Low/Medium/High), Back button (visual placeholders) |
| `interaction.py` | `Interactable` data class + `InteractionSystem` (Entity subclass) — proximity detection, "Press E" prompts, timed feedback messages, callback support |

### assets/

Reserved directories for future game resources:

| Subdirectory | Planned Content |
|---|---|
| `textures/` | Diffuse maps, normal maps, UI sprites |
| `models/` | 3D meshes (.obj, .glb) |
| `audio/` | Sound effects, music tracks |
| `fonts/` | Custom TTF/OTF fonts |

### docs/

| File | Purpose |
|---|---|
| `phase_notes.md` | Design notes and decisions for each development phase |

---

## 🎮 Game Systems

### Scene System
The `SceneManager` handles three scenes: **Menu**, **Settings**, and **Game**. Each scene is a collection of objects created on entry and destroyed on exit. A state dictionary tracks live objects, and `_destroy_keys()` handles cleanup.

### Interaction System
`InteractionSystem` runs every frame, checking the distance between the player and all registered `Interactable` objects. When the player is within `INTERACT_DISTANCE`, a prompt appears. Pressing the interact key triggers a message and an optional callback. Currently used by cyber terminals; designed for doors, loot, NPCs in future.

### Sprint System
`PlayerController` subclasses `Entity` so its `update()` runs each frame. Holding Left Shift multiplies the base walk speed by `PLAYER_SPRINT_MULTIPLIER`. The `is_sprinting` flag is read by the HUD to display a sprint indicator.

### HUD System
The expanded HUD shows two columns: left (system status, energy bar, access level) and right (zone name, sprint indicator). The energy bar is a scaled quad. Values are currently config defaults; they will become dynamic when gameplay systems are implemented.

### Settings System
The settings panel shows sliders for volume and mouse sensitivity, plus quality preset buttons. Controls are visual placeholders; logic will be connected when the options system is implemented.

---

## 🏃 How to Run

### Locally

```bash
pip install -r requirements.txt
python main.py
```

### In Docker

```bash
docker build -t aim-cyber-reign .

# Linux / WSL with X11:
xhost +local:docker
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix aim-cyber-reign

# Windows with VcXsrv:
docker run -e DISPLAY=host.docker.internal:0 aim-cyber-reign
```

---

## 🗺 Phase Roadmap

| Phase | Status | Focus |
|---|---|---|
| **1 — Foundation** | ✅ Complete | Structure, menu, player, environment, HUD, Docker, docs |
| **2 — Visual Upgrade & Interaction** | ✅ Complete | Animated menu, settings, sprint, expanded world, interaction system, HUD expansion |
| 3 — Combat | 🔲 Planned | Weapons, shooting, hit detection |
| 4 — Enemies | 🔲 Planned | AI opponents, patrol, combat AI |
| 5 — Missions | 🔲 Planned | Objectives, quests, hacking mini-games |
| 6 — Inventory | 🔲 Planned | Items, pickups, equipment |
| 7 — Audio | 🔲 Planned | SFX, ambient music, UI audio |
| 8 — Polish | 🔲 Planned | Particles, post-processing, save/load |

---

## 📐 Coding Conventions

1. **One class per file** — each module owns a single responsibility.
2. **Config-driven** — no magic numbers; all tunables live in `config.py`.
3. **Comment everything** — every meaningful line has an inline comment; every function and class has a docstring.
4. **Cleanup pattern** — every scene object class exposes a `destroy()` method that removes all its entities.
5. **Imports at the top** — standard lib → engine → project, separated by blank lines.
6. **Snake_case** for variables and functions, **PascalCase** for classes.

---

## 🤖 AI Collaboration Rules

1. After every major step, update `AI_PROGRESS.md` with what was done.
2. Never leave placeholder or broken imports.
3. Always check that new code compiles (`py_compile`) before marking a step complete.
4. Follow the file layout described above — do not create files outside this structure.
5. Use `config.py` for any new constants; do not hard-code values in logic files.
6. Keep `main.py` minimal — all logic goes into `src/` modules.
7. Write beginner-friendly comments on every new line of code.

---

© Aimtech — AIM: Cyber Reign
