# Spec: Last-Move Highlight (Board + History)

**Date:** 2026-06-17
**Status:** Approved
**Tests:** B4.7 (history highlight fix), new board feature

---

## Goal

Two visual improvements to make the last played move clearly identifiable:

1. **Board highlight** — source and destination squares of the last move are tinted yellow.
2. **History highlight (B4.7 fix)** — the last played half-move in the history panel is colored with ACCENT, regardless of whether it was White's or Black's move.

---

## Approach

Ansatz A: a single `_last_move: tuple[int, int] | None` field tracks the last move's squares. All existing logic is derived from this plus the already-present `_move_history` / `_current_half` state.

---

## Changes

### 1. `src/gui/constants.py`

Add two new color constants:

```python
HIGHLIGHT_LAST_FROM = (210, 196, 82)   # source square — softer yellow
HIGHLIGHT_LAST_TO   = (245, 220, 50)   # destination square — saturated yellow
```

### 2. `src/gui/game_screen.py` — State

In `GameScreen.__init__`:

```python
self._last_move: tuple[int, int] | None = None  # (from_sq, to_sq)
```

In `_make_move()`, after `play_move(...)`:

```python
self._last_move = (move.from_sq, move.to_sq)
```

Reset is implicit: a new `GameScreen` instance always starts with `_last_move = None`.

### 3. `src/gui/game_screen.py` — `_draw_board()`

Replace the existing square color priority block with:

```python
if sq == self._selected_sq:
    color = HIGHLIGHT_SEL
elif sq in legal_dests or sq in capture_dests:
    color = HIGHLIGHT_LEGAL
elif self._last_move and sq == self._last_move[1]:   # to_sq
    color = HIGHLIGHT_LAST_TO
elif self._last_move and sq == self._last_move[0]:   # from_sq
    color = HIGHLIGHT_LAST_FROM
else:
    color = base_color
```

Priority (highest → lowest):
1. Selected square
2. Legal move / capture destinations
3. Last move destination
4. Last move source
5. Base board color

### 4. `src/gui/game_screen.py` — `_draw_history_panel()`

Replace the existing per-row color logic with:

```python
for idx, (move_num, white_pgn, black_pgn) in enumerate(visible):
    is_last_row = (idx == len(visible) - 1)

    w_color = ACCENT if (is_last_row and black_pgn == "") else TEXT_DARK
    b_color = ACCENT if (is_last_row and black_pgn != "") else TEXT_DARK

    # render num, white_pgn with w_color, black_pgn with b_color
```

Behavior:
- White just moved → white PGN in last row = ACCENT, black cell empty
- Black just moved → black PGN in last row = ACCENT, white PGN = TEXT_DARK
- All earlier rows → TEXT_DARK throughout

---

## Constants import update

`game_screen.py` already imports from `gui.constants`. Add `HIGHLIGHT_LAST_FROM` and `HIGHLIGHT_LAST_TO` to that import.

---

## Out of scope

- No changes to move recording, PGN generation, or game logic.
- No promotion-specific handling needed — promotion moves have valid `from_sq`/`to_sq`.
