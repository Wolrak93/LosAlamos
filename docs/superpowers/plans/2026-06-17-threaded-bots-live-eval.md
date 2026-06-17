# Threaded Bots & Live Eval Display Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run bots in background threads so the clock ticks in real time during thinking, and show live search depth / simulation count plus the bot's actual eval in the info panel.

**Architecture:** A `BotProgress` shared object is passed to each bot's `choose_move`; bots write live updates to it while the main thread polls it each frame. `GameScreen` spawns a daemon thread per bot move and polls `thread.is_alive()` in `update()` to apply the result without blocking. The eval bar and number are driven by `BotProgress.eval` (pawn units, positive = White advantage) instead of the material count.

**Tech Stack:** Python threading (`threading.Thread`), pygame event loop, existing bot/evaluator infrastructure.

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `src/bots/progress.py` | **Create** | `BotProgress` dataclass |
| `tests/test_progress.py` | **Create** | Tests for `BotProgress` |
| `src/bots/base.py` | **Modify** | Add `progress` param to abstract signature |
| `src/bots/random_bot.py` | **Modify** | Accept and ignore `progress` |
| `src/bots/greedy_bot.py` | **Modify** | Compute material eval, write to `progress` |
| `tests/test_bots.py` | **Modify** | Add GreedyBot progress test |
| `src/bots/minimax_bot.py` | **Modify** | Return score from `_search_root`, write depth+eval to `progress` |
| `tests/test_minimax.py` | **Modify** | Add MinimaxBot progress test |
| `src/bots/mcts_bot.py` | **Modify** | Count sims, write every 100 iterations |
| `tests/test_mcts.py` | **Modify** | Add MCTSBot progress test |
| `src/gui/game_screen.py` | **Modify** | Thread management + eval display |

---

## Task 1: Create `BotProgress` dataclass

**Files:**
- Create: `src/bots/progress.py`
- Create: `tests/test_progress.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_progress.py
from bots.progress import BotProgress


def test_bot_progress_defaults_to_none():
    p = BotProgress()
    assert p.depth is None
    assert p.eval is None
    assert p.sims is None


def test_bot_progress_fields_can_be_set():
    p = BotProgress()
    p.depth = 5
    p.eval = -1.5
    p.sims = 1200
    assert p.depth == 5
    assert p.eval == -1.5
    assert p.sims == 1200
```

- [ ] **Step 2: Run tests to verify they fail**

```
uv run pytest tests/test_progress.py -v
```

Expected: `ModuleNotFoundError: No module named 'bots.progress'`

- [ ] **Step 3: Create `src/bots/progress.py`**

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BotProgress:
    depth: int | None = None    # Minimax: completed search depth
    eval: float | None = None   # pawn units, positive = White advantage
    sims: int | None = None     # MCTS: total simulations completed
```

- [ ] **Step 4: Run tests to verify they pass**

```
uv run pytest tests/test_progress.py -v
```

Expected: 2 PASSED

- [ ] **Step 5: Commit**

```
git add src/bots/progress.py tests/test_progress.py
git commit -m "feat: add BotProgress dataclass for live bot thinking updates"
```

---

## Task 2: Update `Bot` base class signature

**Files:**
- Modify: `src/bots/base.py:14`

- [ ] **Step 1: Update the abstract method**

Replace line 14 of `src/bots/base.py`:

```python
    @abstractmethod
    def choose_move(self, board: BitBoard, time_budget_seconds: float | None = None) -> Move: ...
```

with:

```python
    @abstractmethod
    def choose_move(
        self,
        board: BitBoard,
        time_budget_seconds: float | None = None,
        progress: "BotProgress | None" = None,
    ) -> Move: ...
```

Also add the import at the top of the file after the existing imports:

```python
from bots.progress import BotProgress
```

The full updated `src/bots/base.py`:

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from bots.progress import BotProgress
from engine.board import BitBoard
from engine.move import Move


class Bot(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def choose_move(
        self,
        board: BitBoard,
        time_budget_seconds: float | None = None,
        progress: BotProgress | None = None,
    ) -> Move: ...
```

- [ ] **Step 2: Run existing bot tests to verify nothing broke**

```
uv run pytest tests/test_bots.py tests/test_minimax.py tests/test_mcts.py -v
```

Expected: all PASSED (base class change doesn't break concrete bots yet — they'll be updated in Tasks 3-6)

- [ ] **Step 3: Commit**

```
git add src/bots/base.py
git commit -m "feat: add progress param to Bot.choose_move abstract signature"
```

---

## Task 3: Update `RandomBot`

**Files:**
- Modify: `src/bots/random_bot.py:12`

- [ ] **Step 1: Update `choose_move`**

Full updated `src/bots/random_bot.py`:

```python
from __future__ import annotations

import random

from bots.base import Bot
from bots.progress import BotProgress
from engine.board import BitBoard
from engine.move import Move
from engine.movegen import generate_legal_moves


class RandomBot(Bot):
    def choose_move(
        self,
        board: BitBoard,
        time_budget_seconds: float | None = None,
        progress: BotProgress | None = None,
    ) -> Move:
        return random.choice(generate_legal_moves(board))
```

- [ ] **Step 2: Run tests**

```
uv run pytest tests/test_bots.py::test_random_bot_returns_legal_move -v
```

Expected: PASSED

- [ ] **Step 3: Commit**

```
git add src/bots/random_bot.py
git commit -m "feat: add progress param to RandomBot.choose_move (no-op)"
```

---

## Task 4: Update `GreedyBot` — write material eval to progress

**Files:**
- Modify: `src/bots/greedy_bot.py`
- Modify: `tests/test_bots.py`

- [ ] **Step 1: Write the failing test**

Add to the bottom of `tests/test_bots.py`:

```python
def test_greedy_bot_writes_eval_to_progress():
    from bots.progress import BotProgress
    b = BitBoard()
    b.set_piece(3, Color.WHITE, PieceType.KING)
    b.set_piece(33, Color.BLACK, PieceType.KING)
    b.set_piece(6, Color.WHITE, PieceType.ROOK)   # White has a rook (value=5)
    bot = GreedyBot("Greed")
    p = BotProgress()
    bot.choose_move(b, progress=p)
    assert p.eval is not None
    assert p.eval == 5.0   # White up a rook = +5 pawn units
```

- [ ] **Step 2: Run test to verify it fails**

```
uv run pytest tests/test_bots.py::test_greedy_bot_writes_eval_to_progress -v
```

Expected: FAILED — `BotProgress` not accepted by old `choose_move`

- [ ] **Step 3: Update `src/bots/greedy_bot.py`**

Full updated file:

```python
from __future__ import annotations

import random

from bots.base import Bot
from bots.progress import BotProgress
from engine.board import PIECE_VALUES, BitBoard, Color, PieceType
from engine.gamestate import GameResult, get_game_outcome, play_move
from engine.move import Move
from engine.movegen import generate_legal_moves


def _score(move: Move) -> int:
    score = 0
    if move.captured is not None:
        score += PIECE_VALUES[move.captured]
    if move.promotion is not None:
        score += PIECE_VALUES[move.promotion] - PIECE_VALUES[PieceType.PAWN]
    return score


class GreedyBot(Bot):
    def choose_move(
        self,
        board: BitBoard,
        time_budget_seconds: float | None = None,
        progress: BotProgress | None = None,
    ) -> Move:
        if progress is not None:
            white_mat = sum(
                bin(board.pieces[Color.WHITE][pt]).count("1") * PIECE_VALUES[pt]
                for pt in PieceType if pt != PieceType.KING
            )
            black_mat = sum(
                bin(board.pieces[Color.BLACK][pt]).count("1") * PIECE_VALUES[pt]
                for pt in PieceType if pt != PieceType.KING
            )
            progress.eval = float(white_mat - black_mat)

        legal = generate_legal_moves(board)

        # 1. Checkmate in 1
        for move in legal:
            copy = board.copy()
            play_move(copy, move)
            outcome = get_game_outcome(copy)
            if outcome is not None and outcome.result in (
                GameResult.WHITE_WINS, GameResult.BLACK_WINS
            ):
                return move

        # 2. Best material gain
        best_score = max(_score(m) for m in legal)
        best_moves = [m for m in legal if _score(m) == best_score]
        chosen = random.choice(best_moves)

        # Prefer queen promotion among equal-score moves
        if chosen.promotion is not None:
            queen_moves = [m for m in best_moves if m.promotion == PieceType.QUEEN]
            if queen_moves:
                return random.choice(queen_moves)
        return chosen
```

- [ ] **Step 4: Run tests**

```
uv run pytest tests/test_bots.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```
git add src/bots/greedy_bot.py tests/test_bots.py
git commit -m "feat: write material eval to BotProgress in GreedyBot"
```

---

## Task 5: Update `MinimaxBot` — return score from `_search_root`, write depth+eval to progress

**Files:**
- Modify: `src/bots/minimax_bot.py:118-153`
- Modify: `tests/test_minimax.py`

- [ ] **Step 1: Write the failing test**

Add to the bottom of `tests/test_minimax.py`:

```python
def test_minimax_writes_progress():
    from bots.progress import BotProgress
    from engine.positions import make_starting_board
    board = make_starting_board()
    bot = _make_minimax()
    p = BotProgress()
    bot.choose_move(board, time_budget_seconds=1.0, progress=p)
    assert p.depth is not None
    assert p.depth >= 1
    assert p.eval is not None
    assert isinstance(p.eval, float)
```

- [ ] **Step 2: Run test to verify it fails**

```
uv run pytest tests/test_minimax.py::test_minimax_writes_progress -v
```

Expected: FAILED

- [ ] **Step 3: Update `src/bots/minimax_bot.py`**

Change the imports at the top — add `BotProgress`:

```python
from bots.progress import BotProgress
```

Change `_search_root` (lines 137-153) to return the score along with the move:

```python
def _search_root(self, board: BitBoard, depth: int, deadline: float, tt: dict) -> tuple[Move, int] | None:
    moves = generate_legal_moves(board)
    moves.sort(key=_mvv_lva, reverse=True)
    best_move: Move | None = None
    alpha = -_MATE - 1

    for move in moves:
        if time.monotonic() > deadline:
            return None
        child = board.copy()
        play_move(child, move)
        score = -_negamax(child, depth - 1, -_MATE - 1, -alpha, self._evaluator, tt, deadline, ply=1)
        if score > alpha:
            alpha = score
            best_move = move

    if best_move is None:
        return None
    return (best_move, alpha)
```

Change `choose_move` (lines 118-135):

```python
def choose_move(
    self,
    board: BitBoard,
    time_budget_seconds: float | None = None,
    progress: BotProgress | None = None,
) -> Move:
    budget = 120.0 if time_budget_seconds is None else time_budget_seconds
    start = time.monotonic()
    deadline = start + budget
    soft_deadline = start + budget * 0.9
    tt: dict = {}
    best_move: Move | None = None

    for depth in range(1, _MAX_DEPTH + 1):
        if time.monotonic() >= soft_deadline:
            break
        result = self._search_root(board, depth, deadline, tt)
        if result is not None:
            best_move, best_score = result
            if progress is not None:
                eval_white = best_score if board.side_to_move == Color.WHITE else -best_score
                progress.depth = depth
                progress.eval = eval_white / 100.0

    if best_move is None:
        best_move = generate_legal_moves(board)[0]
    return best_move
```

- [ ] **Step 4: Run tests**

```
uv run pytest tests/test_minimax.py -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```
git add src/bots/minimax_bot.py tests/test_minimax.py
git commit -m "feat: write search depth and eval to BotProgress in MinimaxBot"
```

---

## Task 6: Update `MCTSBot` — count simulations, write every 100 to progress

**Files:**
- Modify: `src/bots/mcts_bot.py:51-66`
- Modify: `tests/test_mcts.py`

- [ ] **Step 1: Write the failing test**

Add to the bottom of `tests/test_mcts.py`:

```python
def test_mcts_writes_progress():
    from bots.progress import BotProgress
    board = make_starting_board()
    bot = _make_mcts()
    p = BotProgress()
    bot.choose_move(board, time_budget_seconds=1.0, progress=p)
    # 1 second is enough for >100 simulations
    assert p.sims is not None
    assert p.sims >= 100
    assert p.eval is not None
    assert isinstance(p.eval, float)
```

- [ ] **Step 2: Run test to verify it fails**

```
uv run pytest tests/test_mcts.py::test_mcts_writes_progress -v
```

Expected: FAILED

- [ ] **Step 3: Update `src/bots/mcts_bot.py`**

Add the import after existing imports:

```python
from bots.progress import BotProgress
```

Replace `choose_move` (lines 51-66):

```python
def choose_move(
    self,
    board: BitBoard,
    time_budget_seconds: float | None = None,
    progress: BotProgress | None = None,
) -> Move:
    budget = 120.0 if time_budget_seconds is None else time_budget_seconds
    deadline = time.monotonic() + budget * 0.9
    root = _Node(board.copy())
    root_side = board.side_to_move
    total_sims = 0

    while time.monotonic() < deadline:
        node = self._select(root)
        outcome = get_game_outcome(node.board)
        if outcome is None and node.untried_moves:
            node = self._expand(node)
        score = self._simulate(node, root_side)
        self._backpropagate(node, score)
        total_sims += 1

        if progress is not None and total_sims % 100 == 0 and root.children:
            best = max(root.children, key=lambda c: c.visits)
            if best.visits > 0:
                win_rate = best.total_score / best.visits
                eval_cp = (win_rate - 0.5) * 2 * _NORM_MAX
                progress.sims = total_sims
                progress.eval = eval_cp / 100.0 if root_side == Color.WHITE else -eval_cp / 100.0

    if not root.children:
        return generate_legal_moves(board)[0]
    return root.most_visited_child().move  # type: ignore[return-value]
```

- [ ] **Step 4: Run tests**

```
uv run pytest tests/test_mcts.py -v
```

Expected: all PASSED

- [ ] **Step 5: Run full test suite to verify nothing regressed**

```
uv run pytest -v
```

Expected: all PASSED

- [ ] **Step 6: Commit**

```
git add src/bots/mcts_bot.py tests/test_mcts.py
git commit -m "feat: write simulation count and eval to BotProgress in MCTSBot"
```

---

## Task 7: Add threading to `GameScreen`

**Files:**
- Modify: `src/gui/game_screen.py`

No automated test — verified manually by running the game (see final step).

- [ ] **Step 1: Add imports at the top of `src/gui/game_screen.py`**

After `import pygame` (line 3), add:

```python
import threading
```

After the existing `from gui.main_menu import GameConfig` import (line 44), add:

```python
from bots.progress import BotProgress
```

- [ ] **Step 2: Add new state fields to `GameScreen.__init__`**

After `self._maybe_schedule_bot()` (currently the last line of `__init__`, line 115), insert these fields BEFORE the `_maybe_schedule_bot()` call (i.e., just above that line):

```python
        # Bot threading
        self._bot_thread: threading.Thread | None = None
        self._bot_progress: BotProgress | None = None
        self._bot_result: list = [None]
        self._last_eval: dict[Color, float | None] = {
            Color.WHITE: None,
            Color.BLACK: None,
        }
```

- [ ] **Step 3: Update `handle_event` — replace `_execute_bot_move` call**

In `handle_event` (line 129), change:

```python
            self._execute_bot_move()
```

to:

```python
            self._start_bot_thread()
```

- [ ] **Step 4: Update `update()` — add thread polling before clock logic**

Replace the full `update` method (lines 138-158) with:

```python
    def update(self, dt: float) -> None:
        if self._outcome is not None:
            return
        if self._promo_sq is not None:
            return
        # Poll bot thread for completion
        if self._bot_thread is not None and not self._bot_thread.is_alive():
            move = self._bot_result[0]
            color = self._board.side_to_move
            if self._bot_progress is not None and self._bot_progress.eval is not None:
                self._last_eval[color] = self._bot_progress.eval
            self._bot_thread = None
            self._bot_progress = None
            if move is not None:
                self._make_move(move)
        # Clock
        if self._use_clock:
            color = self._board.side_to_move
            self._clocks[color] -= dt
            if self._clocks[color] <= 0:
                self._clocks[color] = 0
                loser = color
                winner_result = (
                    GameResult.BLACK_WINS if loser == Color.WHITE
                    else GameResult.WHITE_WINS
                )
                from engine.gamestate import _side_has_insufficient_material
                winner_color = Color(1 - int(loser))
                if _side_has_insufficient_material(self._board, winner_color):
                    self._outcome = GameOutcome(GameResult.DRAW, "Unzureichendes Material")
                else:
                    self._outcome = GameOutcome(winner_result, "Zeit abgelaufen")
```

- [ ] **Step 5: Replace `_execute_bot_move` with `_start_bot_thread`**

Replace the entire `_execute_bot_move` method (lines 373-385) with:

```python
    def _start_bot_thread(self) -> None:
        if self._outcome is not None:
            return
        if self._bot_thread is not None:
            return  # already thinking
        color = self._board.side_to_move
        bot = self._config.white_bot if color == Color.WHITE else self._config.black_bot
        if bot is None or not self._legal_moves:
            return
        from bots.personalities import calculate_time_budget
        remaining = self._clocks[color] if self._use_clock else None
        move_number = self._board.ply // 2 + 1
        budget = calculate_time_budget(remaining, move_number, self._increment)
        board_copy = self._board.copy()
        self._bot_result = [None]
        self._bot_progress = BotProgress()
        result_holder = self._bot_result
        progress = self._bot_progress

        def _run() -> None:
            result_holder[0] = bot.choose_move(board_copy, budget, progress)

        self._bot_thread = threading.Thread(target=_run, daemon=True)
        self._bot_thread.start()
```

- [ ] **Step 6: Run existing tests to verify nothing broke**

```
uv run pytest tests/test_gui.py -v
```

Expected: all PASSED

- [ ] **Step 7: Commit**

```
git add src/gui/game_screen.py
git commit -m "feat: run bots in background thread so clock ticks during thinking"
```

---

## Task 8: Update eval display — use bot eval instead of material count

**Files:**
- Modify: `src/gui/game_screen.py`

- [ ] **Step 1: Replace `_draw_eval_bar` (lines 490-516)**

Replace the entire `_draw_eval_bar` method with:

```python
    def _draw_eval_bar(self, surf: pygame.Surface, rect: pygame.Rect,
                       color: Color, eval_value: float | None) -> None:
        if eval_value is None:
            white_frac = 0.5
        else:
            clamped = max(-5.0, min(5.0, eval_value))
            white_frac = (clamped + 5.0) / 10.0

        pygame.draw.rect(surf, (90, 58, 26), rect, border_radius=3)
        white_w = int(rect.width * white_frac)
        if white_w > 0:
            pygame.draw.rect(surf,
                             (240, 217, 181),
                             pygame.Rect(rect.x, rect.y, white_w, rect.height),
                             border_radius=3)
```

- [ ] **Step 2: Remove `_calc_eval_diff` (lines 518-527)**

Delete the entire `_calc_eval_diff` method:

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

- [ ] **Step 3: Replace the eval section inside `draw_player` (lines 433-455)**

Find the block that starts with `# Eval: only for evaluating bots` inside `draw_player`. Replace everything from that comment through `y += et.get_height() + 6` with:

```python
            # Eval: only for evaluating bots
            if evaluating:
                lbl = font_label.render(
                    f"EVAL {'WEISS' if color == Color.WHITE else 'SCHWARZ'}",
                    True, TEXT_MUTED
                )
                surf.blit(lbl, (INFO_X + 8, y))
                y += lbl.get_height() + 3

                is_thinking = (
                    self._bot_thread is not None
                    and self._board.side_to_move == color
                )
                if is_thinking and self._bot_progress is not None:
                    current_eval = self._bot_progress.eval
                else:
                    current_eval = self._last_eval[color]

                self._draw_eval_bar(
                    surf, pygame.Rect(INFO_X + 8, y, INFO_W - 16, 8), color, current_eval
                )
                y += 14

                if current_eval is not None:
                    sign = "+" if current_eval > 0 else ""
                    eval_str = f"{sign}{current_eval:.2f}"
                    if current_eval > 0:
                        eval_color = ACCENT
                    elif current_eval < 0:
                        eval_color = (160, 60, 60)
                    else:
                        eval_color = TEXT_MUTED
                else:
                    eval_str = "—"
                    eval_color = TEXT_MUTED
                et = font_eval.render(eval_str, True, eval_color)
                surf.blit(et, (INFO_X + INFO_W // 2 - et.get_width() // 2, y))
                y += et.get_height() + 2

                # Depth / sims during thinking
                if is_thinking and self._bot_progress is not None:
                    from bots.minimax_bot import MinimaxBot
                    from bots.mcts_bot import MCTSBot
                    bot = self._config.white_bot if color == Color.WHITE else self._config.black_bot
                    if isinstance(bot, MinimaxBot) and self._bot_progress.depth is not None:
                        status_str = f"Tiefe {self._bot_progress.depth}"
                    elif isinstance(bot, MCTSBot) and self._bot_progress.sims is not None:
                        status_str = f"{self._bot_progress.sims:,} Sims".replace(",", " ")
                    else:
                        status_str = None
                    if status_str is not None:
                        st = font_label.render(status_str, True, TEXT_MUTED)
                        surf.blit(st, (INFO_X + INFO_W // 2 - st.get_width() // 2, y))
                        y += st.get_height() + 4
                    else:
                        y += 4
                else:
                    y += 4
```

- [ ] **Step 4: Run full test suite**

```
uv run pytest -v
```

Expected: all PASSED

- [ ] **Step 5: Commit**

```
git add src/gui/game_screen.py
git commit -m "feat: show live bot eval and search depth/sims in info panel"
```

---

## Final Verification

- [ ] **Start the game and run MinimaxBot vs RandomBot**

```
uv run python src/main.py
```

Verify:
1. MinimaxBot's clock counts down in real time while it thinks
2. "Tiefe N" appears below the eval number and updates as depth increases
3. Eval number and bar update each time a new depth completes
4. When MinimaxBot finishes its move, depth label disappears and last eval persists

- [ ] **Run MCTSBot vs RandomBot**

Verify:
1. "N Sims" appears and updates every 100 simulations
2. Eval updates alongside the sim count
3. Bot clock ticks normally

- [ ] **Run MinimaxBot vs MinimaxBot**

Verify:
1. UI remains responsive (clock animates, no freeze)
2. Each bot's eval panel shows its own thinking state
