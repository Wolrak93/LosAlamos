# Design: Main Menu UI Fixes

**Date:** 2026-06-17  
**Status:** Approved

## Summary

Three visual bugs in the Main Menu screen need to be fixed:
1. Mini board rendered behind the Aufstellung buttons
2. Missing glyphs for Unicode characters `▾` (dropdown arrow) and `▶` (button icon)
3. Dropdown open-list gets painted over by subsequent draw calls (z-order bug)

---

## Fix 1 — Remove Mini Board

**File:** `src/gui/main_menu.py`

Remove the `_draw_mini_board()` method and its call in `draw()`. Remove the `_MINI_SQ` module-level constant. The Aufstellung position buttons remain unchanged and will render cleanly without the board underneath.

---

## Fix 2 — Replace Missing Glyphs

**File:** `src/gui/widgets.py` — `Dropdown.draw()`

Replace the `▾` arrow rendered via font with a manually drawn downward triangle using `pygame.draw.polygon`. The triangle is drawn in the same position as the old arrow (right side of the dropdown box).

**File:** `src/gui/main_menu.py` — `draw()`

Change `"▶  Match starten"` to `"Match starten"` (no icon).

---

## Fix 3 — Dropdown Z-Order

**File:** `src/gui/main_menu.py` — `draw()`

Move both `self._white_type_dd.draw(surf)` and `self._black_type_dd.draw(surf)` calls to the very end of `draw()`, after all other elements (labels, name inputs, time controls, start button, position buttons) have been drawn. This ensures that open dropdown lists always render on top.

---

## Files Changed

| File | Change |
|------|--------|
| `src/gui/main_menu.py` | Remove mini board, fix button text, reorder dropdown draw calls |
| `src/gui/widgets.py` | Replace `▾` font glyph with `pygame.draw.polygon` triangle |

## Out of Scope

- No changes to layout positions, colors, or other widgets
- No changes to game logic or engine
