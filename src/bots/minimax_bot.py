# src/bots/minimax_bot.py
from __future__ import annotations

import time

from bots.base import Bot
from bots.evaluator import Evaluator
from bots.progress import BotProgress
from engine.board import PIECE_VALUES, BitBoard, Color
from engine.gamestate import GameResult, get_game_outcome, play_move
from engine.move import Move
from engine.movegen import generate_legal_moves
from engine.zobrist import compute_hash

_MATE = 100_000
_MAX_DEPTH = 20

_EXACT = 0
_LOWER = 1
_UPPER = 2


def _mvv_lva(move: Move) -> int:
    if move.captured is None:
        return 0
    return PIECE_VALUES[move.captured] * 100 - PIECE_VALUES[move.piece]


def _negamax(
    board: BitBoard,
    depth: int,
    alpha: int,
    beta: int,
    evaluator: Evaluator,
    tt: dict,
    deadline: float,
    ply: int = 0,
) -> int:
    h = compute_hash(board)
    tt_entry = tt.get(h)
    if tt_entry is not None:
        tt_depth, tt_flag, tt_score = tt_entry
        if tt_depth >= depth:
            if tt_flag == _EXACT:
                return tt_score
            elif tt_flag == _LOWER:
                alpha = max(alpha, tt_score)
            else:
                beta = min(beta, tt_score)
            if alpha >= beta:
                return tt_score

    outcome = get_game_outcome(board)
    if outcome is not None:
        if outcome.result == GameResult.DRAW:
            return 0
        # Return mate score adjusted for distance: closer mates score higher
        return -(_MATE - ply)

    if depth == 0:
        return _quiescence(board, alpha, beta, evaluator)

    moves = generate_legal_moves(board)
    moves.sort(key=_mvv_lva, reverse=True)

    best = -_MATE - 1
    flag = _UPPER

    for move in moves:
        if time.monotonic() > deadline:
            break
        child = board.copy()
        play_move(child, move)
        score = -_negamax(child, depth - 1, -beta, -alpha, evaluator, tt, deadline, ply + 1)
        if score > best:
            best = score
        if score > alpha:
            alpha = score
            flag = _EXACT
        if alpha >= beta:
            flag = _LOWER
            break

    tt[h] = (depth, flag, best)
    return best


def _quiescence(board: BitBoard, alpha: int, beta: int, evaluator: Evaluator, depth: int = 4) -> int:
    raw = evaluator.evaluate(board)
    stand_pat = raw if board.side_to_move == Color.WHITE else -raw

    if stand_pat >= beta:
        return beta
    if stand_pat > alpha:
        alpha = stand_pat
    if depth == 0:
        return alpha

    captures = [m for m in generate_legal_moves(board) if m.captured is not None]
    captures.sort(key=_mvv_lva, reverse=True)

    for move in captures:
        child = board.copy()
        play_move(child, move)
        score = -_quiescence(child, -beta, -alpha, evaluator, depth - 1)
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


class MinimaxBot(Bot):
    def __init__(self, evaluator: Evaluator, name: str) -> None:
        super().__init__(name)
        self._evaluator = evaluator

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
