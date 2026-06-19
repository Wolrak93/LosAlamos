# Info Panel UI Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix captured-piece images, hide eval for non-evaluating players, move the back button to the panel bottom, and add a large eval number for evaluating bots.

**Architecture:** All changes are in `src/gui/assets.py` (new small-sprite helper) and `src/gui/game_screen.py` (new methods + updated `_draw_info_panel()`). A module-level `_is_evaluating_bot()` helper is extracted for testability. No engine or bot files are touched.

**Tech Stack:** Python 3.11, pygame 2.6+, pytest, uv

---

## File Map

| File | Change |
|------|--------|
| `src/gui/assets.py` | Add `_small_sprites` cache + `get_small_sprite()` |
| `src/gui/game_screen.py` | Add `_is_evaluating_bot()`, `_calc_eval_diff()`, `_draw_captured_images()`; rewrite `_draw_info_panel()` |
| `tests/test_gui.py` | New — tests for `_is_evaluating_bot()` |

---

## Task 1: Add `get_small_sprite()` to `assets.py`

**Files:**
- Modify: `src/gui/assets.py`

- [ ] **Step 1: Add the small-sprite cache and function**

In `src/gui/assets.py`, add after the `_sprites` dict (line 24) and the existing `get_sprite` function:

```python
_small_sprites: dict[tuple[Color, PieceType, int], pygame.Surface] = {}


def get_small_sprite(color: Color, pt: PieceType, size: int) -> pygame.Surface:
    key = (color, pt, size)
    if key not in _small_sprites:
        base = _sprites[(color, pt)]
        _small_sprites[key] = pygame.transform.smoothscale(base, (size, size))
    return _small_sprites[key]
```

Full file after the edit:

```python
from __future__ import annotations

from pathlib import Path

import pygame

from engine.board import Color, PieceType

_ASSET_DIR = Path(__file__).parent.parent.parent / "user_input" / "assets"

_FILE_NAMES = {
    (Color.WHITE, PieceType.PAWN):   "w-pawn.png",
    (Color.WHITE, PieceType.KNIGHT): "w-knight.png",
    (Color.WHITE, PieceType.ROOK):   "w-rook.png",
    (Color.WHITE, PieceType.QUEEN):  "w-queen.png",
    (Color.WHITE, PieceType.KING):   "w-king.png",
    (Color.BLACK, PieceType.PAWN):   "b-pawn.png",
    (Color.BLACK, PieceType.KNIGHT): "b-knight.png",
    (Color.BLACK, PieceType.ROOK):   "b-rook.png",
    (Color.BLACK, PieceType.QUEEN):  "b-queen.png",
    (Color.BLACK, PieceType.KING):   "b-king.png",
}

_sprites: dict[tuple[Color, PieceType], pygame.Surface] = {}
_small_sprites: dict[tuple[Color, PieceType, int], pygame.Surface] = {}


def load_sprites(sq_size: int) -> None:
    for key, filename in _FILE_NAMES.items():
        path = _ASSET_DIR / filename
        img = pygame.image.load(str(path)).convert_alpha()
        _sprites[key] = pygame.transform.smoothscale(img, (sq_size, sq_size))


def get_sprite(color: Color, pt: PieceType) -> pygame.Surface:
    return _sprites[(color, pt)]


def get_small_sprite(color: Color, pt: PieceType, size: int) -> pygame.Surface:
    key = (color, pt, size)
    if key not in _small_sprites:
        base = _sprites[(color, pt)]
        _small_sprites[key] = pygame.transform.smoothscale(base, (size, size))
    return _small_sprites[key]
```

- [ ] **Step 2: Commit**

```bash
git add src/gui/assets.py
git commit -m "feat: add get_small_sprite() for scaled-down piece icons"
```

---

## Task 2: Add `_is_evaluating_bot()` helper + tests

**Files:**
- Modify: `src/gui/game_screen.py` (add module-level function before the `GameScreen` class)
- Create: `tests/test_gui.py`

- [ ] **Step 1: Add module-level helper in `game_screen.py`**

Insert the following **before** `class GameScreen:` in `src/gui/game_screen.py`:

```python
def _is_evaluating_bot(bot) -> bool:
    from bots.random_bot import RandomBot
    return bot is not None and not isinstance(bot, RandomBot)
```

- [ ] **Step 2: Write failing tests**

Create `tests/test_gui.py`:

```python
from bots.greedy_bot import GreedyBot
from bots.random_bot import RandomBot
from gui.game_screen import _is_evaluating_bot


def test_human_is_not_evaluating():
    assert _is_evaluating_bot(None) is False


def test_random_bot_is_not_evaluating():
    assert _is_evaluating_bot(RandomBot("r")) is False


def test_greedy_bot_is_evaluating():
    assert _is_evaluating_bot(GreedyBot("g")) is True
```

- [ ] **Step 3: Run failing tests**

```bash
uv run pytest tests/test_gui.py -v
```

Expected: **FAIL** — `ImportError: cannot import name '_is_evaluating_bot'` (function not added yet, or if already added, tests should pass — verify either way).

- [ ] **Step 4: Run tests again after Step 1 is applied**

```bash
uv run pytest tests/test_gui.py -v
```

Expected:
```
PASSED tests/test_gui.py::test_human_is_not_evaluating
PASSED tests/test_gui.py::test_random_bot_is_not_evaluating
PASSED tests/test_gui.py::test_greedy_bot_is_evaluating
```

- [ ] **Step 5: Commit**

```bash
git add src/gui/game_screen.py tests/test_gui.py
git commit -m "feat: add _is_evaluating_bot() helper with tests"
```

---

## Task 3: Add `_calc_eval_diff()` and `_draw_captured_images()` methods

**Files:**
- Modify: `src/gui/game_screen.py`

- [ ] **Step 1: Add `_calc_eval_diff()` method to `GameScreen`**

Add this method to `GameScreen`, between `_draw_eval_bar` and `_draw_history_panel` (i.e., after line 482 in the original file):

```python
def _calc_eval_diff(self) -> int:
    white_mat = sum(
        bin(self._board.pieces[Color.WHITE][pt]).count("1") * PIECE_VALUES[pt]
        for pt in PieceType if pt != PieceType.KING
    )
    black_mat = sum(
        bin(self._board.pieces[Color.BLACK][pt]).count("1") * PIECE_VALUES[pt]
        for pt in PieceType if pt != PieceType.KING
    )
    return white_mat - black_mat
```

- [ ] **Step 2: Add `_draw_captured_images()` method to `GameScreen`**

Add this method directly after `_calc_eval_diff()`:

```python
def _draw_captured_images(self, surf: pygame.Surface, x: int, y: int,
                           color: Color, icon_size: int = 16) -> None:
    from gui.assets import get_small_sprite
    opp = Color(1 - int(color))
    starting = {PieceType.PAWN: 6, PieceType.KNIGHT: 2,
                PieceType.ROOK: 2, PieceType.QUEEN: 1}
    cursor_x = x
    for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT, PieceType.PAWN):
        remaining = bin(self._board.pieces[opp][pt]).count("1")
        captured = starting.get(pt, 0) - remaining
        for _ in range(captured):
            img = get_small_sprite(opp, pt, icon_size)
            surf.blit(img, (cursor_x, y))
            cursor_x += icon_size + 1
```

Note: `color` is the capturing player (e.g., WHITE). We show the opponent's (`opp`) pieces that were captured. So if WHITE captured 2 black pawns, we blit 2 black pawn sprites.

- [ ] **Step 3: Commit**

```bash
git add src/gui/game_screen.py
git commit -m "feat: add _calc_eval_diff() and _draw_captured_images() to GameScreen"
```

---

## Task 4: Rewrite `_draw_info_panel()` with all UI changes

**Files:**
- Modify: `src/gui/game_screen.py` — replace entire `_draw_info_panel()` method (lines 342–430)

- [ ] **Step 1: Replace `_draw_info_panel()`**

Replace the entire method with the following. The key changes vs. the original:
- `draw_player()` gains `evaluating: bool` parameter
- Captured pieces use `_draw_captured_images()` instead of unicode text
- Eval label + bar + large eval number shown only when `evaluating=True`
- Back button removed from between cards and placed at `WINDOW_H - 44`
- The two divider lines around the old button are removed

```python
def _draw_info_panel(self) -> None:
    surf = self._surf
    font_sm = get_font("serif", 11)
    font_md = get_font("serif", 14)
    font_clock = get_font("monospace", 16)
    font_label = get_font("serif", 10)
    font_eval = get_font("monospace", 24)

    panel_rect = pygame.Rect(INFO_X, 0, INFO_W, WINDOW_H)
    pygame.draw.rect(surf, CARD_BG, panel_rect)
    pygame.draw.line(surf, BORDER, (INFO_X, 0), (INFO_X, WINDOW_H), 1)
    pygame.draw.line(surf, BORDER, (INFO_X + INFO_W, 0), (INFO_X + INFO_W, WINDOW_H), 1)

    active = self._board.side_to_move
    y = 12

    def draw_player(color: Color, name: str, bot_label: str, evaluating: bool) -> int:
        nonlocal y
        is_active = (color == active and self._outcome is None)
        # Name + type
        nt = font_md.render(name, True, TEXT_DARK)
        surf.blit(nt, (INFO_X + 8, y))
        y += nt.get_height() + 2
        bt = font_sm.render(bot_label, True, TEXT_MUTED)
        surf.blit(bt, (INFO_X + 8, y))
        y += bt.get_height() + 4
        # Clock
        if self._use_clock:
            secs = max(0, self._clocks[color])
            mins_left = int(secs) // 60
            secs_left = int(secs) % 60
            clock_str = f"{mins_left}:{secs_left:02d}"
            cb = CLOCK_ACTIVE_BG if is_active else CLOCK_INACTIVE_BG
            cf = CLOCK_ACTIVE_FG if is_active else CLOCK_INACTIVE_FG
            cr = pygame.Rect(INFO_X + INFO_W - 72, y - 22, 64, 24)
            pygame.draw.rect(surf, cb, cr, border_radius=3)
            ct = font_clock.render(clock_str, True, cf)
            surf.blit(ct, (cr.centerx - ct.get_width() // 2,
                           cr.centery - ct.get_height() // 2))
        y += 6
        # Captured pieces as sprite images (no +N text)
        self._draw_captured_images(surf, INFO_X + 8, y, color)
        y += 20
        # Eval: only for evaluating bots
        if evaluating:
            lbl = font_label.render(
                f"EVAL {'WEISS' if color == Color.WHITE else 'SCHWARZ'}",
                True, TEXT_MUTED
            )
            surf.blit(lbl, (INFO_X + 8, y))
            y += lbl.get_height() + 3
            self._draw_eval_bar(surf, pygame.Rect(INFO_X + 8, y, INFO_W - 16, 8), color)
            y += 14
            # Large eval number
            diff = self._calc_eval_diff()
            sign = "+" if diff > 0 else ""
            eval_str = f"{sign}{diff:.2f}"
            if diff > 0:
                eval_color = ACCENT
            elif diff < 0:
                eval_color = (160, 60, 60)
            else:
                eval_color = TEXT_MUTED
            et = font_eval.render(eval_str, True, eval_color)
            surf.blit(et, (INFO_X + INFO_W // 2 - et.get_width() // 2, y))
            y += et.get_height() + 6
        return y

    # Black at top
    black_bot = self._config.black_bot
    black_bot_label = (
        f"{type(black_bot).__name__} · Schwarz"
        if black_bot
        else "Mensch · Schwarz"
    )
    draw_player(Color.BLACK,
                self._config.black_name,
                black_bot_label,
                evaluating=_is_evaluating_bot(black_bot))

    # White
    white_bot = self._config.white_bot
    white_bot_label = (
        f"{type(white_bot).__name__} · Weiß"
        if white_bot
        else "Mensch · Weiß"
    )
    draw_player(Color.WHITE,
                self._config.white_name,
                white_bot_label,
                evaluating=_is_evaluating_bot(white_bot))

    # Back button pinned to panel bottom
    back_rect = pygame.Rect(INFO_X + 8, WINDOW_H - 44, INFO_W - 16, 28)
    pygame.draw.rect(surf, CARD_BG, back_rect, border_radius=3)
    pygame.draw.rect(surf, BORDER, back_rect, 1, border_radius=3)
    bt2 = font_sm.render("← Zurück zum Menü", True, TEXT_MUTED)
    surf.blit(bt2, (back_rect.centerx - bt2.get_width() // 2,
                    back_rect.centery - bt2.get_height() // 2))
    self._back_rect = back_rect
```

- [ ] **Step 2: Run existing tests to check nothing is broken**

```bash
uv run pytest tests/ -v
```

Expected: all existing tests pass. `test_gui.py` tests also pass.

- [ ] **Step 3: Commit**

```bash
git add src/gui/game_screen.py
git commit -m "feat: rewrite _draw_info_panel() — sprite captured pieces, conditional eval, button at bottom"
```

---

## Task 5: Manual smoke test

Run the game and verify all five requirements visually:

- [ ] **Step 1: Launch the game**

```bash
uv run python src/main.py
```

- [ ] **Step 2: Check Mensch vs. Mensch**
  - [ ] Eval bar and large eval number **not visible** for either player
  - [ ] Captured pieces row is empty (start of game) — no unicode symbols, no "+N"
  - [ ] "← Zurück zum Menü" button visible at the very bottom of the panel

- [ ] **Step 3: Make a few moves (capture a piece)**
  - [ ] Captured piece row shows the actual piece sprite image (scaled PNG)
  - [ ] No "+N" material advantage number displayed

- [ ] **Step 4: Start a game with GreedyBot**
  - [ ] Eval label ("EVAL WEISS" or "EVAL SCHWARZ") visible for GreedyBot's panel
  - [ ] Eval bar visible for GreedyBot's panel
  - [ ] Large eval number (e.g., "+0.00", "+2.00") visible for GreedyBot's panel
  - [ ] Human player's panel has **no** eval bar and **no** large number

- [ ] **Step 5: Start a game with RandomBot**
  - [ ] RandomBot's panel: **no** eval bar, **no** large number

- [ ] **Step 6: Final commit**

```bash
git add -p  # only if any last-minute fixes were needed
git commit -m "fix: info panel — captured piece images, conditional eval, bottom button"
```

---

## Self-Review

| Spec requirement | Covered by |
|---|---|
| Captured pieces shown as sprite images | Task 1 (get_small_sprite), Task 3 (_draw_captured_images), Task 4 (draw_player uses it) |
| No +N material number | Task 4 — _draw_captured_images does not render text |
| Eval bar hidden for Human and RandomBot | Task 2 (_is_evaluating_bot), Task 4 (evaluating param) |
| Back button at panel bottom | Task 4 — `WINDOW_H - 44` fixed position |
| Large eval number (+2.00 format) for evaluating bots | Task 4 — font_eval + _calc_eval_diff() |
| get_small_sprite lazy cache | Task 1 |
| _is_evaluating_bot tested | Task 2 |
