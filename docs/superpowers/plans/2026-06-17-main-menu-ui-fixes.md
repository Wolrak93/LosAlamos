# Main Menu UI Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix three visual bugs in the Main Menu: remove the mini board that renders behind Aufstellung buttons, replace missing Unicode glyphs with drawn graphics, and fix dropdown z-order so the open list renders on top of all other elements.

**Architecture:** All changes are confined to two files — `src/gui/widgets.py` (Dropdown widget) and `src/gui/main_menu.py` (screen layout and draw order). No logic or engine changes needed. These are pure rendering fixes.

**Tech Stack:** Python, pygame

---

### Task 1: Remove mini board from Aufstellung section

**Files:**
- Modify: `src/gui/main_menu.py`

*Note: These are visual rendering changes. There are no automated tests to write — verification is done by running the app and observing.*

- [ ] **Step 1: Remove `_MINI_SQ` constant**

In `src/gui/main_menu.py`, delete line 41:

```python
_MINI_SQ = 14  # mini board square size
```

- [ ] **Step 2: Remove `_draw_mini_board` call from `draw()`**

In `draw()`, find this block (around line 241–242):

```python
        # Mini board (decorative)
        self._draw_mini_board(surf, right_x, 180)
```

Delete both lines.

- [ ] **Step 3: Remove `_draw_mini_board` method**

Delete the entire method at the bottom of the class (lines 265–272):

```python
    def _draw_mini_board(self, surf, x, y) -> None:
        sq = _MINI_SQ
        for rank in range(5, -1, -1):
            for file in range(6):
                color = BOARD_LIGHT if (rank + file) % 2 == 0 else BOARD_DARK
                rx = x + file * sq
                ry = y + (5 - rank) * sq
                pygame.draw.rect(surf, color, (rx, ry, sq, sq))
```

- [ ] **Step 4: Remove unused color imports**

In `src/gui/main_menu.py`, `BOARD_DARK` and `BOARD_LIGHT` are now unused. Remove them from the import block:

```python
from gui.constants import (
    ACCENT,
    ACCENT_LIGHT,
    BG,
    BORDER,
    CARD_BG,
    TEXT_DARK,
    TEXT_MUTED,
    WINDOW_W,
    get_font,
)
```

- [ ] **Step 5: Run linter**

```bash
cd "c:\OD\OneDrive - HARREN-Group\programming\repos\LosAlamos"
uv run ruff check src/gui/main_menu.py
```

Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add src/gui/main_menu.py
git commit -m "fix: remove decorative mini board from main menu Aufstellung section"
```

---

### Task 2: Replace missing Unicode glyphs

**Files:**
- Modify: `src/gui/widgets.py`
- Modify: `src/gui/main_menu.py`

- [ ] **Step 1: Replace `▾` font glyph with a drawn triangle in `Dropdown.draw()`**

In `src/gui/widgets.py`, replace the two lines that render the arrow:

```python
        # Arrow
        arrow = font.render("▾", True, TEXT_MUTED)
        surface.blit(arrow, (self.rect.right - 18, self.rect.centery - arrow.get_height() // 2))
```

with a manually drawn downward triangle:

```python
        # Arrow (drawn triangle — font glyph unreliable across systems)
        ax = self.rect.right - 14
        ay = self.rect.centery
        pygame.draw.polygon(surface, TEXT_MUTED, [
            (ax - 5, ay - 3),
            (ax + 5, ay - 3),
            (ax,     ay + 4),
        ])
```

- [ ] **Step 2: Remove play icon from "Match starten" button**

In `src/gui/main_menu.py` inside `draw()`, find:

```python
        bt = font_body.render("▶  Match starten", True, (255, 255, 255))
```

Replace with:

```python
        bt = font_body.render("Match starten", True, (255, 255, 255))
```

- [ ] **Step 3: Run linter**

```bash
uv run ruff check src/gui/widgets.py src/gui/main_menu.py
```

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add src/gui/widgets.py src/gui/main_menu.py
git commit -m "fix: replace unrenderable Unicode glyphs with drawn triangle and plain text"
```

---

### Task 3: Fix dropdown z-order

**Files:**
- Modify: `src/gui/main_menu.py`

The issue: `self._white_type_dd.draw(surf)` and `self._black_type_dd.draw(surf)` are called early in `draw()`. All elements drawn afterwards (name inputs, time controls, start button, position buttons) are painted on top, covering the open dropdown list. The fix is to draw both dropdowns last.

- [ ] **Step 1: Remove dropdown draw calls from their current positions**

In `draw()`, remove these two lines from within the White and Black sections:

In the White section block — delete:
```python
        self._white_type_dd.draw(surf)
```

In the Black section block — delete:
```python
        self._black_type_dd.draw(surf)
```

- [ ] **Step 2: Add both dropdown draw calls at the very end of `draw()`**

After the position buttons loop (the last existing block in `draw()`), append:

```python
        # Dropdowns drawn last so open lists render on top of all other elements
        self._white_type_dd.draw(surf)
        self._black_type_dd.draw(surf)
```

- [ ] **Step 3: Run linter**

```bash
uv run ruff check src/gui/main_menu.py
```

Expected: no errors.

- [ ] **Step 4: Visual verification**

Run the app:

```bash
uv run python src/main.py
```

Check:
- Open the white player dropdown → list appears on top of everything below (name input, black section, time controls, button)
- Open the black player dropdown → list appears on top of time controls and start button
- Close both dropdowns → layout looks normal, no artefacts

- [ ] **Step 5: Commit**

```bash
git add src/gui/main_menu.py
git commit -m "fix: draw dropdowns last so open list renders above all other menu elements"
```
