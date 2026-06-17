# Cycle 2 Design — Stärkere Bots

**Date:** 2026-06-17
**Status:** Approved

## Goal

Six named bot personalities combining two search algorithms (Minimax/Alpha-Beta, MCTS) with three
cumulative evaluation tiers (Material, +Positional, +Mobility), all playing at maximum strength
with clock-based time management.

---

## Bot Personalities

| Name | Algorithm | Evaluation |
|---|---|---|
| **Fermi** | Minimax + Alpha-Beta | Material |
| **von Neumann** | Minimax + Alpha-Beta | Material + Positional |
| **Oppenheimer** | Minimax + Alpha-Beta | Material + Positional + Mobility |
| **Feynman** | MCTS | Material |
| **Teller** | MCTS | Material + Positional |
| **Bethe** | MCTS | Material + Positional + Mobility |

All bots play at maximum strength — no artificial weakening.

---

## Architecture

### New files

```
src/bots/
├── evaluator.py       Evaluator class with configurable components
├── minimax_bot.py     Alpha-Beta Minimax with iterative deepening
├── mcts_bot.py        MCTS with evaluator-guided rollouts
└── personalities.py   Factory: creates the 6 named bot instances
```

**`base.py` updated:** `choose_move` gains an optional second parameter:
```python
@abstractmethod
def choose_move(self, board: BitBoard, time_budget_seconds: float | None = None) -> Move: ...
```
`random_bot.py` and `greedy_bot.py` accept and ignore the parameter (no behavior change).

### Data flow

```
personalities.py
  └── MinimaxBot(evaluator=Evaluator(material=True, positional=True, mobility=False), name="von Neumann")
  └── MCTSBot(evaluator=Evaluator(material=True, positional=True, mobility=True), name="Bethe")

MinimaxBot.choose_move(board, time_budget_seconds)
  └── iterative_deepening(board, deadline)
      └── alphabeta(board, depth, α, β)
          └── evaluator.evaluate(board)   ← at leaf nodes

MCTSBot.choose_move(board, time_budget_seconds)
  └── mcts_search(board, deadline)
      └── rollout(board, depth=6) → evaluator.evaluate(board)
```

---

## Evaluator

`Evaluator(material=True, positional=False, mobility=False)`

All components use Centipawn units and are directly addable.

### Component 1 — Material (always active)

Sum of white piece values minus sum of black piece values using existing `PIECE_VALUES` from
`board.py` (P=1, N=3, R=5, Q=9). The Evaluator multiplies by 100 internally to convert to
Centipawn units (P=100, N=300, R=500, Q=900). Existing code outside the Evaluator is unaffected.

### Component 2 — Positional Tables (Piece-Square Tables)

One 6×6 table per piece type, tuned for Los Alamos chess (no bishops, smaller board):

- **Pawns:** bonus for central files (c/d), bonus for advanced ranks
- **Knights:** bonus for center proximity (c3/d3/c4/d4), penalty for edge squares
- **Rooks:** bonus for open files, small bonus in opponent's half
- **Queen:** bonus for center, small penalty in moves 1–5 (anti-early-queen-rush)
- **King (middlegame):** bonus for corner proximity (safety)
- **King (endgame, ≤6 pieces):** bonus for center (activity)

Black tables are the vertical mirror of white tables.

### Component 3 — Mobility

```
mobility_score = (own_legal_moves − opponent_legal_moves) × 0.1 × PAWN_VALUE
```

Weight ≈ 10 Centipawns per extra legal move. Strong signal on the tight 6×6 board.

### Formula

```
score = material + positional_bonus + mobility_bonus
```

Positive = White advantage, negative = Black advantage.

---

## MinimaxBot — Alpha-Beta with Iterative Deepening

### Search

```python
def choose_move(board, time_budget_seconds=120.0):
    deadline = time.monotonic() + time_budget_seconds
    best_move = None
    for depth in range(1, 21):          # hard cap: 20 half-moves
        if time.monotonic() >= deadline * 0.9:
            break
        best_move = alphabeta_root(board, depth, deadline)
    return best_move
```

### Optimizations

| Technique | Purpose |
|---|---|
| Alpha-Beta Pruning | Cuts useless branches — roughly doubles effective search depth |
| Move Ordering | Captures first (MVV-LVA: Most Valuable Victim / Least Valuable Attacker) |
| Transposition Table | Caches evaluated positions via existing `zobrist.py` |
| Quiescence Search | At leaf nodes: extend search with captures-only to avoid horizon effect |

### Quiescence Search

When `depth == 0`, the search does not evaluate immediately. Instead it continues with
captures-only moves until no captures remain (or a depth limit of 4 extra half-moves).
This prevents the engine from evaluating a position as neutral when a piece is hanging.

---

## MCTSBot

### Four phases (repeated until deadline × 0.9)

1. **Selection:** Traverse existing tree nodes using UCT formula:
   `UCT = win_rate + √2 × sqrt(ln(parent_visits) / node_visits)`

2. **Expansion:** Add one unvisited child node.

3. **Simulation (Rollout):** Play out up to 6 half-moves from the expanded node,
   then call `evaluator.evaluate(board)`. The evaluator score is normalized to [0, 1]
   as the rollout result.

4. **Backpropagation:** Propagate the normalized score back through all visited nodes.

### Move selection

After time is up: return the child with the highest `visit_count` (most explored = most trusted).

---

## Time Management

Both bots use the same time budget calculation. The function lives in `personalities.py`
and is called by the GUI before `choose_move`:

```python
def calculate_time_budget(remaining_seconds, move_number, increment_seconds=0):
    if remaining_seconds is None:
        return 120.0                        # no clock: 2 minutes fixed

    if move_number <= 30:
        early_moves_left = max(1, 30 - move_number + 1)
        budget = remaining_seconds * 0.80 / early_moves_left
    else:
        budget = remaining_seconds * 0.10   # 10% of remaining per move

    return budget + increment_seconds
```

The increment is added back to remaining time by the clock after each move (existing behavior).

---

## Main Menu Changes

The player dropdown gains grouping and inline algorithm info:

```
── MENSCH ──
  Mensch
── BASIS-BOTS ──
  RandomBot
  GreedyBot
── WISSENSCHAFTLER ──
  Fermi          Minimax · Material
  von Neumann    Minimax · +Pos
  Oppenheimer    Minimax · +Mob
  Feynman        MCTS · Material
  Teller         MCTS · +Pos
  Bethe          MCTS · +Mob
```

Algorithm info is shown directly in the dropdown (no hover required).
Group separators are non-selectable labels.

---

## Testing

### `tests/test_evaluator.py`
- Material: known position returns expected score (e.g., White has extra queen → +900)
- Positional: knight in center scores higher than knight on edge
- Mobility: position with more legal moves scores higher
- Additivity: combined score equals sum of individual components

### `tests/test_minimax.py`
- Finds checkmate-in-1 reliably
- Does not exceed time budget (measured with `time.monotonic()`)
- Always returns a legal move

### `tests/test_mcts.py`
- Finds checkmate-in-1 with sufficient time
- Does not exceed time budget
- Always returns a legal move

### `tests/test_personalities.py`
- All 6 personalities instantiate without error
- All 6 complete a full game vs RandomBot without crash (short time budget)
