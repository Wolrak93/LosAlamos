from __future__ import annotations

import random

from bots.base import Bot
from engine.board import PIECE_VALUES, BitBoard, PieceType
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
    def choose_move(self, board: BitBoard) -> Move:
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
