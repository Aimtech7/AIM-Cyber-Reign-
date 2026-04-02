# AIM: Cyber Reign

> Cyberpunk 3D game — Python + Ursina

**Author:** Aimtech | **Version:** 0.7.0 | **Phase 7 — Audio System**

---

## 🎮 Features

- First-person movement (WASD, sprint, jump) with footstep audio
- Cyberpunk 3D world (buildings, pillars, walls, platforms, terminals)
- Hacking mini-game with key-press and success/fail sounds
- Security drones with 3-state AI, alert sounds, and EMP interactions
- Player health with regen
- Mission system — "SECTOR BREACH": breach 2 targets + reach extraction
- Win/lose conditions with mission complete/fail sounds
- Inventory — 8 slots, stacking, item pickups with sound
- Equipment — Q/R quick-use slots with cooldowns
- Items — Energy Cell (heal), Hack Booster (+5s timer), EMP Pulse (disable drones)
- **Audio system** — background music per zone, SFX for all interactions
- **Volume control** — adjustable master volume in Settings
- Scene system, Docker support

## 🚀 Run

```bash
pip install -r requirements.txt
python generate_placeholder_audio.py   # first time only
python main.py
```

| Key | Action |
|---|---|
| W/A/S/D | Move |
| Mouse | Look |
| Space | Jump |
| Shift | Sprint |
| E | Interact/Hack/Extract |
| TAB | Toggle inventory |
| Q | Use equipment slot 1 |
| R | Use equipment slot 2 (or restart on end screen) |
| 1-8 | Equip item to Q slot (in inventory) |
| ESC | Menu/abort hack |

## 🗺 Roadmap

| Phase | Status |
|---|---|
| 1–7 | ✅ |
| 8 Polish | 🔲 |

© Aimtech
