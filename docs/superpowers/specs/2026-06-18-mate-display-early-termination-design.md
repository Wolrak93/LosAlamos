# Design Spec: Mate Display & Early Bot Termination

**Date:** 2026-06-18
**Branch:** development

## Goal

1. Display "Matt in N" instead of a raw score (e.g. +999.90) when the MinimaxBot detects a forced checkmate.
2. Allow the bot to terminate its search early once a forced mate is confirmed, without waiting for the time budget to expire.

## Scope

- MinimaxBot only. MCTSBot uses win-rate-based eval and never produces mate scores near `_MATE`.
- Applies to both sides (Weiß and Schwarz).

---

## 1. Data Model — `src/bots/progress.py`

Add one new field to `BotProgress`:

```python
mate_in: int | None = None
```

**Semantics:**
- `None` — no forced mate detected
- `+N` (positive) — White delivers mate in N full moves
- `-N` (negative) — Black delivers mate in N full moves
- Sign convention is identical to `eval`: positive = White advantage.

No existing fields are changed.

---

## 2. Bot Logic — `src/bots/minimax_bot.py`

### Mate detection threshold

`_MATE = 100_000` centipawns. A score counts as a mate score when:

```python
abs(best_score) >= _MATE - _MAX_DEPTH
```

(`_MAX_DEPTH = 20`, so threshold = 99,980 cp — safely above any material evaluation.)

### Mate distance formula

```
ply        = _MATE - abs(best_score)   # half-moves to mate from root
moves      = ceil(ply / 2)             # full moves
sign       = +1 if White wins else -1
mate_in    = sign * moves
```

Example: score 99,990 cp → ply = 10 → moves = 5 → "Matt in 5".

### Changes to `choose_move`

After each completed depth iteration, inside the existing `if progress is not None` block:

1. If `abs(best_score) >= _MATE - _MAX_DEPTH`: compute and store `progress.mate_in`.
2. `break` out of the iterative deepening loop — result is proven, no further search needed.
3. If score is below threshold: set `progress.mate_in = None` (clears any stale value from a previous iteration).

The thread exits naturally; `game_screen.py` detects thread completion at the next poll and plays the move immediately.

---

## 3. GUI Display — `src/gui/game_screen.py`

### New state

```python
self._last_mate_in: dict[Color, int | None] = {Color.WHITE: None, Color.BLACK: None}
```

Updated at thread-end alongside `_last_eval`:

```python
if self._bot_progress is not None:
    if self._bot_progress.eval is not None:
        self._last_eval[color] = self._bot_progress.eval
    self._last_mate_in[color] = self._bot_progress.mate_in
```

### Eval string in `draw_player`

Existing logic picks `current_eval` from either live progress or `_last_eval`. The same source is used for `current_mate_in` (live `self._bot_progress.mate_in` during thinking, `self._last_mate_in[color]` otherwise).

String generation:

```python
if current_mate_in is not None:
    eval_str = f"Matt in {abs(current_mate_in)}"
else:
    sign = "+" if current_eval > 0 else ""
    eval_str = f"{sign}{current_eval:.2f}"
```

Color derivation is unchanged — still based on `current_eval` value (ACCENT / red / TEXT_MUTED).

The eval bar is unchanged; it continues to use `current_eval`.

---

## Files Changed

| File | Change |
|---|---|
| `src/bots/progress.py` | Add `mate_in: int | None = None` |
| `src/bots/minimax_bot.py` | Detect mate score, set `progress.mate_in`, break loop |
| `src/gui/game_screen.py` | Add `_last_mate_in`, use `mate_in` for display string |

---

## Out of Scope

- MCTSBot mate detection
- Clock time adjustment when bot terminates early (clock stops when move is played, which is the existing behaviour)
- Any changes to the eval bar rendering
