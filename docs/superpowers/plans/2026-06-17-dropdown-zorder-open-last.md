# Dropdown Z-Order: Open Last Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure the open dropdown always renders on top of the other (closed) dropdown box, so no option is ever obscured.

**Architecture:** Single conditional block at the end of `MainMenuScreen.draw()` in `src/gui/main_menu.py`. When `_white_type_dd.open` is True, draw black first then white; otherwise draw white first then black. No changes to `widgets.py` or any other file.

**Tech Stack:** Python, pygame

---

### Task 1: Draw open dropdown last in MainMenuScreen.draw()

**Files:**
- Modify: `src/gui/main_menu.py`

*Visual rendering change — verification is done by running the app and observing.*

- [ ] **Step 1: Replace the two-line dropdown draw block**

At the very end of `draw()` in `src/gui/main_menu.py`, find:

```python
        # Dropdowns drawn last so open lists render on top of all other elements
        self._white_type_dd.draw(surf)
        self._black_type_dd.draw(surf)
```

Replace with:

```python
        # Open dropdown drawn last so its list is never covered by the other box
        if self._white_type_dd.open:
            self._black_type_dd.draw(surf)
            self._white_type_dd.draw(surf)
        else:
            self._white_type_dd.draw(surf)
            self._black_type_dd.draw(surf)
```

- [ ] **Step 2: Run linter**

```bash
cd "c:\OD\OneDrive - HARREN-Group\programming\repos\LosAlamos"
uv run ruff check src/gui/main_menu.py
```

Expected: no errors.

- [ ] **Step 3: Visual verification**

Run the app:

```bash
uv run python src/main.py
```

Check:
- Open the white dropdown → all three options (Mensch, RandomBot, GreedyBot) are fully visible, not cut off by the black dropdown box
- Open the black dropdown → all three options fully visible
- Both dropdowns closed → layout looks normal

- [ ] **Step 4: Commit**

```bash
git add src/gui/main_menu.py
git commit -m "fix: draw open dropdown last so its list is never covered by the other dropdown box"
```
