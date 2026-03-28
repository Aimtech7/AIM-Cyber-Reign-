# Phase Notes — AIM: Cyber Reign

> Design decisions and notes for each development phase.
> Author: Aimtech

---

## Phase 1 — Foundation

### Goals
- Establish clean, modular project architecture
- Create a cyberpunk visual theme with neon colours
- Implement basic gameplay loop (menu → game → menu)
- Set up Docker containerisation
- Create comprehensive documentation and AI tracking

### Design Decisions

#### Why Ursina?
Ursina provides a high-level Python API over Panda3D, making it fast to
prototype 3D games without sacrificing access to low-level features.
It handles rendering, input, physics, and UI out of the box.

#### Why a config.py?
Centralising all constants eliminates magic numbers, makes the game
easy to re-theme, and ensures AI tools can find and modify settings
without scanning every file.

#### Why a SceneManager class?
Scene transitions are a common source of bugs in games (leaking entities,
dangling references). Encapsulating all transition logic in one class
with explicit `destroy()` calls on every game object prevents this.

#### Why Docker?
Containerisation ensures the game can be built and run on any machine
with identical dependencies, regardless of the host OS. This is
essential for CI/CD, team collaboration, and reproducible builds.

### Known Limitations
- No textures on buildings (cubes use flat colours)
- No audio
- No post-processing (bloom, glow, etc.)
- FirstPersonController uses basic box colliders

### Lessons Learned
- Ursina's `FirstPersonController` handles gravity and jumping automatically
- Grid lines work well with `unlit=True` entities at low alpha
- `destroy()` must be called on every entity individually; there is no
  bulk scene clear in Ursina

---

## Phase 2 — Combat (Planned)

### Planned Features
- Weapon system (equip, fire, reload)
- Projectile or raycast shooting
- Hit detection and damage
- Muzzle flash and impact effects

---

## Phase 3 — Enemies (Planned)

### Planned Features
- Enemy entities with health
- Patrol waypoints
- Aggro / chase behaviour
- Death and respawn logic

---

*Document maintained by Aimtech and AI assistants.*
