# src/bots/mcts_bot.py
from __future__ import annotations

import math
import random
import time

from bots.base import Bot
from bots.evaluator import Evaluator
from engine.board import BitBoard, Color
from engine.gamestate import GameResult, get_game_outcome, play_move
from engine.move import Move
from engine.movegen import generate_legal_moves

_C = math.sqrt(2)
_ROLLOUT_DEPTH = 6
_NORM_MAX = 3000.0


class _Node:
    __slots__ = ("board", "parent", "move", "children", "visits", "total_score", "untried_moves")

    def __init__(self, board: BitBoard, parent: _Node | None = None, move: Move | None = None) -> None:
        self.board = board
        self.parent = parent
        self.move = move
        self.children: list[_Node] = []
        self.visits = 0
        self.total_score = 0.0
        self.untried_moves: list[Move] = generate_legal_moves(board)

    def uct(self) -> float:
        if self.visits == 0:
            return float("inf")
        assert self.parent is not None
        return (self.total_score / self.visits
                + _C * math.sqrt(math.log(self.parent.visits) / self.visits))

    def best_uct_child(self) -> _Node:
        return max(self.children, key=lambda c: c.uct())

    def most_visited_child(self) -> _Node:
        return max(self.children, key=lambda c: c.visits)


class MCTSBot(Bot):
    def __init__(self, evaluator: Evaluator, name: str) -> None:
        super().__init__(name)
        self._evaluator = evaluator

    def choose_move(self, board: BitBoard, time_budget_seconds: float | None = None) -> Move:
        budget = 120.0 if time_budget_seconds is None else time_budget_seconds
        deadline = time.monotonic() + budget * 0.9
        root = _Node(board.copy())

        while time.monotonic() < deadline:
            node = self._select(root)
            outcome = get_game_outcome(node.board)
            if outcome is None and node.untried_moves:
                node = self._expand(node)
            score = self._simulate(node, board.side_to_move)
            self._backpropagate(node, score)

        if not root.children:
            return generate_legal_moves(board)[0]
        return root.most_visited_child().move  # type: ignore[return-value]

    def _select(self, node: _Node) -> _Node:
        while not node.untried_moves and node.children:
            node = node.best_uct_child()
        return node

    def _expand(self, node: _Node) -> _Node:
        move = node.untried_moves.pop(random.randrange(len(node.untried_moves)))
        child_board = node.board.copy()
        play_move(child_board, move)
        child = _Node(child_board, parent=node, move=move)
        node.children.append(child)
        return child

    def _simulate(self, node: _Node, root_side: Color) -> float:
        b = node.board.copy()
        for _ in range(_ROLLOUT_DEPTH):
            outcome = get_game_outcome(b)
            if outcome is not None:
                return self._terminal_score(outcome, root_side)
            moves = generate_legal_moves(b)
            play_move(b, random.choice(moves))

        raw = self._evaluator.evaluate(b)
        normalized = 0.5 + raw / (2 * _NORM_MAX)
        normalized = max(0.0, min(1.0, normalized))
        if root_side == Color.BLACK:
            normalized = 1.0 - normalized
        return normalized

    @staticmethod
    def _terminal_score(outcome, root_side: Color) -> float:
        if outcome.result == GameResult.DRAW:
            return 0.5
        if outcome.result == GameResult.WHITE_WINS:
            return 1.0 if root_side == Color.WHITE else 0.0
        return 0.0 if root_side == Color.WHITE else 1.0

    def _backpropagate(self, node: _Node, score: float) -> None:
        n: _Node | None = node
        while n is not None:
            n.visits += 1
            n.total_score += score
            n = n.parent
