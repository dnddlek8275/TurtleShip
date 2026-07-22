# TurtleShip

A five-stage naval shooting game built with Python and Pygame.

The player controls a turtle ship, clears waves of enemy vessels, and fights a boss with a distinct projectile pattern at the end of each stage. The game combines keyboard or mouse shooting, collision-based combat, stage progression, optional image and audio assets, and a responsive game window.

## Gameplay

- Move inside the playable area while avoiding enemies and hostile projectiles.
- Destroy 45 regular enemies to summon the current stage boss.
- Defeat the boss to advance to the next stage.
- Clear all five stages to finish the game.
- Later stages increase enemy speed, health, spawn rate, boss health, and shield strength.

The player begins with 140 HP. The game tracks score, remaining HP, stage progress, enemy kills, boss health, and boss shields.

## Stages

| Stage | Encounter | Boss Pattern |
| --- | --- | --- |
| 1. Fog Strait | Fog Command Ship | Three-way split barrage |
| 2. Whirlpool Waters | Whirlpool General Ship | Horizontal spread barrage |
| 3. Fire Ship Breakthrough | Fire Ship Commander | Flame fan and split projectiles |
| 4. Black Fleet | Black Siege Ship | Tracking sniper attacks |
| 5. Flagship Showdown | Enemy Flagship | Shield regeneration and storm barrage |

## Controls

| Input | Action |
| --- | --- |
| Arrow keys or WASD | Move the player ship |
| Space | Fire |
| Left mouse button | Fire during gameplay |
| Enter or Space | Start or restart |
| P | Pause or resume |
| Escape | Return to the menu; exit from menu and result screens |

The game starts in a maximized resizable window. Pass `--windowed` to use the default window size.

## Requirements

- Python 3
- Pygame

Install Pygame:

```bash
pip install pygame
```

## Run

```bash
python basic.py
```

Windowed mode:

```bash
python basic.py --windowed
```

## Asset System

Assets are optional. The game searches for supported files and continues with drawn fallbacks when a matching image or sound is unavailable.

### Images

Supported formats: PNG, JPG, and JPEG.

Common names include `splash`, `main_menu`, `game_background`, `player`, `enemy`, `mini_boss`, and `boss_room`. Stage-specific assets use names such as `enemy_stageN`, `boss_stageN`, `bullet_stageN`, and `projectile_stageN`, where `N` is 1 through 5.

### Audio

Supported formats: MP3, OGG, and WAV.

The loader recognizes common background music and sound effects as well as stage-specific shooting, hit, boss, and destruction sounds.

## Project Structure

```text
.
├── assets/
│   ├── audio/
│   │   └── README.md
│   └── images/
│       ├── README.md
│       ├── game_background.png
│       ├── main_menu.png
│       └── player.png
├── basic.py
└── README.md
```

## Implementation Notes

`basic.py` contains the complete game loop, input handling, stage definitions, spawning logic, projectile patterns, collision detection, scoring, rendering, and audio loading. The loop runs at 60 FPS and supports live window resizing.

The repository is a fork of `mingyu2157/TurtleShip`.
