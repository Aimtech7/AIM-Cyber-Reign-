# GAME_STRUCTURE.md — AIM: Cyber Reign

> Architecture reference — v0.5.0

---

## 📁 Structure

```
cyberpunk_game/
├── main.py
├── src/
│   ├── __init__.py, config.py
│   ├── menu.py, settings.py, player.py
│   ├── environment.py, interaction.py
│   ├── ui.py, scenes.py
│   ├── game_state.py, hacking.py
│   ├── enemies.py         ← Phase 4
│   └── missions.py        ← Phase 5
├── assets/, docs/
└── Dockerfile, README.md, GAME_STRUCTURE.md, AI_PROGRESS.md
```

## 📄 File Purposes

| File | Purpose |
|---|---|
| `config.py` | All constants (~390 lines) |
| `menu.py` | Animated main menu |
| `player.py` | FPS controller + sprint |
| `environment.py` | 3D world + terminals + extraction zone |
| `interaction.py` | Proximity interaction + pause |
| `ui.py` | Full HUD: status, health, alert, mission panel |
| `scenes.py` | Scene transitions + hacking + drones + missions |
| `settings.py` | Settings panel |
| `game_state.py` | Breaches, health, alert tracking |
| `hacking.py` | Key-sequence mini-game |
| `enemies.py` | SecurityDrone AI |
| `missions.py` | Mission, Objective, MissionManager |

---

## 🎮 Game Systems

### Mission System (Phase 5)
```
Game starts → "SECTOR BREACH" mission auto‑loads
  → Objective 1: Breach Alpha + Gamma (2 terminals)
  → Objective 2: Reach extraction zone
  → HP = 0 → MISSION FAILED → R to restart
  → Extraction before objectives → "Complete objectives first!"
  → All done + extraction → MISSION COMPLETE → R to restart
```

### Security (Phase 4)
Drones patrol → detect → chase → damage.  Failed hacks raise global alert.

### Hacking (Phase 3)
Terminal interaction → key-sequence challenge → breach/fail → state update + alert.

### Terminal States
| State | Colour |
|---|---|
| Locked | Green |
| Mission Target | Orange |
| Active | Yellow |
| Breached | Cyan |

---

## 🗺 Roadmap

| Phase | Status |
|---|---|
| 1–4 | ✅ |
| **5 — Missions** | **✅** |
| 6 — Inventory | 🔲 |
| 7 — Audio | 🔲 |
| 8 — Polish | 🔲 |

---
© Aimtech — AIM: Cyber Reign
