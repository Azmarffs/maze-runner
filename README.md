# Maze Runner - Escape from AI

A retro-styled, AI-driven maze escape game built with Pygame. Navigate a procedurally generated maze, avoid monsters, collect powerups, and escape before you are caught by the mutated monsters!

---

## Table of Contents
- [Features](#features)
- [Installation & Running](#installation--running)
- [Game Structure](#game-structure)
- [Sprites & Animation](#sprites--animation)
- [Maze Generation & Braiding](#maze-generation--braiding)
- [Player Movement](#player-movement)
- [Monster AI](#monster-ai)
- [Powerups](#powerups)
- [UI & Visual Effects](#ui--visual-effects)
- [Configuration](#configuration)
- [Assets](#assets)

---

## Features
- **Procedurally generated mazes** with multiple paths (braided for loops).
- **AI monsters** that chase the player using A* pathfinding.
- **Powerups**: Speed boost (yellow, lightning) and shield (blue, shield).
- **Animated player and monster sprites**.
- **Storm events** that limit vision and add challenge.
- **Responsive controls** (WASD/Arrow keys).
- **Single-click launch (see below for building an executable).**

---

## Installation & Running

1. **Install Python 3.8+** and [Pygame](https://www.pygame.org/):
   ```sh
   pip install pygame
   ```
2. **Run the game:**
   ```sh
   python main.py
   ```

---

## Game Structure
- **main.py**: Entry point, sets up the window and main loop.
- **game.py**: Main game logic, state management, UI, and event handling.
- **maze.py**: Maze generation, braiding (loops), and powerup placement.
- **player.py**: Player movement, animation, health, and powerup logic.
- **monster.py**: Monster AI, pathfinding, and animation.
- **powerups.py**: Powerup types, effects, and rendering.
- **particles.py**: Particle system for visual effects.
- **config.py**: All game constants, colors, and settings.
- **assets/**: Sprite images and enemy spritesheet.

---

## Sprites & Animation
- **Player**: Uses 4-directional animated sprites (idle and walk) loaded from `assets/elf_*` folders.
  - Each direction (up, down, left, right) has 1 idle and 8 walk frames.
- **Monster**: Uses a spritesheet (`assets/enemy_spritesheet.png`) with 5 animation frames, rotated/flipped for direction.
- **Powerups**:
  - **Speed**: Yellow circle with a black lightning bolt.
  - **Shield**: Blue circle with a white border and shield overlay.

---

## Maze Generation & Braiding
- **Algorithm**: Recursive backtracking for perfect maze generation.
- **Braiding**: After generation, random walls are removed to create loops and multiple paths (`braid_chance=0.12`).
- **Start/Exit**: Randomly chosen at distant points in the maze.
- **Powerups**: Placed randomly on open cells, not at start/exit.

---

## Player Movement
- **Controls**: WASD or Arrow keys.
- **Movement**: Smooth interpolation between cells; only one move at a time unless at target.
- **Speed Boost**: Doubles movement speed for a limited time.
- **Health**: 100%, reduced by 20% per monster hit. Temporary invulnerability after hit.
- **Sprite Animation**: Direction and state (idle/walk) determine frame.

---

## Monster AI
- **Pathfinding**: Uses A* (with Manhattan distance heuristic) to chase the player.
- **Behavior**:
  - Monsters periodically recalculate the shortest path to the player.
  - If frozen (by shield powerup), they stop moving for a duration.
  - Multiple monsters can be present, each with slightly different speed.
- **Animation**: Directional, with frame cycling.

---

## Powerups
- **Speed Powerup (Yellow, Lightning)**:
  - Grants a speed boost for a few seconds.
  - Visually: yellow circle with a lightning bolt.
- **Shield Powerup (Blue, Shield)**:
  - Grants a shield for 10 seconds (timer shown in UI).
  - Absorbs the next monster hit, then disappears.
  - Visually: blue circle, white border, shield overlay.
- **Collection**: Powerups are picked up by moving onto their cell.

---

## UI & Visual Effects
- **Health Bar**: Terminal-style, bottom left, green.
- **Shield Timer**: Large blue label and icon above health bar when active.
- **Speed Boost**: Yellow label with timer.
- **CRT/Terminal Look**: Scanlines, glow, and retro fonts.
- **Particles**: Used for movement, powerup, win, and game over effects.
- **Storms**: Periodically darken the screen, limiting vision.

---

## Configuration
All settings are in `config.py`:
- Screen size, FPS, maze size, colors, powerup durations, monster speed, etc.
- Easily tweakable for custom difficulty or look.

---

## Assets
- **Player Sprites**: `assets/elf_*` folders (PNG frames for each direction and state).
- **Monster Spritesheet**: `assets/enemy_spritesheet.png`.
- **Powerup Icons**: Drawn in code, not loaded from file.

---


## AI Details
- **Monster Pathfinding**: Each monster uses A* to find the shortest path to the player, recalculating every move. The heuristic is Manhattan distance, and only open cells are considered.
- **Player Movement**: Smooth, grid-based, with interpolation for animation. Speed boost is handled by doubling the interpolation rate.
- **Powerup Logic**: Powerups are objects on the maze grid. Speed and shield effects are managed by timers on the player object.
- **Maze Braiding**: After initial maze generation, random wall removal creates loops, making the maze less linear and more interesting for both player and AI.

---
