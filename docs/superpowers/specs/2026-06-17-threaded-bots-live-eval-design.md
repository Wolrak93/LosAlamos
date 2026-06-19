# Design Spec: Threaded Bots & Live Eval Display

**Date:** 2026-06-17
**Status:** Approved

## Problem

1. Bot `choose_move()` blocks the main thread. While thinking, the active player's clock does not tick. When the bot finishes and the turn switches, `clock.tick(60)` returns a large accumulated `dt` that is charged to the *other* player's clock.
2. Bot-vs-Bot matches show a frozen UI with no feedback.
3. The eval bar/number displays raw material count, not the bot's actual search evaluation.
4. No live depth or simulation count is shown during thinking.

## Goals

- Bot clock ticks in real time while the bot thinks.
- UI remains responsive (clock animates, frame renders) during bot thinking.
- Info panel shows the bot's actual eval, updated live during search.
- MinimaxBot shows current search depth; MCTSBot shows simulation count.
- GreedyBot continues to show material eval (that is its eval).
- RandomBot: no eval shown (unchanged).

## Architecture Overview

All bots run in a background daemon thread. The main thread continues to process frames normally. A `BotProgress` shared object allows the bot to push live updates; the main thread reads it each frame for display.

## Section 1: Threading in `game_screen.py`

### New State Fields

```python
_bot_thread: threading.Thread | None = None
_bot_progress: BotProgress | None = None
_bot_result: list[Move | None]          # single-element mutable container
_last_eval: dict[Color, float | None]   # persists eval between moves
```

### Flow

1. `_BOT_MOVE_EVENT` fires (unchanged 300 ms cosmetic delay).
2. `handle_event()` calls `_start_bot_thread()` instead of `_execute_bot_move()`.
3. `_start_bot_thread()`:
   - Copies the board (`self._board.copy()`).
   - Creates a fresh `BotProgress()`.
   - Calculates the time budget.
   - Starts a `daemon=True` thread that calls `bot.choose_move(board_copy, budget, progress)` and stores the result in `_bot_result[0]`.
4. `update(dt)` checks every frame:
   ```python
   if self._bot_thread is not None and not self._bot_thread.is_alive():
       move = self._bot_result[0]
       color = self._board.active_color
       if self._bot_progress.eval is not None:
           self._last_eval[color] = self._bot_progress.eval
       self._bot_thread = None
       self._bot_progress = None
       self._make_move(move)
   ```
5. Clock logic in `update(dt)` is unchanged — it already ticks the active player's clock each frame. With the main loop no longer blocked, it works correctly.

### Cancellation

When the user returns to the menu, the current screen is replaced. The daemon thread continues briefly but its result is never applied (no reference to the old screen remains). No explicit cancellation needed.

## Section 2: `BotProgress` Dataclass and Bot Changes

### New File: `src/bots/progress.py`

```python
from dataclasses import dataclass, field

@dataclass
class BotProgress:
    depth: int | None = None    # Minimax: completed search depth
    eval: float | None = None   # eval in pawn units (positive = white advantage)
    sims: int | None = None     # MCTS: total simulations completed
```

### Updated `choose_move` Signature (all bots)

```python
def choose_move(
    self,
    board: BitBoard,
    time_budget_seconds: float | None = None,
    progress: BotProgress | None = None,
) -> Move:
```

The `progress` parameter is optional and defaults to `None` so existing call sites (e.g. tests) require no change.

### Per-Bot Behavior

| Bot | `progress.depth` | `progress.eval` | `progress.sims` | When updated |
|---|---|---|---|---|
| MinimaxBot | current depth `d` | `best_score` from that depth | — | after each completed iterative-deepening level |
| MCTSBot | — | `best_child.score / best_child.visits` | running total | every 100 simulations |
| GreedyBot | — | material score of chosen move | — | once, before returning |
| RandomBot | — | — | — | never |

### MinimaxBot Detail

In the iterative deepening loop, after each depth `d` completes and a `best_move` is confirmed:

```python
if progress is not None:
    progress.depth = d
    progress.eval = best_score
```

`best_score` is in the same pawn units already used by the evaluator. Positive = white advantage.

### MCTSBot Detail

Inside the simulation loop, after every 100 iterations:

```python
if progress is not None and total_sims % 100 == 0:
    best = max(root.children, key=lambda c: c.visits)
    progress.sims = total_sims
    progress.eval = best.score / best.visits if best.visits > 0 else 0.0
```

`score / visits` is already in pawn units because `_simulate()` uses the same board evaluator as MinimaxBot.

### GreedyBot Detail

After selecting the best move, before returning:

```python
if progress is not None:
    progress.eval = best_score  # material score in pawn units
```

## Section 3: Eval Display in the Info Panel

### `_last_eval` Persistence

`_last_eval: dict[Color, float | None]` is initialized to `{WHITE: None, BLACK: None}`. After each bot move, `_last_eval[color]` is updated from `progress.eval`. This value persists and is shown between moves.

### Eval Source per Bot

| Bot | Eval source | Bar scale |
|---|---|---|
| MinimaxBot | `BotProgress.eval` (actual search eval) | −5 to +5 pawn units, clamped |
| MCTSBot | `BotProgress.eval` (avg simulation eval) | −5 to +5 pawn units, clamped |
| GreedyBot | `BotProgress.eval` (material score) | −5 to +5 pawn units, clamped |
| RandomBot | — | no bar shown |

The current material-based eval calculation (`white_mat - black_mat`) is removed and replaced by reading `_last_eval` or `_bot_progress.eval`.

### Live Display During Thinking

When `_bot_thread is not None`, the info panel reads live from `_bot_progress`:

- **Eval number:** `_bot_progress.eval` (or `_last_eval` if `None` not yet set)
- **Eval bar:** derived from live eval, clamped to [−5, +5]
- **Depth/Sims label** (new line below eval number):
  - MinimaxBot: `"Tiefe {depth}"` (e.g. `"Tiefe 5"`)
  - MCTSBot: `"{sims:,} Sims"` (e.g. `"1 234 Sims"`)
  - GreedyBot / RandomBot: nothing

### Display When Not Thinking

- Eval number: `_last_eval[color]` (last completed move's eval); `"—"` if `None`
- Eval bar: derived from `_last_eval[color]`; neutral (50/50) if `None`
- Depth/Sims label: hidden

### Eval Bar Formula

```python
WHITE_PERSPECTIVE_EVAL = eval if color == WHITE else -eval
clamped = max(-5.0, min(5.0, WHITE_PERSPECTIVE_EVAL))
white_frac = (clamped + 5.0) / 10.0
```

The white portion of the bar grows as the position favors white.

## Files Affected

| File | Change |
|---|---|
| `src/bots/progress.py` | **New** — `BotProgress` dataclass |
| `src/bots/base.py` | Update `choose_move` signature |
| `src/bots/minimax_bot.py` | Write to `progress` in iterative deepening loop |
| `src/bots/mcts_bot.py` | Write to `progress` every 100 sims |
| `src/bots/greedy_bot.py` | Write material eval to `progress` once |
| `src/bots/random_bot.py` | Accept `progress` param, do nothing |
| `src/gui/game_screen.py` | Thread management, `_last_eval`, updated info panel drawing |

## Out of Scope

- Cancellation signal to stop a bot mid-search (bot respects its own time budget)
- Showing expected best line (PV) in the UI
- Win-probability percentage display
