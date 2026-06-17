# Last-Move Highlight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Highlight the last-move source/destination squares on the board in yellow, and fix the history panel so the last half-move is always shown in ACCENT color (B4.7).

**Architecture:** One new `_last_move` tuple field on `GameScreen` stores the coordinates; `_draw_board()` and `_draw_history_panel()` read it. Two new color constants cover source/destination shading.

**Tech Stack:** Python, pygame, existing `src/gui/constants.py` + `src/gui/game_screen.py`

---

## File Map

| File | Change |
|---|---|
| `src/gui/constants.py` | Add `HIGHLIGHT_LAST_FROM`, `HIGHLIGHT_LAST_TO` |
| `src/gui/game_screen.py` | Add `_last_move` state, update `_make_move`, `_draw_board`, `_draw_history_panel`, imports |

---

## Task 1: Add color constants

**Files:**
- Modify: `src/gui/constants.py`

> These are purely visual; no automated test applies. Manual verification in Task 4.

- [ ] **Step 1: Add the two constants at the end of the color block in `constants.py`**

  Open `src/gui/constants.py`. After line `PROMO_CIRCLE_BG = (255, 255, 255)` add:

  ```python
  HIGHLIGHT_LAST_FROM = (210, 196, 82)
  HIGHLIGHT_LAST_TO   = (245, 220, 50)
  ```

  Result — the color block should end with:
  ```python
  PROMO_HOVER_BG = (232, 160, 32)
  PROMO_CIRCLE_BG = (255, 255, 255)
  OVERLAY_DIM = (0, 0, 0, 160)
  HIGHLIGHT_LAST_FROM = (210, 196, 82)
  HIGHLIGHT_LAST_TO   = (245, 220, 50)
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add src/gui/constants.py
  git commit -m "feat: add HIGHLIGHT_LAST_FROM and HIGHLIGHT_LAST_TO color constants"
  ```

---

## Task 2: Add `_last_move` state and set it on each move

**Files:**
- Modify: `src/gui/game_screen.py` (lines ~11–41 for imports, ~91–112 for `__init__`, ~275–285 for `_make_move`)

- [ ] **Step 1: Add the new constants to the import block**

  In `src/gui/game_screen.py`, find the `from gui.constants import (` block. Add `HIGHLIGHT_LAST_FROM` and `HIGHLIGHT_LAST_TO` to it:

  ```python
  from gui.constants import (
      ACCENT,
      BG,
      BOARD_DARK,
      BOARD_LIGHT,
      BOARD_PX,
      BOARD_X,
      BOARD_Y,
      BORDER,
      CARD_BG,
      CLOCK_ACTIVE_BG,
      CLOCK_ACTIVE_FG,
      CLOCK_INACTIVE_BG,
      CLOCK_INACTIVE_FG,
      FILE_NAMES,
      HIGHLIGHT_LAST_FROM,
      HIGHLIGHT_LAST_TO,
      HIGHLIGHT_LEGAL,
      HIGHLIGHT_SEL,
      HIST_W,
      HIST_X,
      INFO_W,
      INFO_X,
      PROMO_CIRCLE_BG,
      PROMO_HOVER_BG,
      RANK_LABEL_W,
      SQ_SIZE,
      TEXT_DARK,
      TEXT_MUTED,
      WINDOW_H,
      WINDOW_W,
      get_font,
  )
  ```

- [ ] **Step 2: Initialise `_last_move` in `__init__`**

  In `GameScreen.__init__`, after the line `self._promo_hover: int | None = None`, add:

  ```python
  self._last_move: tuple[int, int] | None = None  # (from_sq, to_sq)
  ```

- [ ] **Step 3: Set `_last_move` in `_make_move()`**

  In `_make_move()`, the current body is:
  ```python
  def _make_move(self, move: Move) -> None:
      pgn = move.to_pgn()
      play_move(self._board, move)
      if self._use_clock:
          ...
  ```

  Add `self._last_move = (move.from_sq, move.to_sq)` immediately after `play_move(...)`:

  ```python
  def _make_move(self, move: Move) -> None:
      pgn = move.to_pgn()
      play_move(self._board, move)
      self._last_move = (move.from_sq, move.to_sq)
      if self._use_clock:
          moved_color = Color(1 - int(self._board.side_to_move))
          self._clocks[moved_color] = max(0, self._clocks[moved_color] + self._increment)
      self._record_pgn(pgn)
      self._legal_moves = generate_legal_moves(self._board)
      self._outcome = get_game_outcome(self._board)
      if self._outcome is None:
          self._maybe_schedule_bot()
  ```

- [ ] **Step 4: Commit**

  ```bash
  git add src/gui/game_screen.py
  git commit -m "feat: track last-move squares in GameScreen state"
  ```

---

## Task 3: Highlight last-move squares on the board

**Files:**
- Modify: `src/gui/game_screen.py` → `_draw_board()` (lines ~211–223)

- [ ] **Step 1: Replace the square color priority block**

  In `_draw_board()`, find the existing block:
  ```python
  # Background color
  if sq == self._selected_sq:
      color = HIGHLIGHT_SEL
  elif sq in legal_dests or sq in capture_dests:
      color = HIGHLIGHT_LEGAL
  else:
      color = base_color
  ```

  Replace it with:
  ```python
  # Background color
  if sq == self._selected_sq:
      color = HIGHLIGHT_SEL
  elif sq in legal_dests or sq in capture_dests:
      color = HIGHLIGHT_LEGAL
  elif self._last_move and sq == self._last_move[1]:
      color = HIGHLIGHT_LAST_TO
  elif self._last_move and sq == self._last_move[0]:
      color = HIGHLIGHT_LAST_FROM
  else:
      color = base_color
  ```

- [ ] **Step 2: Commit**

  ```bash
  git add src/gui/game_screen.py
  git commit -m "feat: highlight last-move source and destination squares on board"
  ```

---

## Task 4: Fix history panel highlight (B4.7)

**Files:**
- Modify: `src/gui/game_screen.py` → `_draw_history_panel()` (lines ~558–567)

- [ ] **Step 1: Replace the per-row color logic**

  In `_draw_history_panel()`, find the existing loop:
  ```python
  y = panel_top
  for move_num, white_pgn, black_pgn in visible:
      num = font_hist.render(f"{move_num}.", True, TEXT_MUTED)
      surf.blit(num, (HIST_X + 4, y))
      w_color = ACCENT if black_pgn == "" else TEXT_DARK
      wt = font_hist.render(white_pgn, True, w_color)
      surf.blit(wt, (HIST_X + 26, y))
      if black_pgn:
          bt = font_hist.render(black_pgn, True, TEXT_DARK)
          surf.blit(bt, (HIST_X + 66, y))
      y += row_h
  ```

  Replace it with:
  ```python
  y = panel_top
  for idx, (move_num, white_pgn, black_pgn) in enumerate(visible):
      is_last_row = (idx == len(visible) - 1)
      num = font_hist.render(f"{move_num}.", True, TEXT_MUTED)
      surf.blit(num, (HIST_X + 4, y))
      w_color = ACCENT if (is_last_row and black_pgn == "") else TEXT_DARK
      wt = font_hist.render(white_pgn, True, w_color)
      surf.blit(wt, (HIST_X + 26, y))
      if black_pgn:
          b_color = ACCENT if is_last_row else TEXT_DARK
          bt = font_hist.render(black_pgn, True, b_color)
          surf.blit(bt, (HIST_X + 66, y))
      y += row_h
  ```

- [ ] **Step 2: Run the app and verify manually**

  ```bash
  cd src && python main.py
  ```

  Checklist:
  - [ ] Spiel starten (Mensch vs. Mensch)
  - [ ] Weiß zieht: letzter weißer Zug in History in ACCENT (grün), Brett zeigt gelbe Quell- und Zielfelder
  - [ ] Schwarz zieht: letzter schwarzer Zug in History in ACCENT, ältere Züge in TEXT_DARK (dunkel), Brett-Highlight wechselt
  - [ ] Weitere Züge: immer nur der zuletzt gespielte Halbzug ist hervorgehoben
  - [ ] Figur anklicken während letzter Zug sichtbar: Selection-Highlight (gelb) überlagert Last-Move-Highlight korrekt
  - [ ] Promotion abschließen: Highlight zeigt Quell- und Zielfeld der Promotion

- [ ] **Step 3: Commit**

  ```bash
  git add src/gui/game_screen.py
  git commit -m "fix: highlight last half-move in history panel for both colors (B4.7)"
  ```
