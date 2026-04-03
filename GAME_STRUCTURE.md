# GAME_STRUCTURE.md — AIM: Cyber Reign

> Architecture reference — v0.8.0

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
│   ├── audio.py           ← Phase 7
│   ├── effects.py         ← Phase 8 (glow, particles, camera FX)
│   └── save_system.py     ← Phase 8 (JSON persistence)
├── assets/
│   ├── audio/             ← Phase 7 (22 .wav files)
│   ├── fonts/, textures/
├── saves/                 ← Phase 8 (auto-generated save directory)
├── docs/
└── Dockerfile, README.md, GAME_STRUCTURE.md, AI_PROGRESS.md
```

## 📄 File Purposes

| File | Purpose |
|---|---|
| `config.py` | All constants (~580 lines) — gameplay balance, effects, UI, save/load |
| `menu.py` | Animated main menu (with Continue button if save exists) |
| `player.py` | FPS controller + sprint + head bob + camera shake integration |
| `environment.py` | 3D world + terminals + extraction zone + glow effects + neon accents |
| `interaction.py` | Proximity interaction + pause |
| `ui.py` | Full HUD: health lerp, damage vignette, alert flash, mission, inventory |
| `scenes.py` | Scene manager + hacking + drones + missions + save/load + particles |
| `settings.py` | Settings panel (volume slider wired to audio) |
| `game_state.py` | Breaches, health, alert, hack boost tracking |
| `hacking.py` | Key-sequence mini-game (with key/success/fail SFX) |
| `enemies.py` | SecurityDrone AI (with LOD + frame-skip optimization) |
| `missions.py` | Mission, Objective, MissionManager |
| `items.py` | Item base class + 3 item types |
| `inventory.py` | Inventory, EquipmentManager, ItemPickup |
| `audio.py` | AudioManager — music, SFX, volume control |
| `effects.py` | GlowPulse, ParticleEmitter, CameraFX |
| `save_system.py` | JSON save/load, auto-save, apply_save_data |

---

## 🎮 Game Systems

### Polish & Effects (Phase 8)
```
GlowPulse → terminals / extraction zone (sine-wave scale + alpha)
ParticleEmitter → EMP burst / hacking / alert (auto-cleanup)
CameraFX → head bob (walking) + shake (damage, EMP, hack fail)
Damage Vignette → red overlay on hit (fades out)
Alert Flash → border flash on alert escalation
Health Bar → smooth lerp transition with color gradient
```

### Save / Load (Phase 8)
```
Auto-save → on terminal breach + extraction success
Continue → menu button loads save → apply_save_data → restore state
Save data: player position, health, breached terminals, inventory, mission
```

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
| **8 — Polish & Final Touches** | ✅ |

---
© Aimtech — AIM: Cyber Reign
