# AIM: Cyber Reign

> Cyberpunk 3D game — Python + Ursina

**Author:** Aimtech | **Version:** 0.8.0 | **Phase 8 — Polish & Final Touches**

---

## 🎮 Features

- First-person movement (WASD, sprint, jump) with head bob & camera shake
- Cyberpunk 3D world with neon glow effects and accent lighting
- Hacking mini-game with key-press and success/fail sounds
- Security drones with 3-state AI, distance-based LOD optimization
- Player health with smooth animated health bar, damage vignette, color gradient
- Mission system — "SECTOR BREACH": breach 2 targets + reach extraction
- Win/lose conditions with mission complete/fail sounds
- Inventory — 8 slots, stacking, item pickups with sound
- Equipment — Q/R quick-use slots with cooldowns
- Items — Energy Cell (heal), Hack Booster (+5s timer), EMP Pulse (disable drones + particles)
- Audio system — background music per zone, SFX for all interactions
- Volume control — adjustable master volume in Settings
- **Save/Load system** — auto-saves on breach/extraction, Continue from menu
- **Visual polish** — glow pulses, particle effects, damage vignette, alert flash
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
| **8 — Polish & Final Touches** | ✅ |

© Aimtech
