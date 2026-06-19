# 50-Move Rule Counter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a text-only counter at the bottom of the history panel showing remaining half-moves until a 50-move-rule draw.

**Architecture:** Six lines appended to `_draw_history_panel()` in `game_screen.py`. No new helpers needed — the computation is `100 - board.halfmove_clock` inlined directly. No new constants or fonts required; both `font_label` and `font_hist` are already instantiated at the top of that method.

**Tech Stack:** Python, pygame

---

### Task 1: Add counter to `_draw_history_panel()`

**Files:**
- Modify: `src/gui/game_screen.py` — `_draw_history_panel()` method (currently ends around line 568)

> **Note:** This change is pure pygame rendering with no extractable logic unit (`100 - x` does not merit a test function). Verification is visual.

- [ ] **Step 1: Add the counter rendering at the end of `_draw_history_panel()`**

In [src/gui/game_screen.py](src/gui/game_screen.py), find `_draw_history_panel()`. The method currently ends after the `for move_num, white_pgn, black_pgn in visible:` loop. Append the following lines directly after that loop (still inside the method body):

```python
        # 50-move rule counter
        y_counter = WINDOW_H - 60
        lbl_50 = font_label.render("50-ZÜGE-REGEL", True, TEXT_MUTED)
        surf.blit(lbl_50, (HIST_X + 6, y_counter))
        remaining = 100 - self._board.halfmove_clock
        val_50 = font_hist.render(f"{remaining} Halbzüge", True, TEXT_MUTED)
        surf.blit(val_50, (HIST_X + 6, y_counter + lbl_50.get_height() + 2))
```

- [ ] **Step 2: Run the existing test suite to confirm no regressions**

```
uv run pytest tests/ -v
```

Expected: all tests pass.

- [ ] **Step 3: Run the game and verify visually**

```
uv run python src/main.py
```

Check:
- History panel shows `50-ZÜGE-REGEL` label and `100 Halbzüge` at the bottom on game start.
- Make a pawn move (resets halfmove clock → still 100); make a non-pawn/non-capture move (clock increments → counter decreases).
- Counter text color is muted (same as history labels), no color changes.

- [ ] **Step 4: Commit**

```
git add src/gui/game_screen.py
git commit -m "feat: add 50-move rule counter to history panel"
```
