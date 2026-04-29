# Snakes and Ladders

A console-based Snakes and Ladders game written in Python
The board is randomly generated every round, supports 2–4 players (any mix of humans and computer-controlled players), and uses the [`rich `]  (https://github.com/Textualize/rich)library to render a colored ASCII board, banner, and leaderboard.
---

## Features

- Randomized board every round — snake and ladder positions, counts,
  and lengths change every game
- Three difficulty modes that change the snake/ladder ratio:
  - **Easy** — many ladders, few snakes
  - **Medium** — balanced
  - **Hard** — many snakes, few ladders
- 2, 3, or 4 players — any seat may be a human or a CPU
- Choose your die: **6**, **12**, or **20** sides
- Choose your board size: **50** or **100** squares
- Color-coded board:
  - `▼N` red — snake (slides down to square N)
  - `▲N` green — ladder (climbs up to square N)
  - `★` yellow — finish square
  - `P1`–`P4` — players in distinct colors
  - `xN` yellow — N players sharing the same square
- Move history log, viewable after each game
- Per-session leaderboard of the fastest wins
- Replay without restarting the program
- **Exact-roll-to-win** rule — overshooting the final square forfeits
  the move

---

## Requirements

- Python 3.8 or newer
- The `rich` library

Install the one dependency with:

```bash
pip install rich
```

---

## How to run

From the project directory:

```bash
python snakes.py
```

Press `Ctrl+C` at any time to quit cleanly.

---

## How to play

1. **Setup**
   - Choose how many players will play (2–4).
   - For each player, type a name to play as a human, or leave the line
     blank to fill that seat with a CPU.
   - Pick a difficulty, board size, and die.

2. **Each turn**
   - The active player presses **Enter** to roll.  CPU players roll
     automatically.
   - The dice value is added to the player's current square.
   - If the destination square is a snake head (`▼`), the player slides
     down to the snake's tail.
   - If the destination square is a ladder bottom (`▲`), the player
     climbs up to the ladder's top.
   - If the destination square is past the final square, the player
     stays put — you must roll the **exact** number to land on the last
     square.

3. **Winning**
   - The first player to land exactly on the final square wins.
   - The game ends, the winner is recorded on the session leaderboard,
     and you can choose to view the full move history and/or play
     another round.

---

## Project structure

```
Project/
├── snakes.py     # All game code
└── README.md     # This file
```

The single source file is organized into clearly labeled sections:

| Section            | Purpose                                              |
|--------------------|------------------------------------------------------|
| `Player` class     | Bundles each player's name, marker, position, turns  |
| Board generation   | `generate_board(size, difficulty)` builds the board  |
| Display helpers    | `make_cell`, `draw_board`, color and symbol setup    |
| Game logic         | `roll_die`, `take_turn`, `play_round`                |
| Input helpers      | `ask_int`, `ask_choice`, `ask_yes_no`                |
| Setup / main loop  | `setup_game`, `main`, replay handling                |

---
