from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from engine.board import BitBoard, Color, PieceType
from engine.move import Move
from engine.movegen import find_king_sq, generate_legal_moves, is_square_attacked
from engine.zobrist import compute_hash


class GameResult(Enum):
    IN_PROGRESS = auto()
    WHITE_WINS = auto()
    BLACK_WINS = auto()
    DRAW = auto()


@dataclass
class GameOutcome:
    result: GameResult
    reason: str


def is_in_check(board: BitBoard) -> bool:
    color = board.side_to_move
    opp = Color(1 - int(color))
    king_sq = find_king_sq(board, color)
    return is_square_attacked(board, king_sq, opp)


def has_insufficient_material(board: BitBoard) -> bool:
    for color in (Color.WHITE, Color.BLACK):
        pieces = board.pieces[color]
        if (pieces[PieceType.ROOK] or pieces[PieceType.QUEEN]
                or pieces[PieceType.PAWN]):
            return False
        # King + Knight only
        knight_count = bin(pieces[PieceType.KNIGHT]).count("1")
        if knight_count > 1:
            return False
    return True


def get_game_outcome(board: BitBoard) -> GameOutcome | None:
    # 50-move rule
    if board.halfmove_clock >= 100:
        return GameOutcome(GameResult.DRAW, "50-Züge-Regel")

    # Threefold repetition
    current_hash = compute_hash(board)
    if board.position_history.count(current_hash) >= 2:
        return GameOutcome(GameResult.DRAW, "Dreifache Stellungswiederholung")

    # Insufficient material
    if has_insufficient_material(board):
        return GameOutcome(GameResult.DRAW, "Unzureichendes Material")

    # No legal moves
    legal = generate_legal_moves(board)
    if not legal:
        if is_in_check(board):
            winner = (
                GameResult.BLACK_WINS
                if board.side_to_move == Color.WHITE
                else GameResult.WHITE_WINS
            )
            return GameOutcome(winner, "Schachmatt")
        return GameOutcome(GameResult.DRAW, "Patt")

    return None


def play_move(board: BitBoard, move: Move) -> None:
    move.apply(board)
    board.position_history.append(compute_hash(board))
