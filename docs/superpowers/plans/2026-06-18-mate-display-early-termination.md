# Mate Display & Early Bot Termination Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show "Matt in N" in the eval panel when the MinimaxBot finds a forced checkmate, and terminate the bot's search loop early once the mate is confirmed.

**Architecture:** Add `mate_in: int | None` to `BotProgress` as the explicit signal; the bot sets it and breaks its loop; the GUI reads it to format the display string. Three focused changes, no new abstractions.

**Tech Stack:** Python, pygame, pytest, uv

---

## File Map

| File | Change |
|---|---|
| `src/bots/progress.py` | Add `mate_in: int | None = None` field |
| `src/bots/minimax_bot.py` | Add `import math`; detect mate score; set `progress.mate_in`; `break` loop |
| `src/gui/game_screen.py` | Add `_last_mate_in` state; capture it at thread-end; use it for display string |
| `tests/test_progress.py` | Tests for new `mate_in` field |
| `tests/test_minimax.py` | Tests: bot sets `mate_in`, bot exits early on forced mate |

---

## Task 1: Add `mate_in` to BotProgress

**Files:**
- Modify: `tests/test_progress.py`
- Modify: `src/bots/progress.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_progress.py`:

```python
def test_bot_progress_mate_in_defaults_to_none():
    p = BotProgress()
    assert p.mate_in is None


def test_bot_progress_mate_in_can_be_set():
    p = BotProgress()
    p.mate_in = 3
    assert p.mate_in == 3
    p.mate_in = -2
    assert p.mate_in == -2
```

- [ ] **Step 2: Run tests — expect FAIL**

```
uv run pytest tests/test_progress.py -v
```

Expected: `AttributeError: 'BotProgress' object has no attribute 'mate_in'`

- [ ] **Step 3: Add the field**

In `src/bots/progress.py`, add the new field after `sims`:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BotProgress:
    depth: int | None = None    # Minimax: completed search depth
    eval: float | None = None   # pawn units, positive = White advantage
    sims: int | None = None     # MCTS: total simulations completed
    mate_in: int | None = None  # Full moves to forced mate; +N=White wins, -N=Black wins
```

- [ ] **Step 4: Run tests — expect PASS**

```
uv run pytest tests/test_progress.py -v
```

Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bots/progress.py tests/test_progress.py
git commit -m "feat: add mate_in field to BotProgress"
```

---

## Task 2: MinimaxBot — detect mate score and exit early

**Files:**
- Modify: `tests/test_minimax.py`
- Modify: `src/bots/minimax_bot.py`

The position used in existing tests (and reused here):
- White King a1 (sq 0), Black King f6 (sq 35), White Rook f1 (sq 5), White Queen a5 (sq 24)
- White to move — mate in 1 exists (Qa6#)

`_MATE = 100_000`, `_MAX_DEPTH = 20`. A score is a mate score when `abs(score) >= _MATE - _MAX_DEPTH = 99_980`.

Mate distance formula:
```
ply   = _MATE - abs(best_score)    # half-moves to mate
moves = ceil(ply / 2)              # full moves (mate in N)
sign  = +1 if White wins, -1 if Black wins
```

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_minimax.py`:

```python
def test_minimax_sets_mate_in_when_checkmate_found():
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)
    b.set_piece(5, Color.WHITE, PieceType.ROOK)
    b.set_piece(24, Color.WHITE, PieceType.QUEEN)
    from bots.progress import BotProgress
    bot = _make_minimax()
    p = BotProgress()
    bot.choose_move(b, time_budget_seconds=5.0, progress=p)
    assert p.mate_in is not None
    assert p.mate_in > 0  # White wins


def test_minimax_exits_early_on_forced_mate():
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)
    b.set_piece(5, Color.WHITE, PieceType.ROOK)
    b.set_piece(24, Color.WHITE, PieceType.QUEEN)
    from bots.progress import BotProgress
    bot = _make_minimax()
    p = BotProgress()
    start = time.monotonic()
    bot.choose_move(b, time_budget_seconds=60.0, progress=p)
    elapsed = time.monotonic() - start
    assert elapsed < 5.0
    assert p.mate_in is not None
```

- [ ] **Step 2: Run tests — expect FAIL**

```
uv run pytest tests/test_minimax.py::test_minimax_sets_mate_in_when_checkmate_found tests/test_minimax.py::test_minimax_exits_early_on_forced_mate -v
```

Expected: `AssertionError: assert None is not None`

- [ ] **Step 3: Update `choose_move` in `src/bots/minimax_bot.py`**

Add `import math` at the top (after the existing `import time`):

```python
import math
import time
```

Replace the `choose_move` method (lines 121–147) with:

```python
def choose_move(
    self,
    board: BitBoard,
    time_budget_seconds: float | None = None,
    progress: BotProgress | None = None,
) -> Move:
    budget = 120.0 if time_budget_seconds is None else time_budget_seconds
    start = time.monotonic()
    deadline = start + budget
    soft_deadline = start + budget * 0.9
    tt: dict = {}
    best_move: Move | None = None

    for depth in range(1, _MAX_DEPTH + 1):
        if time.monotonic() >= soft_deadline:
            break
        result = self._search_root(board, depth, deadline, tt)
        if result is not None:
            best_move, best_score = result
            if progress is not None:
                eval_white = (
                    best_score if board.side_to_move == Color.WHITE else -best_score
                )
                progress.depth = depth
                progress.eval = eval_white / 100.0
                if abs(best_score) >= _MATE - _MAX_DEPTH:
                    ply = _MATE - abs(best_score)
                    moves = math.ceil(ply / 2)
                    sign = 1 if eval_white > 0 else -1
                    progress.mate_in = sign * moves
                    break
                else:
                    progress.mate_in = None

    if best_move is None:
        best_move = generate_legal_moves(board)[0]
    return best_move
```

- [ ] **Step 4: Run tests — expect PASS**

```
uv run pytest tests/test_minimax.py -v
```

Expected: all 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/bots/minimax_bot.py tests/test_minimax.py
git commit -m "feat: detect forced mate in MinimaxBot, set mate_in and exit loop early"
```

---

## Task 3: GUI — display "Matt in N"

**Files:**
- Modify: `src/gui/game_screen.py`

No automated test for rendering. Verified manually by running the app against a mate position.

### 3a — Add `_last_mate_in` state

- [ ] **Step 1: Add `_last_mate_in` to `__init__`**

In `src/gui/game_screen.py`, find the `_last_eval` initialisation (around line 121):

```python
self._last_eval: dict[Color, float | None] = {
    Color.WHITE: None,
    Color.BLACK: None,
}
```

Add `_last_mate_in` directly after it:

```python
self._last_eval: dict[Color, float | None] = {
    Color.WHITE: None,
    Color.BLACK: None,
}
self._last_mate_in: dict[Color, int | None] = {
    Color.WHITE: None,
    Color.BLACK: None,
}
```

### 3b — Capture `mate_in` at thread-end

- [ ] **Step 2: Update the thread-completion poll in `update`**

Find the block around line 155:

```python
if self._bot_thread is not None and not self._bot_thread.is_alive():
    move = self._bot_result[0]
    color = self._board.side_to_move
    if self._bot_progress is not None and self._bot_progress.eval is not None:
        self._last_eval[color] = self._bot_progress.eval
    self._bot_thread = None
    self._bot_progress = None
```

Replace with:

```python
if self._bot_thread is not None and not self._bot_thread.is_alive():
    move = self._bot_result[0]
    color = self._board.side_to_move
    if self._bot_progress is not None and self._bot_progress.eval is not None:
        self._last_eval[color] = self._bot_progress.eval
    if self._bot_progress is not None:
        self._last_mate_in[color] = self._bot_progress.mate_in
    self._bot_thread = None
    self._bot_progress = None
```

### 3c — Use `mate_in` for the display string

- [ ] **Step 3: Update the eval string block in `draw_player`**

Find the block around lines 479–503 inside `draw_player`:

```python
if is_thinking and self._bot_progress is not None:
    current_eval = self._bot_progress.eval
else:
    current_eval = self._last_eval[color]

self._draw_eval_bar(
    surf, pygame.Rect(INFO_X + 8, y, INFO_W - 16, 8), color, current_eval
)
y += 14

if current_eval is not None:
    sign = "+" if current_eval > 0 else ""
    eval_str = f"{sign}{current_eval:.2f}"
    if current_eval > 0:
        eval_color = ACCENT
    elif current_eval < 0:
        eval_color = (160, 60, 60)
    else:
        eval_color = TEXT_MUTED
else:
    eval_str = "—"
    eval_color = TEXT_MUTED
```

Replace with:

```python
if is_thinking and self._bot_progress is not None:
    current_eval = self._bot_progress.eval
    current_mate_in = self._bot_progress.mate_in
else:
    current_eval = self._last_eval[color]
    current_mate_in = self._last_mate_in[color]

self._draw_eval_bar(
    surf, pygame.Rect(INFO_X + 8, y, INFO_W - 16, 8), color, current_eval
)
y += 14

if current_eval is not None:
    if current_mate_in is not None:
        eval_str = f"Matt in {abs(current_mate_in)}"
    else:
        sign = "+" if current_eval > 0 else ""
        eval_str = f"{sign}{current_eval:.2f}"
    if current_eval > 0:
        eval_color = ACCENT
    elif current_eval < 0:
        eval_color = (160, 60, 60)
    else:
        eval_color = TEXT_MUTED
else:
    eval_str = "—"
    eval_color = TEXT_MUTED
```

- [ ] **Step 4: Run full test suite**

```
uv run pytest -v
```

Expected: all tests PASS (no GUI rendering tests affected).

- [ ] **Step 5: Run the app and verify visually**

```
uv run python src/main.py
```

Start a MinimaxBot vs MinimaxBot game. When one side reaches a forced mate, verify:
- Eval panel shows "Matt in N" (e.g. "Matt in 5") instead of "+999.90"
- Bot makes its move immediately without waiting for its full time budget
- Eval bar still renders (based on `current_eval`, unchanged)

- [ ] **Step 6: Commit**

```bash
git add src/gui/game_screen.py
git commit -m "feat: show Matt in N in eval panel when forced mate is detected"
```
