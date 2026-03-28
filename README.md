# AIM: Cyber Reign

> A futuristic cyberpunk 3D game built with Python and the Ursina engine.

**Author:** Aimtech
**Phase:** Phase 2 — Visual Upgrade & Interaction
**Version:** 0.2.0

---

## 🎮 Game Description

**AIM: Cyber Reign** is a dark, neon-drenched cyberpunk game set in a
futuristic digital cityscape. The player navigates a glowing grid-lined
world filled with towering neon structures, pillars, elevated platforms,
and interactive cyber terminals.

### Current Features (Phase 2)

- **Animated main menu** with floating neon particles and Settings button
- **Settings panel** with volume, sensitivity, and quality controls
- **First-person movement** with WASD, mouse look, jumping, and **sprinting** (Left Shift)
- **Expanded 3D world** — buildings, neon pillars, boundary walls, elevated platforms
- **Interaction system** — walk up to cyber terminals and press E to access them
- **Expanded HUD** — energy bar, access level, zone name, sprint indicator
- **Scene system** — menu ↔ settings ↔ game transitions
- **Docker support** for containerised execution

---

## 🛠 Tools & Technologies

| Tool / Library | Purpose |
|---|---|
| **Python 3.11+** | Core language |
| **Ursina** | 3D game engine (built on Panda3D) |
| **Docker** | Containerisation for reproducible builds |

---

## 📁 Project Structure

```
cyberpunk_game/
├── main.py                # Entry point
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container recipe
├── .dockerignore
├── README.md
├── GAME_STRUCTURE.md      # Architecture docs
├── AI_PROGRESS.md         # AI tracking log
├── src/
│   ├── __init__.py
│   ├── config.py          # All constants
│   ├── menu.py            # Animated main menu
│   ├── settings.py        # Settings panel
│   ├── player.py          # FPS controller + sprint
│   ├── environment.py     # Full 3D world
│   ├── ui.py              # Expanded HUD
│   ├── scenes.py          # Scene manager
│   └── interaction.py     # Interaction framework
├── assets/{textures,models,audio,fonts}/
└── docs/phase_notes.md
```

---

## 🚀 Setup & Run

### Prerequisites

- Python 3.11 or newer
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
python main.py
```

### Controls

| Key | Action |
|---|---|
| W / A / S / D | Move |
| Mouse | Look around |
| Space | Jump |
| Left Shift | Sprint |
| E | Interact with terminals |
| ESC | Return to menu |

---

## 🐳 Docker

### Build the Image

```bash
docker build -t aim-cyber-reign .
```

### Run the Container

```bash
# Linux / WSL with X11:
xhost +local:docker
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix aim-cyber-reign

# Windows with VcXsrv:
docker run -e DISPLAY=host.docker.internal:0 aim-cyber-reign
```

---

## 🗺 Roadmap

| Phase | Status | Focus |
|---|---|---|
| **1 — Foundation** | ✅ | Structure, menu, player, environment, HUD, Docker |
| **2 — Visual Upgrade** | ✅ | Animated menu, settings, sprint, expanded world, interaction, HUD |
| 3 — Combat | 🔲 | Weapons, shooting, hit detection |
| 4 — Enemies | 🔲 | AI opponents, patrol, combat AI |
| 5 — Missions | 🔲 | Objectives, quests, hacking mini-games |
| 6 — Inventory | 🔲 | Items, pickups, equipment |
| 7 — Audio | 🔲 | SFX, ambient music, UI audio |
| 8 — Polish | 🔲 | Particles, post-processing, save/load |

---

## 📝 License

This project is proprietary. © Aimtech. All rights reserved.
