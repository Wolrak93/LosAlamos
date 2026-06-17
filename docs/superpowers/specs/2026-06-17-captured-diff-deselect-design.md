# Spec: Captured Pieces Difference + Piece Deselection

**Date:** 2026-06-17
**Status:** Approved

---

## Overview

Two focused changes to `src/gui/game_screen.py`:

1. **Captured pieces display** — show only the net advantage (difference), not all captured pieces.
2. **Piece deselection** — deselect a piece when clicking on it again.

---

## Change 1: Captured Pieces — Net Difference Only

### Goal

Only display the surplus captures per piece type. If both sides captured the same number of pawns, no pawns are shown under either player.

### Location

`game_screen.py` — `_draw_captured_images(self, surf, x, y, color, icon_size=16)` (line ~486)

### Current Logic

For a given `color`, calculates how many opponent pieces are missing (captured by `color`) and renders that many icons.

```python
remaining = bin(self._board.pieces[opp][pt]).count("1")
captured = starting.get(pt, 0) - remaining
for _ in range(captured):
    ...
```

### New Logic

For each piece type, compute the net difference:

```python
opp = Color(1 - int(color))
opp_remaining    = bin(self._board.pieces[opp][pt]).count("1")
color_remaining  = bin(self._board.pieces[color][pt]).count("1")
captured_by_color = starting.get(pt, 0) - opp_remaining
captured_by_opp   = starting.get(pt, 0) - color_remaining
net = max(0, captured_by_color - captured_by_opp)
for _ in range(net):
    ...
```

### Behaviour

| Scenario | White shows | Black shows |
|---|---|---|
| White: 3 pawns, Black: 2 pawns | 1 pawn | — |
| White: 1 queen, Black: 0 | 1 queen | — |
| White: 2 rooks, Black: 2 rooks | — | — |

### Constraints

- No change to function signature or call sites.
- No change to rendering pipeline or icon sizing.
- Existing piece-type order (Q, R, N, P) and spacing unchanged.

---

## Change 2: Piece Deselection on Re-Click

### Goal

Clicking on the already-selected piece deselects it (sets `_selected_sq = None`).

### Location

`game_screen.py` — `_handle_board_click()` (line ~217), "Select own piece" block (line ~242).

### Current Logic

```python
if piece_info is not None and piece_info[0] == color:
    self._selected_sq = sq   # re-selects same piece on re-click
else:
    self._selected_sq = None
```

### New Logic

```python
if piece_info is not None and piece_info[0] == color:
    if sq == self._selected_sq:
        self._selected_sq = None   # deselect on re-click
    else:
        self._selected_sq = sq
else:
    self._selected_sq = None
```

### Cases Covered

| Click target | Before | After |
|---|---|---|
| Same square as selected piece | stays selected | deselects |
| Different own piece | switches selection | unchanged |
| Empty square | deselects | unchanged |
| Opponent piece (no legal capture) | deselects | unchanged |
| Legal move destination | executes move | unchanged |

### Constraints

- No change to promotion flow.
- No change to bot-turn guard.
- Clicking a different own piece still switches selection (intended).

---

## Files Changed

| File | Lines affected |
|---|---|
| `src/gui/game_screen.py` | ~486–499 (`_draw_captured_images`) |
| `src/gui/game_screen.py` | ~242–246 (`_handle_board_click`) |

## Tests

- Existing captured-pieces tests should be updated to reflect net-difference output.
- Add test cases for deselection via re-click.
