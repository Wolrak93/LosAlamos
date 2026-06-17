from __future__ import annotations

import random

from engine.board import BitBoard, Color, PieceType

_NORMAL_BACK = [
    PieceType.ROOK, PieceType.KNIGHT, PieceType.QUEEN,
    PieceType.KING, PieceType.KNIGHT, PieceType.ROOK,
]


def _place_back_rank(board: BitBoard, color: Color, pieces: list[PieceType]) -> None:
    rank = 0 if color == Color.WHITE else 5
    for file, pt in enumerate(pieces):
        board.set_piece(rank * 6 + file, color, pt)


def _place_pawns(board: BitBoard, color: Color) -> None:
    rank = 1 if color == Color.WHITE else 4
    for file in range(6):
        board.set_piece(rank * 6 + file, color, PieceType.PAWN)


def _random_back_rank() -> list[PieceType]:
    pieces = _NORMAL_BACK[:]
    random.shuffle(pieces)
    return pieces


def make_starting_board(mode: str = "normal") -> BitBoard:
    board = BitBoard()
    if mode == "random_sym":
        back = _random_back_rank()
        _place_back_rank(board, Color.WHITE, back)
        _place_back_rank(board, Color.BLACK, back)
    elif mode == "random_asym":
        _place_back_rank(board, Color.WHITE, _random_back_rank())
        _place_back_rank(board, Color.BLACK, _random_back_rank())
    else:  # normal
        _place_back_rank(board, Color.WHITE, _NORMAL_BACK)
        _place_back_rank(board, Color.BLACK, _NORMAL_BACK)
    _place_pawns(board, Color.WHITE)
    _place_pawns(board, Color.BLACK)
    return board
