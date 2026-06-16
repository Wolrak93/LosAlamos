# LosAlamos — Cycle 1 Design Specification

**Date:** 2026-06-16  
**Scope:** Full Cycle 1 — Engine, Bots, Main Menu, Game Screen  
**Status:** Approved by user

---

## 1. Architecture Overview

```
src/
  engine/
    board.py          # BitBoard class, position representation
    move.py           # Move dataclass
    movegen.py        # Legal move generation
    gamestate.py      # Check/mate/draw detection, game loop logic
    zobrist.py        # Hashing for repetition detection
  bots/
    base.py           # Bot abstract base class
    random_bot.py     # RandomBot
    greedy_bot.py     # GreedyBot
  gui/
    constants.py      # Colors, sizes, asset paths
    assets.py         # Sprite loader
    main_menu.py      # MainMenuScreen
    game_screen.py    # GameScreen
    widgets.py        # Reusable UI elements (clock, eval bar, move history)
  main.py             # Entry point, screen manager
tests/
  test_movegen.py
  test_gamestate.py
  test_bots.py
```

---

## 2. Engine — Bitboard Representation

### Board State

Each position is represented by **10 bitboards** (one per piece type per color),
stored as Python `int` (64-bit semantics, upper 28 bits always zero for 6×6).

```
Piece types: PAWN, KNIGHT, ROOK, QUEEN, KING  (no bishops)
Colors:      WHITE, BLACK
```

Square indexing: `sq = rank * 6 + file`, rank 0 = row 1 (White's back rank).

```
rank 5 (row 6): squares 30–35  ← Black's back rank
rank 0 (row 1): squares  0– 5  ← White's back rank
```

### Additional State Fields

| Field | Type | Purpose |
|---|---|---|
| `side_to_move` | `Color` | WHITE or BLACK |
| `halfmove_clock` | `int` | 50-move rule counter |
| `position_history` | `list[int]` | Zobrist hashes for repetition detection |
| `ply` | `int` | Total half-moves played |

### Piece Values

| Piece | Value |
|---|---|
| Pawn | 1 |
| Knight | 3 |
| Rook | 5 |
| Queen | 9 |

---

## 3. Move Generation

### Move Dataclass

```python
@dataclass
class Move:
    from_sq: int
    to_sq: int
    piece: PieceType
    color: Color
    captured: PieceType | None = None
    promotion: PieceType | None = None  # QUEEN, ROOK, or KNIGHT only
```

### Rules per Piece

| Piece | Movement |
|---|---|
| Pawn | One step forward; diagonal capture; promotion on rank 5 (White) / rank 0 (Black). No double-step, no en passant. |
| Knight | Pre-computed attack table (L-shapes, wrap-aware for 6×6). |
| Rook | Sliding ray attacks: horizontal + vertical. |
| Queen | Sliding ray attacks: horizontal + vertical + diagonal (standard Queen). |
| King | Pre-computed attack table (one step any direction). |

Legal move filter: a move is legal only if the moving side's king is not in check after the move (make/unmake approach).

---

## 4. Game State & Draw Detection

| Condition | Handling |
|---|---|
| Check | King is attacked by any opponent piece. |
| Checkmate | Side to move is in check and has no legal moves. |
| Stalemate | Side to move is not in check but has no legal moves → draw. |
| Insufficient material | King alone **or** King + Knight → draw. |
| Threefold repetition | Current Zobrist hash appears 3× in `position_history` → draw. |
| 50-move rule | `halfmove_clock` reaches 100 (100 half-moves = 50 full moves) → draw. |
| Time-out | Losing side's clock reaches 0:00. Exception: if opponent has insufficient material → draw. |

---

## 5. Starting Positions

| Mode | Description |
|---|---|
| Normal | White: R-N-Q-K-N-R on rank 0. Black: mirrored on rank 5. Pawns on rank 1 / rank 4. |
| Random Symmetric | Both sides get the same randomly shuffled back rank (R/N/Q/K/N/R, King always between Rooks is NOT required — full random). |
| Random Asymmetric | White and Black each get an independently shuffled back rank. |

---

## 6. Bots

### RandomBot
Selects a uniformly random move from the legal move list.

### GreedyBot

Priority order (highest first):

1. **Checkmate in 1** — iterate all legal moves, play each, check if opponent is in checkmate. If found, play it immediately.
2. **Best material gain** — score each move by: `captured_piece_value + promotion_gain`. `promotion_gain` = value of promoted piece − pawn value (e.g., promotion to Queen = 9 − 1 = +8). Play the highest-scoring move.
3. **Tie-break** — random among equal-score moves.

Both bots implement the abstract `Bot` base class with a single method:
```python
def choose_move(self, board: BitBoard) -> Move: ...
```

---

## 7. Visual Design Language

| Element | Value |
|---|---|
| Background | `#f5f0e8` (warm cream) |
| Primary accent | `#3d5a3e` (dark green) |
| Secondary / border | `#c8b89a` (warm tan) |
| Card background | `#faf6ee` |
| Font | Georgia, serif |
| Board light square | `#f0d9b5` |
| Board dark square | `#b58863` |
| Selected piece | `#f6f669` (yellow) |
| Legal move highlight | `#cdd16f` (yellow-green dot) |
| Active clock | `#3d5a3e` bg, white text |
| Inactive clock | `#c0b09a` bg, cream text |
| Evaluation bar (white side) | `#f0d9b5` fill on dark `#5a3a1a` track |

Window size: **900 × 650 px**, non-resizable in Cycle 1.

---

## 8. Main Menu Screen

### Layout: Two Columns

```
┌─────────────────────────────────────────────────────┐
│                    LOS ALAMOS                        │  ← Title
│                 Schachvariante · 6×6                 │  ← Subtitle
│─────────────────────────────────────────────────────│
│  Left column (flex 3)      │  Right column (flex 2)  │
│                            │                         │
│  WEISS                     │  [AUFSTELLUNG label]    │
│  [Dropdown: Mensch ▾]      │                         │
│  [Name input]              │  ┌─ Mini Board 6×6 ─┐   │
│                            │  │  (decorative)     │   │
│  SCHWARZ                   │  └───────────────────┘   │
│  [Dropdown: RandomBot ▾]   │                         │
│  [Name input]              │  [ Normal         ]     │
│  ─────────────────         │  [ Sym. Zufall     ]     │
│  ZEIT & INKREMENT          │  [ Asym. Zufall    ]     │
│  [__ min]  +  [__ sek]     │                         │
│  (leer = keine Zeitk.)     │                         │
│                            │                         │
│  [▶  Match starten]        │                         │
└─────────────────────────────────────────────────────┘
```

### Dropdown Options
- `Mensch` / `RandomBot` / `GreedyBot`

### Time Control
- Two integer fields: **minutes** (0–99) and **increment seconds** (0–60).
- Both empty or zero → no time control (clock hidden in game screen).

### Starting Position
- Clicking a position button highlights it (border: `#3d5a3e`, bg: `#eef2ee`).
- Default: Normal.

---

## 9. Game Screen

### Layout: Three Columns

```
┌──────────────┬──────────────────────┬────────────────┐
│              │  RandomBot           │  ZUGHISTORIE   │
│              │  RandomBot · Schwarz │  1. c3   c4    │
│  6×6 BOARD   │  [clock: inactive]   │  2. Nc3  Nd4   │
│              │  ♙♙ +2               │  3. Qb2  Rc6   │
│  coordinates │  ─── EVAL SCHWARZ ── │  ...           │
│  (a-f, 1-6)  │  [bar]   −0.3 ♙     │  7. c4   …     │
│              │  ─────────────────── │                │
│              │  [← Zurück zum Menü] │                │
│              │  ─────────────────── │                │
│              │  ─── EVAL WEISS ──── │                │
│              │  [bar]   +0.5 ♙      │                │
│              │  —                   │                │
│              │  Joachim             │                │
│              │  Mensch · Weiß · Zug │                │
│              │  [clock: active]     │                │
└──────────────┴──────────────────────┴────────────────┘
```

### Board Details
- Square size: **88 px** → board renders at 528 × 528 px.
- Coordinate labels: rank numbers (1–6) left of board, file letters (a–f) below.
- White always at bottom (rank 1 = bottom row).
- Click to select a piece → legal moves highlighted with a dot (empty squares) or colored square (captures).
- Click a highlighted square → execute the move.

### Info Panel (Middle Column)
- **Captured pieces:** shown as icons of extra pieces captured (material difference). If equal material: `—`. If ahead: e.g., `♟♟ +2`.
- **Eval bar:** horizontal bar, white fills from left proportional to advantage. Shows numeric value like `+0.5 ♙`. In Cycle 1: shows material balance. Placeholder for engine eval in Cycle 2.
- **Two separate eval bars** — one per player, labeled "Eval Schwarz" / "Eval Weiß". In Cycle 1 both bars show material balance (mirrored perspective: +0.5 for White = −0.5 for Black). In Cycle 2+ each bar shows that bot's own engine evaluation.
- **Back button:** centered between the two player sections.
- **Move history:** PGN-style notation, current half-move highlighted in `#cdd16f`. Scrolls automatically to show latest move.

---

## 10. Promotion UI

When a White pawn reaches rank 5 (or Black pawn reaches rank 0):

- The rest of the board is **dimmed** (opacity 0.55).
- Three circles appear **overlaid on the promotion column**, stacked from the promotion square downward (for White) or upward (for Black):
  - Circle 1 (promotion square): Queen
  - Circle 2 (next square): Rook
  - Circle 3 (next square): Knight
- Each circle: 30 px diameter, white background, piece symbol.
- Hovered circle: orange background (`#e8a020`), white symbol.
- Click → promotes and returns board to normal.
- **Bot promotion:** no dialog — GreedyBot always promotes to Queen (highest value); RandomBot promotes randomly.

---

## 11. Game Over Overlay

Modal overlay centered over the game screen, semi-transparent backdrop.

```
┌─────────────────────┐
│    ♔ / 🤝           │  ← icon
│  Weiß gewinnt       │  ← result
│  Schachmatt         │  ← reason
│                     │
│  [Neues Spiel] [←]  │  ← buttons
└─────────────────────┘
```

**Result titles:** "Weiß gewinnt" / "Schwarz gewinnt" / "Remis"

**Reason strings:**
- Schachmatt
- Patt
- Zeit abgelaufen
- Unzureichendes Material
- Dreifache Stellungswiederholung
- 50-Züge-Regel

**Buttons:**
- "Neues Spiel" → restarts with the same settings from the previous game (no return to menu).
- "← Menü" → returns to Main Menu.

---

## 12. Pygame Technical Notes

- **Screen manager:** a simple `current_screen` variable; `MainMenuScreen` and `GameScreen` each implement `handle_event()`, `update()`, `draw()`.
- **Clock:** pygame `Clock` ticks at 60 FPS. Game clock decrements in `update()` using `dt` (delta time in seconds). After each move, the increment is added to the moving side's clock before the turn switches.
- **Bot moves:** executed via `pygame.time.set_timer` with a short delay (e.g., 300 ms) so the board renders before the bot responds. No threading.
- **Assets:** sprites loaded once at startup via `assets.py`, stored in a dict keyed by `(Color, PieceType)`.
