# Design: Draw Open Dropdown Last

**Date:** 2026-06-17  
**Status:** Approved

## Problem

When the white dropdown is open, its GreedyBot option (y=256–288) is covered by the black dropdown box (y=260–292), because `_black_type_dd.draw()` is called after `_white_type_dd.draw()` at the end of `MainMenuScreen.draw()`.

## Fix

**File:** `src/gui/main_menu.py`

Replace the current two-line block at the end of `draw()`:

```python
        # Dropdowns drawn last so open lists render on top of all other elements
        self._white_type_dd.draw(surf)
        self._black_type_dd.draw(surf)
```

With a conditional that always draws the open dropdown last:

```python
        # Open dropdown drawn last so its list is never covered by the other box
        if self._white_type_dd.open:
            self._black_type_dd.draw(surf)
            self._white_type_dd.draw(surf)
        else:
            self._white_type_dd.draw(surf)
            self._black_type_dd.draw(surf)
```

This handles all cases: white open, black open, neither open (order irrelevant).

## Out of Scope

No changes to `widgets.py` or any other file.
