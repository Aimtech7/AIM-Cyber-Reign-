# AIM: Cyber Reign

> A futuristic cyberpunk 3D game built with Python and the Ursina engine.

**Author:** Aimtech
**Phase:** Phase 3 — Hacking Core System
**Version:** 0.3.0

---

## 🎮 Game Description

**AIM: Cyber Reign** is a dark, neon-drenched cyberpunk game set in a
futuristic digital cityscape. The player navigates a glowing grid-lined
world, hacks cyber terminals via a timed key-sequence challenge, and
progresses through security access levels.

### Current Features (Phase 3)

- **Animated main menu** with floating particles and Settings button
- **Settings panel** with volume, sensitivity, and quality controls
- **First-person movement** with WASD, mouse look, jumping, and sprint
- **Expanded 3D world** — buildings, pillars, walls, platforms, terminals
- **Hacking mini-game** — timed key-sequence challenge per terminal
- **Terminal states** — locked (green) → active (yellow) → breached (cyan)
- **Game state tracking** — breached count, access level progression
- **Expanded HUD** — energy, access level, zone, sprint, breached nodes
- **Scene system** — menu ↔ settings ↔ game transitions
- **Docker support** for containerised execution

---

## 📁 Project Structure

```
cyberpunk_game/
├── main.py                # Entry point
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md, GAME_STRUCTURE.md, AI_PROGRESS.md
├── src/
│   ├── __init__.py, config.py
│   ├── menu.py, settings.py
│   ├── player.py, environment.py
│   ├── ui.py, scenes.py
│   ├── interaction.py
│   ├── game_state.py       # Phase 3
│   └── hacking.py          # Phase 3
├── assets/{textures,models,audio,fonts}/
└── docs/phase_notes.md
```

---

## 🚀 Setup & Run

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

---

## 🐳 Docker

```bash
docker build -t aim-cyber-reign .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix aim-cyber-reign
```

---

## 🗺 Roadmap

| Phase | Status | Focus |
|---|---|---|
| **1 — Foundation** | ✅ | Structure, menu, player, environment, HUD, Docker |
| **2 — Visual Upgrade** | ✅ | Animated menu, settings, sprint, expanded world |
| **3 — Hacking Core** | ✅ | Mini-game, terminal states, game state tracking |
| 4 — Enemy AI & Combat | 🔲 | Opponents, weapons, damage |
| 5 — Missions | 🔲 | Objectives, quests |
| 6 — Inventory | 🔲 | Items, equipment |
| 7 — Audio | 🔲 | SFX, music |
| 8 — Polish | 🔲 | VFX, save/load |

---

## 📝 License

This project is proprietary. © Aimtech. All rights reserved.
