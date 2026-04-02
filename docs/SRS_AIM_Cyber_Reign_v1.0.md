▪  ▪  ▪
# SYSTEMS REQUIREMENTS SPECIFICATION
## AIM: Cyber Reign — 3D Cyberpunk First-Person Action Game
### Benchmarked Against: Deus Ex · System Shock · Cyberpunk 2077 · Hacknet · Watch Dogs

| Document Type | Systems Requirements Specification (SRS) |
|---|---|
| Version | 1.0 — Development Release |
| Date | April 2026 |
| Status | Approved — Phase 7 Complete, Phase 8 Planned |
| Prepared By | Aimtech Development Team |
| Classification | Commercial — Confidential |
| Benchmark Sources | Deus Ex (stealth hacking), System Shock (cyberpunk FPS), Cyberpunk 2077 (open-world FPS), Hacknet (hacking mini-games), Watch Dogs (drone mechanics) |

▪  ▪  ▪

---

## 1. INTRODUCTION

### 1.1 Purpose

This Systems Requirements Specification (SRS) defines the complete functional and non-functional requirements for **AIM: Cyber Reign**, a 3D first-person cyberpunk action game built with Python and the Ursina engine. It serves as the authoritative reference document for the development team, quality assurance engineers, and all project stakeholders throughout the system lifecycle.

Version 1.0 documents the current state of the system as delivered through Phase 7 (Audio System) and provides forward-looking requirements for the remaining Phase 8 (Polish & Final Touches). Competitive benchmarking findings drawn from five leading games — Deus Ex, System Shock, Cyberpunk 2077, Hacknet, and Watch Dogs — inform the system's design patterns and gameplay mechanics.

### 1.2 Scope

AIM: Cyber Reign is a single-player, first-person 3D action game set in a dark cyberpunk environment. The player is an infiltrator tasked with breaching secured terminals, evading or disabling security drones, collecting tactical items, and completing extraction-based missions. The system scope encompasses:

- First-person player controller with WASD movement, mouse look, sprint, and jump
- Procedurally themed 3D cyberpunk environment with buildings, pillars, walls, platforms, and grid-lit floors
- Hacking mini-game system with timed key-sequence challenges at varying security levels
- Security drone AI with three-state behaviour: IDLE → SUSPICIOUS → ALERT
- Mission and objective framework with win/lose conditions and restart capability
- Inventory and equipment system with item pickups, stacking, and quick-use slots
- Comprehensive audio system with background music, sound effects, and volume control
- Animated main menu with particle effects, settings panel, and scene management
- Heads-Up Display (HUD) with real-time status, mission tracking, equipment display, and inventory panel
- Docker containerisation for reproducible builds and deployment

### 1.3 Definitions, Acronyms & Abbreviations

| Term / Acronym | Definition |
|---|---|
| SRS | Systems Requirements Specification |
| UC | Use Case |
| FPS | First-Person Shooter / Frames Per Second (context-dependent) |
| HUD | Heads-Up Display — in-game overlay showing status, objectives, and inventory |
| AI | Artificial Intelligence — drone behaviour state machine |
| SFX | Sound Effects — one-shot audio clips |
| EMP | Electromagnetic Pulse — disables security drones temporarily |
| WASD | W-A-S-D movement keys (forward, left, backward, right) |
| SKU | Not applicable (single-product game) |
| RBAC | Not applicable (single-player, no user roles at runtime) |
| Ursina | Python 3D game engine built on Panda3D |
| Panda3D | Open-source 3D rendering engine (C++ with Python bindings) |
| SceneManager | Central orchestrator class managing menu ↔ game ↔ hacking transitions |
| GameState | Centralised tracker for health, alert level, breached terminals, and buffs |
| Vendor Hub | Not applicable (game context) |
| Breach | Successfully hacking a terminal to gain access |
| Extraction Zone | Designated area where the player completes a mission |
| Security Level | Terminal difficulty rating (1–3) determining hack sequence length |
| Alert Level | Global security state: CALM (0), SUSPICIOUS (1), ALERT (2) |
| Docker | Containerisation platform for reproducible builds |
| NFR | Non-Functional Requirement |

### 1.4 References & Benchmarks

| Reference | Source | Relevance to This SRS |
|---|---|---|
| Ursina Engine Documentation | ursina.org | Core game engine API, Entity system, FirstPersonController |
| Panda3D Manual | panda3d.org | Underlying rendering, audio, and physics systems |
| Deus Ex (2000, Ion Storm) | Competitive benchmark | Stealth-hacking gameplay, terminal breach mechanics, security AI |
| System Shock 2 (Irrational Games) | Competitive benchmark | Cyberpunk FPS, HUD design, inventory system, audio atmosphere |
| Cyberpunk 2077 (CD Projekt RED) | Competitive benchmark | Neon visual aesthetics, first-person movement, sprint mechanics |
| Hacknet (Team Fractal Alligator) | Competitive benchmark | Hacking mini-game design, timed challenges, security levels |
| Watch Dogs (Ubisoft) | Competitive benchmark | Drone AI, EMP mechanics, alert system escalation |
| IEEE Std 830-1998 | IEEE | Document structure and quality standard |

---

## 2. SYSTEM OVERVIEW

### 2.1 Business Context & Market Opportunity

AIM: Cyber Reign targets the growing market of cyberpunk-themed indie games, combining first-person action with strategic hacking mechanics. The game differentiates itself through its modular architecture, extensible mission system, and AI-driven security response — patterns validated by the benchmark titles.

Competitive benchmarking confirms the commercial viability of these mechanics. Deus Ex demonstrated that terminal hacking as a core gameplay loop creates high player engagement. Hacknet has proven that timed key-sequence challenges with escalating difficulty are compelling. Watch Dogs validated that drone AI with detection-pursuit-damage states creates meaningful tactical depth. Cyberpunk 2077 confirmed that neon-lit environments with first-person traversal define the genre's visual identity. System Shock 2 established that inventory management with consumable items adds strategic layers to FPS gameplay.

AIM: Cyber Reign synthesises all five proven patterns into a single, Python-accessible, modular game.

### 2.2 System Architecture Overview

The game follows a three-tier architecture, with each tier mapped to its technology stack and benchmark reference:

| Tier | Component | Technology | Benchmark |
|---|---|---|---|
| Presentation | 3D Rendering, HUD, Menus, Hacking Panel, Inventory UI | Ursina Engine (OpenGL) | Cyberpunk 2077 visuals, System Shock HUD |
| Application | Game Logic, AI State Machines, Scene Management, Audio, Missions | Python 3.11, Custom Modules | Deus Ex hacking, Hacknet challenges, Watch Dogs drones |
| Data | Configuration Constants, Game State, Inventory Slots | In-memory Python objects (`config.py`, `game_state.py`) | System Shock 2 inventory model |

> **Architecture Note**
> The modular single-file-per-system design enables AI-assisted development workflows where each module can be independently reasoned about, modified, and tested without cross-file dependencies.

### 2.3 Key Stakeholders

| Stakeholder | Role | Key Interest | Benchmark Analogue |
|---|---|---|---|
| Player | End user / gamer | Engaging gameplay, responsive controls, immersive atmosphere | All benchmark player bases |
| Aimtech (Developer) | Primary developer, project owner | Clean architecture, extensibility, modular phases | Indie studio (Team Fractal Alligator) |
| Development Team | AI-assisted builders & maintainers | Clear requirements, modular codebase, phase-based delivery | — |
| QA / Testers | Quality assurance | Reproducible builds (Docker), test coverage, consistent behaviour | — |

### 2.4 Core Feature Summary

The following eight features constitute the commercially essential capability set, each validated by at least one benchmark game:

| # | Feature | Description | Benchmark Source |
|---|---|---|---|
| 1 | First-Person Player Controller | WASD movement, mouse look, sprint (Shift), jump (Space) with physics | Cyberpunk 2077, Deus Ex |
| 2 | Cyberpunk 3D Environment | Buildings, pillars, walls, platforms, neon-lit grid floor, ambient lighting | Cyberpunk 2077, System Shock |
| 3 | Hacking Mini-Game System | Timed key-sequence challenges with 3 security levels, progress tracking, penalties | Hacknet, Deus Ex |
| 4 | Security Drone AI | 3-state behaviour (IDLE/SUSPICIOUS/ALERT), patrol, detect, chase, damage, EMP vulnerability | Watch Dogs, System Shock |
| 5 | Mission & Objective System | Structured objectives (breach/reach), extraction zone, win/lose/restart loop | Deus Ex mission structure |
| 6 | Inventory & Equipment System | 8-slot inventory with stacking, 2 quick-use equipment slots (Q/R), item pickups | System Shock 2 inventory |
| 7 | Audio System | Background music per scene, SFX for all interactions, volume control | All benchmarks |
| 8 | Scene Management & UI | Animated main menu, settings panel, HUD with real-time stats, scene transitions | All benchmarks |

---

## 3. FUNCTIONAL REQUIREMENTS

All functional requirements are classified by priority: **HIGH** (must-have for current version), **MEDIUM** (required for Phase 8 polish), **LOW** (planned future enhancement). Requirements in **bold** denote features informed by competitive benchmarking.

### 3.1 FR-01: Player Controller & Movement

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-01.1 | HIGH | The system shall provide a first-person controller with WASD directional movement at a configurable base speed (default: 6 units/sec). |
| FR-01.2 | HIGH | The system shall support mouse-look camera control with configurable sensitivity (default: 80, 80). |
| FR-01.3 | HIGH | The system shall allow the player to sprint by holding Left Shift, multiplying base speed by a configurable factor (default: 1.8×). **[Benchmark: Cyberpunk 2077]** |
| FR-01.4 | HIGH | The system shall allow the player to jump using the Space key with configurable height (default: 2 units). |
| FR-01.5 | HIGH | The system shall play footstep audio at walk intervals (0.5s) and sprint intervals (0.3s), alternating between two footstep variants. **[Benchmark: System Shock 2]** |
| FR-01.6 | HIGH | The system shall detect jump and landing events and play corresponding sound effects. |
| FR-01.7 | HIGH | The system shall spawn the player at a configurable start position (default: 0, 2, 0). |
| FR-01.8 | HIGH | The player controller shall be disableable during hacking, inventory, and end-screen states. |

### 3.2 FR-02: Game Environment

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-02.1 | HIGH | The system shall render a ground plane (100×100 units) with a neon-cyan grid overlay at configurable line spacing (default: 2 units). **[Benchmark: Cyberpunk 2077 aesthetics]** |
| FR-02.2 | HIGH | The system shall place 12 buildings of varying dimensions with neon edge lighting and randomised accent colours from the cyberpunk palette. |
| FR-02.3 | HIGH | The system shall place 8 decorative pillars with neon glow tops and bases distributed around the arena. |
| FR-02.4 | HIGH | The system shall place 4 boundary walls with collision boxes enclosing the play area (60×60 units). |
| FR-02.5 | HIGH | The system shall place 5 elevated platforms with collision boxes, including a central low platform. |
| FR-02.6 | HIGH | The system shall provide ambient lighting tinted blue and a directional "sun" light with cold blue-grey colour. |
| FR-02.7 | HIGH | The system shall place 4 hackable cyber terminals at configurable positions with labels and security levels (1–3). |
| FR-02.8 | HIGH | The system shall render an extraction zone at configurable coordinates with a glowing pad, pulsing ring, and corner markers. **[Benchmark: Deus Ex extraction]** |
| FR-02.9 | HIGH | The system shall spawn 6 item pickup entities at configurable positions, each with a bobbing and rotating animation. |

### 3.3 FR-03: Hacking System

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-03.1 | HIGH | The system shall present a full-screen hacking panel when the player interacts with an unhacked terminal. **[Benchmark: Hacknet]** |
| FR-03.2 | HIGH | The hacking panel shall generate a random key sequence from the key pool (W, A, S, D, Q, R, F) with length determined by security level: Level 1 → 4 keys, Level 2 → 5 keys, Level 3 → 6 keys. |
| FR-03.3 | HIGH | The system shall provide a countdown timer (default: 12 seconds) with a visual progress bar that changes colour: cyan (>50%), yellow (25–50%), magenta (<25%). |
| FR-03.4 | HIGH | Correct key presses shall advance progress and highlight the key in green with a key-press sound effect. |
| FR-03.5 | HIGH | Wrong key presses shall penalise the player by rolling back 1 correct key and playing a failure sound. |
| FR-03.6 | HIGH | Timer expiration shall result in hack failure with appropriate visual and audio feedback. |
| FR-03.7 | HIGH | The player may abort a hack by pressing ESC without penalty. |
| FR-03.8 | HIGH | Hack Booster items shall add bonus time (default: +5 seconds) to the hacking timer. **[Benchmark: System Shock consumables]** |
| FR-03.9 | HIGH | Successful hacks shall mark the terminal as "breached" with a visual colour change (cyan), update game state, and notify the mission manager. |
| FR-03.10 | HIGH | Music shall switch from ambient to a tense loop during hacking and revert on completion. **[Benchmark: Hacknet audio design]** |

### 3.4 FR-04: Security Drone AI

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-04.1 | HIGH | The system shall spawn 4 security drones at configurable positions, each with a dark body, glowing ring, and antenna. **[Benchmark: Watch Dogs drone design]** |
| FR-04.2 | HIGH | Each drone shall implement a three-state AI: IDLE (patrol), SUSPICIOUS (detection), ALERT (chase). **[Benchmark: Watch Dogs AI]** |
| FR-04.3 | HIGH | In IDLE state, drones shall wander within a configurable patrol radius (default: 8 units) with a gentle vertical bob. |
| FR-04.4 | HIGH | When a player enters detection radius (default: 12 units), drones shall enter SUSPICIOUS state, turn toward the player, and play an alert sound. |
| FR-04.5 | HIGH | After 2 seconds in SUSPICIOUS or if the player enters close range, drones shall escalate to ALERT state with chase sound and pursue at chase speed (default: 4.5 units/sec). |
| FR-04.6 | HIGH | In ALERT state, drones within damage radius (default: 3.5 units) shall deal damage to the player (default: 8 HP/sec) with throttled hit sounds (max 1/sec). |
| FR-04.7 | HIGH | Drones shall revert to IDLE after the player escapes detection range for a timeout period (default: 6 seconds). |
| FR-04.8 | HIGH | The glow ring and antenna colour shall change per state: cyan (IDLE), yellow (SUSPICIOUS), magenta (ALERT). |
| FR-04.9 | HIGH | Drones shall be disableable by EMP items for a configurable duration (default: 5 seconds), displaying a grey dim colour while disabled. **[Benchmark: Watch Dogs EMP]** |
| FR-04.10 | HIGH | Global alert level shall force all drones into ALERT state when at maximum threshold. |

### 3.5 FR-05: Player Health & Alert System

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-05.1 | HIGH | The player shall have a maximum health pool (default: 100 HP) displayed on the HUD with a colour-coded health bar. |
| FR-05.2 | HIGH | The system shall implement health regeneration (default: 2 HP/sec) after a delay period following damage (default: 4 seconds). **[Benchmark: Cyberpunk 2077 regen]** |
| FR-05.3 | HIGH | The system shall track a global alert level with three tiers: CALM (0), SUSPICIOUS (1), ALERT (2). |
| FR-05.4 | HIGH | The alert level shall increase on hack success (proportional to security level) and significantly on hack failure. |
| FR-05.5 | HIGH | The alert level shall decay over time when no new alerts are raised (default: 20-second hold, 0.15/sec decay). |
| FR-05.6 | HIGH | Player death (0 HP) shall trigger mission failure. |

### 3.6 FR-06: Mission & Objective System

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-06.1 | HIGH | The system shall provide a reusable mission framework supporting Objective, Mission, and MissionManager classes. **[Benchmark: Deus Ex mission structure]** |
| FR-06.2 | HIGH | Objectives shall support two types: 'breach' (hack specific terminals) and 'reach' (enter a zone). |
| FR-06.3 | HIGH | The system shall ship with a default mission "SECTOR BREACH": breach 2 required terminals (Access Node Alpha, Data Terminal Gamma), then reach extraction zone. |
| FR-06.4 | HIGH | Mission-required terminals shall be visually highlighted with an orange glow and "[TARGET]" prefix in interaction prompts. |
| FR-06.5 | HIGH | The extraction zone shall only trigger mission completion when all breach objectives are complete. |
| FR-06.6 | HIGH | The MissionManager shall provide HUD info (mission name, current objective, progress, status, feedback messages). |
| FR-06.7 | HIGH | Mission statuses shall follow: NOT_STARTED → ACTIVE → COMPLETED or FAILED. |
| FR-06.8 | HIGH | On mission completion or failure, the system shall display a full-screen overlay with result text (green/magenta) and options to restart (R) or return to menu (ESC). |
| FR-06.9 | HIGH | Mission completion and failure shall play distinct sound effects and stop background music. |

### 3.7 FR-07: Inventory & Equipment System

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-07.1 | HIGH | The system shall provide an 8-slot inventory with stackable item support. **[Benchmark: System Shock 2 inventory]** |
| FR-07.2 | HIGH | Items within detection range (default: 3 units) shall be auto-collected into the inventory with a pickup sound effect. |
| FR-07.3 | HIGH | The inventory shall be viewable via a toggle panel (TAB key) showing item icons, names, counts, and equipped status. |
| FR-07.4 | HIGH | The system shall provide two quick-use equipment slots mapped to Q and R keys with a 2-second cooldown. |
| FR-07.5 | HIGH | Items shall be equippable from the inventory panel using number keys 1–8. |
| FR-07.6 | HIGH | The system shall provide three consumable item types: |
| FR-07.6a | HIGH | **Energy Cell** (⚡): Restores 30 HP. Stack limit: 5. No effect at full health. |
| FR-07.6b | HIGH | **Hack Booster** (◈): Adds +5 seconds to next hack timer. Stack limit: 3. Single-use buff. |
| FR-07.6c | HIGH | **EMP Pulse** (◉): Disables all drones within 15-unit radius for 5 seconds. Stack limit: 3. **[Benchmark: Watch Dogs EMP]** |
| FR-07.7 | HIGH | Item pickups in the world shall display as glowing orange cubes with a vertical bob and slow rotation animation. |
| FR-07.8 | HIGH | Equipment slots shall auto-clear when the last item of an equipped type is consumed. |

### 3.8 FR-08: Audio System

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-08.1 | HIGH | The system shall provide a centralised AudioManager handling background music (looping), one-shot SFX, and volume control. **[Benchmark: All titles — audio immersion]** |
| FR-08.2 | HIGH | The AudioManager shall support three volume channels: Master, Music, and SFX, each independently configurable (0.0–1.0). |
| FR-08.3 | HIGH | Effective volume shall be calculated as master × channel volume. |
| FR-08.4 | HIGH | The system shall provide 3 music tracks: `menu_loop` (main menu), `cyber_ambient` (in-game), `tense_loop` (hacking). |
| FR-08.5 | HIGH | The system shall provide 22 sound effects covering: UI (4), hacking (4), drones (4), player movement (4), missions (3), and item interactions (3). |
| FR-08.6 | HIGH | Music shall switch contextually: menu → ambient on game start, ambient → tense on hack start, tense → ambient on hack end. |
| FR-08.7 | HIGH | Missing audio files shall produce console warnings but shall never crash the application (graceful fallback). |
| FR-08.8 | HIGH | A placeholder audio generator script (`generate_placeholder_audio.py`) shall produce all 22 WAV files as sine-wave tones for development. |

### 3.9 FR-09: Main Menu & Settings

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-09.1 | HIGH | The system shall present an animated main menu with neon title, subtitle, version tag, author credit, and three buttons (Start Game, Settings, Exit). |
| FR-09.2 | HIGH | The menu shall feature 30 animated background particles drifting upward with random neon colours, creating a living cyberpunk atmosphere. **[Benchmark: Cyberpunk 2077 menu aesthetics]** |
| FR-09.3 | HIGH | Menu buttons shall have neon styling with hover (magenta) and press (purple) colour states, and play a click sound effect. |
| FR-09.4 | HIGH | The Settings panel shall provide a volume slider controlling master audio volume, wired to the AudioManager. |
| FR-09.5 | HIGH | Pressing ESC during gameplay shall return to the main menu, destroying all game entities cleanly. |

### 3.10 FR-10: Heads-Up Display (HUD)

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-10.1 | HIGH | The HUD shall display (left panel): system status, project name/version, access level, breached node count. |
| FR-10.2 | HIGH | The HUD shall display (right panel): zone name, sprint indicator, alert level (with colour), health bar with numeric value, equipment slot status (Q/R). |
| FR-10.3 | HIGH | The HUD shall display (bottom panel): mission name, current objective, progress, and mission status. |
| FR-10.4 | HIGH | The HUD shall display (centre): security warning alerts (SUSPICIOUS / ALERT), mission feedback messages, item pickup/use feedback. |
| FR-10.5 | HIGH | The health bar shall change colour based on health percentage: green (>50%), yellow (25–50%), magenta (<25%). |
| FR-10.6 | HIGH | Equipment slot display shall show item name, cooldown timer, and ready status. |
| FR-10.7 | HIGH | All HUD text shall use the VeraMono monospace font for cyberpunk aesthetic consistency. |

### 3.11 FR-11: Scene Management

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-11.1 | HIGH | The SceneManager shall orchestrate all scene transitions: Menu → Game, Game → Menu, Game → Hacking → Game, Game → End Screen. |
| FR-11.2 | HIGH | Scene transitions shall cleanly destroy all entities from the previous scene to prevent memory leaks. |
| FR-11.3 | HIGH | The SceneManager shall manage a state dictionary tracking all active game objects: menu, settings, environment, player, HUD, interaction, game state, hacking panel, drones, mission manager, inventory, and equipment. |
| FR-11.4 | HIGH | Input handling shall be delegated through the SceneManager, with context-aware routing (hacking absorbs input, inventory absorbs number keys, end screen captures R/ESC). |

### 3.12 FR-12: Interaction System

| Req. ID | Priority | Requirement Description |
|---|---|---|
| FR-12.1 | HIGH | The system shall detect interactive objects within a configurable proximity range (default: 5 units). |
| FR-12.2 | HIGH | When near an interactable, the system shall display a context-specific prompt (e.g., "Press E to hack [TARGET] Access Node Alpha"). |
| FR-12.3 | HIGH | The interaction key (default: E) shall trigger the associated callback (hack terminal, attempt extraction). |
| FR-12.4 | HIGH | The interaction system shall be pauseable during hacking, inventory, and end-screen states. |
| FR-12.5 | HIGH | Interaction messages shall display for a configurable duration (default: 3 seconds). |

---

## 4. NON-FUNCTIONAL REQUIREMENTS

| NFR ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | The game shall maintain a minimum of 30 FPS at 1280×720 resolution on a system with a 2GHz quad-core CPU and integrated GPU. |
| NFR-02 | Performance | Scene transitions (menu → game, game → menu) shall complete in under 3 seconds including entity creation and audio switching. |
| NFR-03 | Performance | The hacking panel shall render and accept input with no perceptible lag (< 16ms input latency). |
| NFR-04 | Scalability | The environment system shall support up to 50 buildings, 20 terminals, and 20 drones without architecture redesign. |
| NFR-05 | Scalability | The inventory system shall support up to 64 slots without performance degradation. |
| NFR-06 | Availability | The game shall gracefully handle missing audio files without crashing — substituting console warnings and continuing normal operation. |
| NFR-07 | Portability | The game shall run on Windows, macOS, and Linux via standard Python 3.11+ and Ursina engine. |
| NFR-08 | Portability | The game shall be containerisable via Docker for reproducible builds, with X11 forwarding or virtual framebuffer for display. |
| NFR-09 | Usability | A first-time player shall understand basic controls (move, look, interact, hack) within 1 minute of starting the game, aided by on-screen prompts. |
| NFR-10 | Usability | The HUD shall provide all critical information (health, alert, objectives, equipment) at a glance without requiring menu navigation during gameplay. |
| NFR-11 | Maintainability | All global constants shall be centralised in `config.py` — no magic numbers scattered across source files. |
| NFR-12 | Maintainability | Each game system shall be encapsulated in a single source file with clear docstrings and type annotations for AI-assisted development. |
| NFR-13 | Maintainability | The codebase shall follow modular architecture: 18 source files, each under 700 lines, with single-responsibility design. |
| NFR-14 | Extensibility | New item types shall be addable by subclassing `Item` and registering in the `create_item()` factory function — no core system changes required. |
| NFR-15 | Extensibility | New missions shall be addable by creating `Mission` and `Objective` instances — no MissionManager changes required. |

---

## 5. BUSINESS USE CASES

### 5.1 Overview

Business Use Cases capture the game's value delivery to primary stakeholders at the strategic level, independent of technical implementation. Each BUC is informed by demonstrated gameplay patterns from the benchmark titles.

### 5.2 BUC-01: Player Completes a Mission

> **Business Objective**
> Enable a player to experience a complete gameplay loop — from mission briefing through tactical hacking, drone evasion, item usage, and successful extraction — within a 10–15 minute play session, replicating the proven Deus Ex mission structure.

| Field | Value |
|---|---|
| Business Goal | Deliver a satisfying, replayable gameplay loop that demonstrates all core systems |
| Primary Actor | Player |
| Trigger | Player clicks "Start Game" from the main menu |
| Business Value | Validates core gameplay loop; demonstrates all systems working in harmony |
| Success Outcome | Player breaches 2 target terminals, evades/disables drones, and reaches extraction |
| Failure Outcome | Player dies to drone damage before completing objectives |
| Business Rules | Mission objectives must be completed in order. Extraction requires all breaches. Health reaching 0 triggers mission failure. |
| Benchmark Pattern | Deus Ex mission flow; Hacknet challenge escalation; Watch Dogs tactical drone evasion |

### 5.3 BUC-02: Player Masters the Hacking System

> **Business Objective**
> Provide an engaging, skill-based hacking mechanic that rewards pattern recognition and fast reactions — following the Hacknet model of timed challenges with escalating difficulty.

| Field | Value |
|---|---|
| Business Goal | Create a compelling core mechanic that players want to master |
| Primary Actor | Player |
| Trigger | Player interacts with a terminal (presses E) |
| Business Value | Core engagement loop; differentiating mechanic; drives replayability |
| Success Outcome | Player completes key sequence within time limit, terminal is breached |
| Failure Outcome | Timer expires or player accumulates too many errors |
| Business Rules | Security levels 1–3 determine sequence length. Wrong keys penalise progress. Hack Boosters add time. ESC aborts safely. |
| Benchmark Pattern | Hacknet timed challenges; Deus Ex terminal hacking |

### 5.4 BUC-03: Developer Extends the Game

> **Business Objective**
> Enable developers (including AI assistants) to extend the game with new content — items, missions, enemies, environments — without modifying core systems.

| Field | Value |
|---|---|
| Business Goal | Maximise development velocity and AI-assisted coding efficiency |
| Primary Actor | Developer / AI Assistant |
| Trigger | Developer identifies new feature requirement |
| Business Value | Accelerates iteration; reduces bug risk; enables AI pair-programming |
| Success Outcome | New feature added via subclassing and configuration, no core files modified |
| Business Rules | Constants in config.py. Items via factory pattern. Missions via Objective/Mission classes. Drones via DRONE_SPECS. |
| Benchmark Pattern | Modular indie game architecture (best practice) |

---

## 6. SYSTEM USE CASES

### 6.1 Use Case Summary

| UC ID | Use Case Name | Actor(s) | Priority | Phase |
|---|---|---|---|---|
| UC-01 | Navigate the Environment | Player | HIGH | 1–2 |
| UC-02 | Hack a Terminal | Player, HackingPanel | HIGH | 3 |
| UC-03 | Evade Security Drones | Player, SecurityDrone(s) | HIGH | 4 |
| UC-04 | Take Damage & Regenerate | Player, Drones, GameState | HIGH | 4 |
| UC-05 | Complete a Mission | Player, MissionManager | HIGH | 5 |
| UC-06 | Collect & Use Items | Player, Inventory, Items | HIGH | 6 |
| UC-07 | Equip & Activate Equipment | Player, EquipmentManager | HIGH | 6 |
| UC-08 | Fire EMP Pulse | Player, Drones, EMPItem | HIGH | 6 |
| UC-09 | Adjust Audio Settings | Player, AudioManager, Settings | HIGH | 7 |
| UC-10 | Navigate Main Menu | Player, MainMenu, SceneManager | HIGH | 1–2 |

### 6.2 Detailed Use Cases

---

**USE CASE — Hack a Terminal [UC-02]**

| Field | Value |
|---|---|
| Use Case ID | UC-02 |
| Use Case Name | Hack a Terminal |
| Actor(s) | Player (Primary), HackingPanel (System), AudioManager (Secondary) |
| Description | The player approaches a hackable terminal, initiates a breach, and completes a timed key-sequence challenge to gain access. |
| Preconditions | Player is in the game scene. Terminal has not been previously breached. Player is within interaction distance (5 units). No other hack is in progress. |
| Main Flow | 1. Player approaches a terminal. 2. HUD displays "Press E to hack [label]". 3. Player presses E. 4. Player controller is frozen; mouse unlocked. 5. Music switches to tense loop. 6. HackingPanel renders with key sequence, timer bar, and status. 7. Player presses keys matching the displayed sequence in order. 8. Each correct key highlights green with SFX. 9. All keys completed → "BREACH COMPLETE" displayed. 10. Terminal marked as breached (colour → cyan). 11. Game state updated (access level, alert). 12. Mission manager notified. 13. Music reverts to ambient. 14. Player control restored. |
| Alternate Flow | Step 7: Wrong key → progress rolled back by 1, warning displayed, fail SFX. Timer expires → hack fails, terminal remains locked, alert raised. Step 3: Terminal already breached → "already breached" message, no panel opened. Player presses ESC → hack aborted, no penalty, control restored. |
| Postconditions | Terminal is breached or remains locked. Game state updated. Alert level adjusted. Player control restored. |
| Priority | HIGH |
| Benchmark Reference | Hacknet timed challenges; Deus Ex terminal breach |

---

**USE CASE — Complete a Mission [UC-05]**

| Field | Value |
|---|---|
| Use Case ID | UC-05 |
| Use Case Name | Complete a Mission |
| Actor(s) | Player (Primary), MissionManager (System), SecurityDrones (Antagonist) |
| Description | The player completes the "SECTOR BREACH" mission by hacking 2 required terminals and reaching the extraction zone while surviving drone attacks. |
| Preconditions | Game scene is active. Mission loaded and status is ACTIVE. |
| Main Flow | 1. Mission starts with "MISSION: SECTOR BREACH" on HUD. 2. Player navigates to first target terminal (orange glow). 3. Player hacks terminal 1 (see UC-02). 4. HUD updates objective progress (1/2). 5. Player navigates to second target terminal. 6. Player hacks terminal 2. 7. "OBJECTIVE COMPLETE: Breach required terminals" displayed. 8. Player navigates to extraction zone. 9. Player presses E in extraction zone. 10. Mission completes → "MISSION COMPLETE" overlay with green text. 11. Mission complete SFX plays; music stops. 12. End screen offers Restart (R) or Menu (ESC). |
| Alternate Flow | Step 9: Not all breach objectives complete → "Complete all objectives before extraction!" message. Player health reaches 0 at any point → "MISSION FAILED" overlay with magenta text, fail SFX. |
| Postconditions | Mission status is COMPLETED or FAILED. End screen displayed. Player may restart or return to menu. |
| Priority | HIGH |
| Benchmark Reference | Deus Ex mission completion; System Shock extraction mechanics |

---

**USE CASE — Collect & Use Items [UC-06]**

| Field | Value |
|---|---|
| Use Case ID | UC-06 |
| Use Case Name | Collect & Use Items |
| Actor(s) | Player (Primary), Inventory (System), Items (System) |
| Description | The player auto-collects items from the world, views inventory, equips items to quick-use slots, and activates them during gameplay. |
| Preconditions | Game scene is active. Item pickups exist in the world. |
| Main Flow | 1. Player walks near a glowing item pickup (within 3 units). 2. Item auto-collected; pickup SFX plays. 3. HUD displays "PICKED UP: ⚡ Energy Cell". 4. Player presses TAB to view inventory. 5. Inventory panel shows items with icons, names, counts. 6. Player presses 1–8 to equip item to Q slot. 7. HUD updates equipment display. 8. Player presses Q to use equipped item. 9. Item effect activates (heal / boost / EMP). 10. Item consumed; cooldown starts (2 seconds). |
| Alternate Flow | Step 1: Inventory full → item not collected, remains in world. Step 8: Cooldown active → use ignored. Step 8: Energy Cell at full HP → "Cannot use that now". |
| Postconditions | Item effect applied. Item count decremented. Equipment slot cleared if stack depleted. |
| Priority | HIGH |
| Benchmark Reference | System Shock 2 inventory; Watch Dogs gadgets |

---

## 7. USE CASE DIAGRAM — TEXTUAL REPRESENTATION

### 7.1 System Actors

| Actor | Type | Interacts With |
|---|---|---|
| Player | External Primary | UC-01 through UC-10 (all use cases) |
| HackingPanel | System Component | UC-02 (key-sequence challenge) |
| SecurityDrone(s) | System Component | UC-03, UC-04, UC-08 (patrol, chase, EMP) |
| GameState | System Component | UC-02, UC-04, UC-05, UC-06 (health, alert, breach tracking) |
| MissionManager | System Component | UC-05 (objective tracking, extraction, win/lose) |
| Inventory | System Component | UC-06, UC-07 (item storage, stacking) |
| EquipmentManager | System Component | UC-07, UC-08 (quick-use slots, cooldowns) |
| AudioManager | System Component | UC-02, UC-03, UC-05, UC-06, UC-09, UC-10 (music/SFX) |
| SceneManager | System Component | UC-01 through UC-10 (scene orchestration) |
| InteractionSystem | System Component | UC-02, UC-05 (proximity detection, prompts) |

### 7.2 Use Case Relationship Map

| Base Use Case | Relationship | Related Use Case |
|---|---|---|
| UC-02: Hack a Terminal | «include» | UC-01: Navigate (must reach terminal) |
| UC-05: Complete Mission | «include» | UC-02: Hack a Terminal (breach required) |
| UC-05: Complete Mission | «include» | UC-01: Navigate (reach extraction) |
| UC-06: Collect Items | «include» | UC-01: Navigate (must reach pickup) |
| UC-07: Equip Item | «include» | UC-06: Collect Items (must have items) |
| UC-08: Fire EMP | «include» | UC-07: Equip Item (must equip EMP) |
| UC-04: Take Damage | «extend» | UC-03: Evade Drones (damage on fail) |
| UC-03: Evade Drones | «extend» | UC-02: Hack (hacking raises alert) |

### 7.3 Actor-to-Use Case Matrix

| Use Case | Player | HackPanel | Drones | GameState | MissionMgr | Inventory | EquipMgr | AudioMgr | SceneMgr | InteractSys |
|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 Navigate | ● | – | – | – | – | – | – | – | ◑ | – |
| UC-02 Hack Terminal | ● | ● | – | ◑ | ◑ | – | – | ◑ | ◑ | ● |
| UC-03 Evade Drones | ● | – | ● | ◑ | – | – | – | ◑ | – | – |
| UC-04 Damage/Regen | ● | – | ◑ | ● | – | – | – | – | – | – |
| UC-05 Complete Mission | ● | – | – | ◑ | ● | – | – | ◑ | ◑ | ● |
| UC-06 Collect Items | ● | – | – | – | – | ● | – | ◑ | ◑ | – |
| UC-07 Equip Item | ● | – | – | – | – | ◑ | ● | – | ◑ | – |
| UC-08 Fire EMP | ● | – | ◑ | – | – | ◑ | ◑ | ◑ | ◑ | – |
| UC-09 Audio Settings | ● | – | – | – | – | – | – | ● | ◑ | – |
| UC-10 Main Menu | ● | – | – | – | – | – | – | ◑ | ● | – |

● Primary Actor   ◑ Secondary / Supporting Actor   – Not Involved

---

## 8. DATA REQUIREMENTS

### 8.1 Core Data Entities

| Entity | Key Attributes | Relationships |
|---|---|---|
| GameState | health, max_health, alert_level, alert_accumulator, breached_labels, access_level, hack_boost_active | Central tracker → referenced by HUD, Drones, Missions, Items |
| PlayerController | controller, is_sprinting, _footstep_timer, _was_grounded | One Player → One GameState; One Player → One Inventory |
| SecurityDrone | state, spawn_pos, player_ref, game_state, emp_disabled, _emp_timer | Many Drones → One Player; Many Drones → One GameState |
| HackingPanel | terminal_label, security_level, sequence, progress, time_remaining, active | One Panel → One Terminal; One Panel → One GameState |
| Mission | name, objectives, status | One Mission → Many Objectives |
| Objective | description, obj_type, required_count, current_count, target_labels, completed | Many Objectives → One Mission |
| MissionManager | mission, _messages, _msg_timer | One Manager → One Mission |
| Inventory | max_slots, slots[{item, count}] | One Inventory → Many Items |
| Item (base) | name, description, icon_char, item_type, stackable, max_stack | Abstract base; subclassed by 3 types |
| EnergyCellItem | Inherits Item; heals 30 HP | One Item → One GameState (on use) |
| HackBoosterItem | Inherits Item; +5s hack time | One Item → One GameState (on use) |
| EMPPulseItem | Inherits Item; 15u radius, 5s disable | One Item → Many Drones (via callback) |
| EquipmentManager | slots {q, r}, cooldowns {q, r} | One Manager → One Inventory |
| ItemPickup | position, item_type, collected, glow_ring | Many Pickups → One Environment |
| AudioManager | volumes {master, music, sfx}, _current_music, _music_name | Singleton → All systems |

### 8.2 Environment Configuration Data

| Entity | Count | Key Attributes |
|---|---|---|
| Buildings | 12 | Position (x, z), width, height, depth — defined in `BUILDING_SPECS` |
| Pillars | 8 | Position (x, z), radius, height — defined in `PILLAR_SPECS` |
| Walls | 4 | Position (x, z), width, height, depth — defined in `WALL_SPECS` |
| Platforms | 5 | Position (x, z), width, height, depth — defined in `PLATFORM_SPECS` |
| Terminals | 4 | Position (x, z), label, security_level — defined in `TERMINAL_SPECS` |
| Drones | 4 | Spawn position (x, y, z) — defined in `DRONE_SPECS` |
| Item Pickups | 6 | Position (x, z), item_type — defined in `ITEM_PICKUP_SPECS` |

### 8.3 Audio Asset Manifest

| Category | Track/SFX Name | File | Purpose |
|---|---|---|---|
| Music | menu_loop | menu_loop.wav | Main menu background |
| Music | cyber_ambient | cyber_ambient.wav | In-game ambient |
| Music | tense_loop | tense_loop.wav | Hacking / high-security |
| UI SFX | click | click.wav | Menu button click |
| UI SFX | slider | slider.wav | Settings slider adjust |
| UI SFX | inventory_toggle | inventory_toggle.wav | TAB open/close |
| UI SFX | pickup | pickup.wav | Item collected |
| Hacking SFX | terminal_on | terminal_on.wav | Terminal interaction start |
| Hacking SFX | key_press | key_press.wav | Correct key in sequence |
| Hacking SFX | hack_success | hack_success.wav | Breach complete |
| Hacking SFX | hack_fail | hack_fail.wav | Wrong key / timeout |
| Drone SFX | drone_alert | drone_alert.wav | IDLE → SUSPICIOUS |
| Drone SFX | drone_chase | drone_chase.wav | SUSPICIOUS → ALERT |
| Drone SFX | drone_hit | drone_hit.wav | Drone damages player |
| Drone SFX | drone_disabled | drone_disabled.wav | EMP hit |
| Player SFX | footstep1 | footstep1.wav | Walk step variant 1 |
| Player SFX | footstep2 | footstep2.wav | Walk step variant 2 |
| Player SFX | jump | jump.wav | Player jumps |
| Player SFX | land | land.wav | Player lands |
| Mission SFX | extract | extract.wav | Extraction zone reached |
| Mission SFX | mission_complete | mission_complete.wav | Mission success |
| Mission SFX | mission_fail | mission_fail.wav | Mission failure |

---

## 9. PROJECT MILESTONES & DELIVERY PHASES

> **Delivery Principle**
> Following the agreed principle of small iterative milestones, the project is structured into eight phases. Each phase delivers independently testable, demonstrable functionality.

| Phase | Milestone | Deliverables | Status |
|---|---|---|---|
| 1 | Foundation | Project structure, main menu, player controller (WASD/jump), 3D environment (buildings, floor, grid), HUD skeleton, scene management, Docker, documentation | ✅ Complete |
| 2 | Visual Upgrade & Interaction | Animated menu with particles, settings panel, sprint mechanic, expanded environment (pillars, walls, platforms), interaction system with proximity prompts, enhanced HUD | ✅ Complete |
| 3 | Hacking Core System | Hacking mini-game with timed key-sequences, terminal states (locked/active/breached), game state tracking (breaches, access level), HUD breach count | ✅ Complete |
| 4 | Security Response System | Security drones with 3-state AI (patrol/detect/chase), global alert system (CALM/SUSPICIOUS/ALERT), player health with damage and regeneration, HUD health bar and alert indicator | ✅ Complete |
| 5 | Mission & Objective System | Mission framework (Objective/Mission/MissionManager), "Sector Breach" mission (2 breaches + extraction), extraction zone with visual markers, mission HUD panel, win/lose/restart overlay | ✅ Complete |
| 6 | Inventory & Equipment System | Item base class + 3 types (Energy Cell, Hack Booster, EMP Pulse), 8-slot inventory with stacking, equipment manager (Q/R slots, 2s cooldown), item pickups in world, inventory panel (TAB), HUD equipment display | ✅ Complete |
| 7 | Audio System | AudioManager (music + SFX + volume control), 22 placeholder audio files, music per scene (menu/ambient/tense), SFX for all interactions (UI/hacking/drones/player/missions), settings volume slider integration | ✅ Complete |
| 8 | Polish & Final Touches | Visual post-processing (bloom, glow), texture improvements, gameplay balancing, additional missions, UI refinement, performance optimisation, production audio replacement | 🔲 Planned |

---

## 10. ASSUMPTIONS, CONSTRAINTS & RISKS

| Type | Item | Detail |
|---|---|---|
| Assumption | Python Availability | Target users have Python 3.11+ installed or can run Docker containers. |
| Assumption | GPU Capability | Target systems have OpenGL-capable graphics (integrated GPU minimum). |
| Assumption | Audio Hardware | Target systems have audio output capability. Missing audio files are handled gracefully. |
| Assumption | Single Player | The game is single-player only. No networking, multiplayer, or server infrastructure required. |
| Constraint | Technology Stack | Development constrained to Python + Ursina engine (Panda3D). No low-level C++ or custom engine development. |
| Constraint | Phase Budget | Each phase targets 1–2 development sessions. Scope per phase is bounded by this constraint. |
| Constraint | Display Requirement | Ursina/Panda3D requires an OpenGL display. Docker deployment requires X11 forwarding or Xvfb. |
| Constraint | Resolution | Default window: 1280×720 windowed. Fullscreen configurable but not optimised for ultra-wide. |
| Risk | Ursina Limitations | Ursina's Entity-based architecture may limit performance with very large entity counts. Mitigation: Config-driven specs cap entity counts at proven levels. |
| Risk | Audio Placeholder Quality | Placeholder sine-wave audio is not production quality. Mitigation: Modular AudioManager allows drop-in replacement of WAV/OGG files. |
| Risk | Scope Creep in Phase 8 | Polish phase has loosely defined scope. Mitigation: Phase 8 items prioritised individually before development begins. |
| Risk | Control Complexity | Growing control scheme (10+ keys) may overwhelm new players. Mitigation: On-screen prompts, settings panel, and HUD indicators. |
| Risk | AI Development Dependency | Project relies heavily on AI-assisted development. Mitigation: Comprehensive documentation (this SRS, GAME_STRUCTURE.md, AI_PROGRESS.md), modular architecture, detailed docstrings. |

---

## 11. TECHNOLOGY STACK

| Component | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.11+ | Primary development language |
| Game Engine | Ursina | Latest (pip) | 3D rendering, input handling, Entity system, audio |
| Rendering Backend | Panda3D / OpenGL | Bundled with Ursina | 3D graphics, textures, lighting |
| Audio | Ursina Audio (Panda3D) | Bundled | WAV/OGG playback, looping, volume control |
| Containerisation | Docker | Latest | Reproducible builds, CI/CD readiness |
| Base Image | python:3.11-slim | Latest | Minimal container footprint |
| Font | VeraMono.ttf | Bundled with Ursina | Monospace cyberpunk HUD typography |
| Placeholder Audio | generate_placeholder_audio.py | Custom | Sine-wave WAV generation for development |

---

## 12. FILE STRUCTURE & MODULE RESPONSIBILITIES

| File | Lines | Purpose |
|---|---|---|
| `main.py` | 85 | Application entry point; window config; SceneManager creation; game loop start |
| `src/config.py` | 499 | All global constants: window, colours, player, environment, hacking, drones, alerts, health, missions, inventory, audio, metadata |
| `src/scenes.py` | 606 | Central SceneManager: menu/game transitions, hacking flow, drone spawning, mission orchestration, item pickups, EMP, equipment, audio switching |
| `src/player.py` | 170 | FirstPersonController: WASD, sprint, jump, footstep audio, jump/land detection |
| `src/environment.py` | 327 | 3D world builder: floor, buildings, pillars, walls, platforms, terminals, extraction zone, item pickups, lighting |
| `src/interaction.py` | ~150 | Proximity-based interaction system: Interactable class, prompt display, callback dispatch |
| `src/ui.py` | 397 | Heads-Up Display: status, health, alert, missions, equipment, inventory panel |
| `src/hacking.py` | 396 | Hacking mini-game: key-sequence generation, timer, input handling, success/fail |
| `src/enemies.py` | 342 | SecurityDrone: 3-state AI (idle/suspicious/alert), patrol, detect, chase, damage, EMP disable |
| `src/game_state.py` | 220 | GameState: terminal tracking, health/regen, alert system, hack boost flag |
| `src/missions.py` | 384 | Mission framework: Objective, Mission, MissionManager, Sector Breach factory |
| `src/items.py` | 229 | Item base class + 3 types: EnergyCellItem, HackBoosterItem, EMPPulseItem, create_item factory |
| `src/inventory.py` | 413 | Inventory (8-slot, stacking), EquipmentManager (Q/R slots, cooldowns), ItemPickup (world entity) |
| `src/audio.py` | 217 | AudioManager: music (looping), SFX (one-shot), volume control (master/music/sfx), graceful fallback |
| `src/menu.py` | 283 | MainMenu: animated particles, neon title, buttons with click SFX |
| `src/settings.py` | ~120 | SettingsMenu: volume slider wired to AudioManager |
| `src/__init__.py` | ~10 | Package initialiser |
| `generate_placeholder_audio.py` | ~200 | Generates 22 placeholder WAV files as sine-wave tones |
| `Dockerfile` | 50 | Docker container: python:3.11-slim, system deps, pip install, run main.py |
| `requirements.txt` | 12 | Single dependency: `ursina` |

---

## 13. DOCUMENT CHANGE LOG

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | April 2026 | Aimtech Development Team | Initial SRS — comprehensive documentation of Phases 1–7; functional requirements for all 12 systems; non-functional requirements; 10 use cases; data model; technology stack; file structure |

---

## 14. APPROVAL & SIGN-OFF

By signing below, each stakeholder confirms they have reviewed this Systems Requirements Specification v1.0 and approve it as the authoritative basis for continued development.

| Role | Name | Date | Signature/Initial |
|---|---|---|---|
| Project Owner / Lead Developer | Aimtech | April 2026 | |
| QA Lead | | | |
| Technical Reviewer | | | |
| Documentation Lead | | | |

---

© Aimtech — AIM: Cyber Reign — All Rights Reserved
