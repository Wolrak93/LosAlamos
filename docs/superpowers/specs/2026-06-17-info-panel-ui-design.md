# Design Spec: Info Panel UI Improvements

**Date:** 2026-06-17
**File:** `src/gui/game_screen.py`, `src/gui/assets.py`

---

## Goal

Five targeted improvements to the right-side info panel of the game screen:

1. Captured pieces shown as scaled-down sprite images (not Unicode text)
2. Material advantage number removed from captured pieces display
3. Eval bar and eval number hidden for Human and RandomBot players
4. "Zurück zum Menü" button moved to the very bottom of the panel
5. Large numeric evaluation display (+2.00 format) added to evaluating-bot info boxes

---

## Scope

Changes are confined to `src/gui/game_screen.py` and `src/gui/assets.py`.  
No engine, bot logic, or other GUI files are touched.

---

## Changes

### 1. `assets.py` — Small sprite cache

Add a second sprite cache `_small_sprites` and a new public function:

```python
_small_sprites: dict[tuple[Color, PieceType, int], pygame.Surface] = {}

def get_small_sprite(color: Color, pt: PieceType, size: int) -> pygame.Surface:
    key = (color, pt, size)
    if key not in _small_sprites:
        base = _sprites[(color, pt)]
        _small_sprites[key] = pygame.transform.smoothscale(base, (size, size))
    return _small_sprites[key]
```

`get_small_sprite` is lazy: it caches on first call per (color, pt, size).  
Must only be called after `load_sprites()` has run.

---

### 2. `game_screen.py` — `_draw_captured_images()`

Replace `_captured_display()` (returns string) with `_draw_captured_images(surf, x, y, color, icon_size)`:

- For each piece type `[QUEEN, ROOK, KNIGHT, PAWN]`:
  - Count how many of the opponent's pieces were captured
  - Call `get_small_sprite(opponent_color, pt, icon_size)` for each captured piece
  - Blit sprites left-to-right; each sprite's x-offset = `cursor_x`, then `cursor_x += icon_size + 1` (1px gap between sprites, no overlap)
- No `+N` material advantage text is rendered
- `icon_size = 16` (pixels)
- The opponent color: if `color == WHITE`, opponent is `BLACK` (white captured black pieces)
- Row height consumed: `icon_size` px + small vertical margin

Import `get_small_sprite` from `gui.assets`.

---

### 3. `game_screen.py` — Evaluating-bot detection

In `_draw_info_panel()`, before calling `draw_player()`:

```python
from bots.random_bot import RandomBot

def _is_evaluating_bot(bot) -> bool:
    return bot is not None and not isinstance(bot, RandomBot)
```

This returns `True` only for bots that perform real evaluation (currently: `GreedyBot` and future bots). Human (`None`) and `RandomBot` return `False`.

---

### 4. `game_screen.py` — `draw_player()` signature change

Add parameter `evaluating: bool` to the nested `draw_player()` function.

Layout inside `draw_player()`:

```
Name (font_md)
Bot label (font_sm)
Clock (optional, unchanged)
Captured piece images row (icon_size=16, via _draw_captured_images)
--- only if evaluating=True ---
  "EVAL WEISS/SCHWARZ" label (font_label, 10px)
  Eval bar (8px tall, unchanged)
  Large eval number (font 24px, centered, format "+2.00")
```

The large eval number:
- Calculated as `diff = white_mat - black_mat` (same as `_draw_eval_bar`)
- Formatted: `f"+{diff:.2f}"` if diff > 0, `f"{diff:.2f}"` otherwise
- Font: `get_font("monospace", 24)` (or nearest system equivalent)
- Color: `ACCENT` if diff > 0, `TEXT_MUTED` if diff == 0, red-ish (`(160, 60, 60)`) if diff < 0
- Centered horizontally within the panel

Extract the eval calculation into a private method `_calc_eval_diff() -> int` to avoid duplication between `_draw_eval_bar` and the large number display.

---

### 5. `game_screen.py` — "Zurück zum Menü" button position

Remove the button from between the two player cards.

Place it at a fixed absolute position at the bottom of the info panel:

```python
back_rect = pygame.Rect(INFO_X + 8, WINDOW_H - 44, INFO_W - 16, 28)
```

The divider lines around the old button position are also removed.

---

## Layout Sketch (INFO panel, 196px wide, 650px tall)

```
┌─────────────────────────┐  y=0
│ [Black name]            │
│ [Bot label]   [Clock]   │
│ [♟♟♟♟  captured imgs]  │
│ EVAL SCHWARZ (if eval)  │
│ [====eval bar======]    │
│ +2.00 (if eval, large)  │
├─────────────────────────┤  ~y=200 (variable)
│                         │
│ [White name]            │
│ [Bot label]   [Clock]   │
│ [♙♙  captured imgs]    │
│ EVAL WEISS (if eval)    │
│ [====eval bar======]    │
│ +2.00 (if eval, large)  │
│                         │
│                         │
│ [← Zurück zum Menü]     │  y=606 (WINDOW_H - 44)
└─────────────────────────┘  y=650
```

---

## Edge Cases

- If no pieces are captured, `_draw_captured_images()` renders nothing (zero-height still advances `y` by `icon_size` for consistent spacing).
- If `load_sprites()` has not been called, `get_small_sprite()` will raise `KeyError` — same contract as existing `get_sprite()`, no extra guard needed.
- `_calc_eval_diff()` returns 0 when all pieces are gone (total=0 guard already in `_draw_eval_bar`, carry it over).
- The "Zurück zum Menü" button's click detection via `self._back_rect` is unchanged.

---

## Files Changed

| File | Change |
|------|--------|
| `src/gui/assets.py` | Add `get_small_sprite()` and `_small_sprites` cache |
| `src/gui/game_screen.py` | Replace `_captured_display()` with `_draw_captured_images()`, add `_calc_eval_diff()`, update `draw_player()`, reposition button |
