# Spec: 50-Move Rule Counter in History Panel

**Date:** 2026-06-17
**Status:** Approved

## Overview

Add a text-only counter to the history panel that shows how many half-moves remain
before a draw is declared by the 50-move rule.

## Placement

At the bottom of the history panel (`_draw_history_panel()`), pinned near the lower
edge of the panel. Rendered after the scrollable move list, at a fixed y-position
(`WINDOW_H - 60`), left-aligned with `HIST_X + 6`.

## Visual Layout

Two lines, both in `TEXT_MUTED`:

```
50-ZÜGE-REGEL          ← font_label  (serif 10, TEXT_MUTED)
100 Halbzüge           ← font_hist   (monospace 11, TEXT_MUTED)
```

The value decreases from 100 to 0 as moves are played. At 0 the game ends
via the existing `get_game_outcome()` check (`board.halfmove_clock >= 100`).

## Data Source

`self._board.halfmove_clock` (integer, 0–100).
Remaining half-moves = `100 - board.halfmove_clock`.

## Color / Urgency

None. Both lines always render in `TEXT_MUTED`. No color changes at any threshold.

## Always Visible

The counter is always rendered, including at game start when the value is 100.

## Scope

Single change: add ~6 lines at the end of `_draw_history_panel()` in
`src/gui/game_screen.py`.

No new constants, no new fonts (both `font_label` and `font_hist` are already
instantiated at the top of `_draw_history_panel()`).
