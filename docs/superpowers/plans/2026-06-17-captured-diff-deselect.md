# Captured Pieces Diff + Piece Deselection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Show only the net captured-piece advantage per piece type in the info panel, and deselect a piece when clicking it again.

**Architecture:** Both changes extract a small pure module-level helper function from the respective `GameScreen` method, making the logic independently testable without pygame. Each helper is tested TDD-style before being wired in.

**Tech Stack:** Python, pygame, pytest, engine.board (BitBoard, Color, PieceType)

---

## File Map

| File | Change |
|---|---|
| `src/gui/game_screen.py` | Add `_net_captured_count()`, update `_draw_captured_images()`; add `_next_selection()`, update `_handle_board_click()` |
| `tests/test_gui.py` | Add tests for both new helpers |

---

## Task 1: Net Captured Count — helper + _draw_captured_images

**Files:**
- Modify: `src/gui/game_screen.py`
- Test: `tests/test_gui.py`

- [ ] **Step 1: Write failing test**

Add to `tests/test_gui.py`:

```python
from engine.board import BitBoard, Color, PieceType
from gui.game_screen import _net_captured_count


def _board_with(white_pawns: int, black_pawns: int) -> BitBoard:
    """Minimal board with only pawns set for the two sides."""
    board = BitBoard()
    for i in range(white_pawns):
        board.set_piece(i, Color.WHITE, PieceType.PAWN)
    for i in range(black_pawns):
        board.set_piece(i + 10, Color.BLACK, PieceType.PAWN)
    return board


def test_net_captured_equal_shows_zero():
    # Both sides have 4 pawns remaining — no advantage for either
    board = _board_with(white_pawns=4, black_pawns=4)
    assert _net_captured_count(board, Color.WHITE, PieceType.PAWN) == 0
    assert _net_captured_count(board, Color.BLACK, PieceType.PAWN) == 0


def test_net_captured_white_advantage():
    # White has 4 pawns, Black has 3 → white captured one more pawn net
    board = _board_with(white_pawns=4, black_pawns=3)
    assert _net_captured_count(board, Color.WHITE, PieceType.PAWN) == 1
    assert _net_captured_count(board, Color.BLACK, PieceType.PAWN) == 0


def test_net_captured_black_advantage():
    # White has 3 pawns, Black has 5 → black shows 2
    board = _board_with(white_pawns=3, black_pawns=5)
    assert _net_captured_count(board, Color.WHITE, PieceType.PAWN) == 0
    assert _net_captured_count(board, Color.BLACK, PieceType.PAWN) == 2
```

- [ ] **Step 2: Run test to verify it fails**

```
uv run pytest tests/test_gui.py::test_net_captured_equal_shows_zero -v
```

Expected: `ImportError` or `FAILED` — `_net_captured_count` does not exist yet.

- [ ] **Step 3: Implement `_net_captured_count` in game_screen.py**

Add this function at module level, directly above the `GameScreen` class (around line 52, after the `_is_evaluating_bot` function):

```python
def _net_captured_count(board, color: Color, pt: PieceType) -> int:
    """Returns how many more pieces of type pt color has captured than the opponent.

    Derivation: net = color_remaining - opp_remaining
    (starting counts cancel out in the difference)
    """
    opp = Color(1 - int(color))
    color_remaining = bin(board.pieces[color][pt]).count("1")
    opp_remaining = bin(board.pieces[opp][pt]).count("1")
    return max(0, color_remaining - opp_remaining)
```

- [ ] **Step 4: Run tests to verify they pass**

```
uv run pytest tests/test_gui.py::test_net_captured_equal_shows_zero tests/test_gui.py::test_net_captured_white_advantage tests/test_gui.py::test_net_captured_black_advantage -v
```

Expected: 3 × PASSED

- [ ] **Step 5: Update `_draw_captured_images` to use the helper**

Current code in `src/gui/game_screen.py` lines 486–499:
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

Replace with:
```python
def _draw_captured_images(self, surf: pygame.Surface, x: int, y: int,
                           color: Color, icon_size: int = 16) -> None:
    from gui.assets import get_small_sprite
    opp = Color(1 - int(color))
    cursor_x = x
    for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT, PieceType.PAWN):
        net = _net_captured_count(self._board, color, pt)
        for _ in range(net):
            img = get_small_sprite(opp, pt, icon_size)
            surf.blit(img, (cursor_x, y))
            cursor_x += icon_size + 1
```

- [ ] **Step 6: Run full test suite to confirm no regressions**

```
uv run pytest -v
```

Expected: all tests PASSED.

- [ ] **Step 7: Commit**

```
git add src/gui/game_screen.py tests/test_gui.py
git commit -m "feat: show only net captured-piece advantage in info panel"
```

---

## Task 2: Piece Deselection — helper + _handle_board_click

**Files:**
- Modify: `src/gui/game_screen.py`
- Test: `tests/test_gui.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/test_gui.py`:

```python
from gui.game_screen import _next_selection


def test_reclick_selected_piece_deselects():
    # Clicking the same square as the selected piece should deselect
    result = _next_selection(
        selected_sq=5,
        sq=5,
        piece_info=(Color.WHITE, PieceType.PAWN),
        color=Color.WHITE,
    )
    assert result is None


def test_click_different_own_piece_selects():
    # Clicking a different own piece while another is selected → switch
    result = _next_selection(
        selected_sq=5,
        sq=12,
        piece_info=(Color.WHITE, PieceType.ROOK),
        color=Color.WHITE,
    )
    assert result == 12


def test_click_empty_square_deselects():
    result = _next_selection(
        selected_sq=5,
        sq=8,
        piece_info=None,
        color=Color.WHITE,
    )
    assert result is None


def test_click_opponent_piece_deselects():
    result = _next_selection(
        selected_sq=5,
        sq=20,
        piece_info=(Color.BLACK, PieceType.PAWN),
        color=Color.WHITE,
    )
    assert result is None


def test_first_click_own_piece_selects():
    # No prior selection (selected_sq=None)
    result = _next_selection(
        selected_sq=None,
        sq=10,
        piece_info=(Color.BLACK, PieceType.KNIGHT),
        color=Color.BLACK,
    )
    assert result == 10
```

- [ ] **Step 2: Run tests to verify they fail**

```
uv run pytest tests/test_gui.py::test_reclick_selected_piece_deselects -v
```

Expected: `ImportError` or `FAILED` — `_next_selection` does not exist yet.

- [ ] **Step 3: Implement `_next_selection` in game_screen.py**

Add directly below `_net_captured_count` (still above the `GameScreen` class):

```python
def _next_selection(
    selected_sq: int | None,
    sq: int,
    piece_info: tuple[Color, PieceType] | None,
    color: Color,
) -> int | None:
    if piece_info is not None and piece_info[0] == color:
        if sq == selected_sq:
            return None
        return sq
    return None
```

- [ ] **Step 4: Run tests to verify they pass**

```
uv run pytest tests/test_gui.py::test_reclick_selected_piece_deselects tests/test_gui.py::test_click_different_own_piece_selects tests/test_gui.py::test_click_empty_square_deselects tests/test_gui.py::test_click_opponent_piece_deselects tests/test_gui.py::test_first_click_own_piece_selects -v
```

Expected: 5 × PASSED

- [ ] **Step 5: Update `_handle_board_click` to use the helper**

Current "Select own piece" block in `src/gui/game_screen.py` lines 242–246:
```python
        # Select own piece
        if piece_info is not None and piece_info[0] == color:
            self._selected_sq = sq
        else:
            self._selected_sq = None
```

Replace with:
```python
        # Select own piece (deselects on re-click)
        self._selected_sq = _next_selection(self._selected_sq, sq, piece_info, color)
```

- [ ] **Step 6: Run full test suite to confirm no regressions**

```
uv run pytest -v
```

Expected: all tests PASSED.

- [ ] **Step 7: Commit**

```
git add src/gui/game_screen.py tests/test_gui.py
git commit -m "feat: deselect piece on re-click in _handle_board_click"
```
