from __future__ import annotations
from enum import IntEnum


class Color(IntEnum):
    WHITE = 0
    BLACK = 1


class PieceType(IntEnum):
    PAWN = 0
    KNIGHT = 1
    ROOK = 2
    QUEEN = 3
    KING = 4


PIECE_VALUES: dict[PieceType, int] = {
    PieceType.PAWN: 1,
    PieceType.KNIGHT: 3,
    PieceType.ROOK: 5,
    PieceType.QUEEN: 9,
    PieceType.KING: 0,
}

BOARD_MASK = (1 << 36) - 1


class BitBoard:
    __slots__ = ("pieces", "side_to_move", "halfmove_clock", "position_history", "ply")

    def __init__(self) -> None:
        # pieces[color][piece_type] = bitboard (int, bit N = square N)
        self.pieces: list[list[int]] = [[0] * 5 for _ in range(2)]
        self.side_to_move: Color = Color.WHITE
        self.halfmove_clock: int = 0
        self.position_history: list[int] = []
        self.ply: int = 0

    def set_piece(self, sq: int, color: Color, pt: PieceType) -> None:
        self.pieces[color][pt] |= 1 << sq

    def remove_piece(self, sq: int, color: Color, pt: PieceType) -> None:
        self.pieces[color][pt] &= ~(1 << sq)

    def get_piece_at(self, sq: int) -> tuple[Color, PieceType] | None:
        mask = 1 << sq
        for color in (Color.WHITE, Color.BLACK):
            for pt in PieceType:
                if self.pieces[color][pt] & mask:
                    return (color, pt)
        return None

    def occupancy(self, color: Color | None = None) -> int:
        if color is None:
            return self.occupancy(Color.WHITE) | self.occupancy(Color.BLACK)
        result = 0
        for pt in range(5):
            result |= self.pieces[color][pt]
        return result

    def copy(self) -> BitBoard:
        new = BitBoard.__new__(BitBoard)
        new.pieces = [row[:] for row in self.pieces]
        new.side_to_move = self.side_to_move
        new.halfmove_clock = self.halfmove_clock
        new.position_history = self.position_history[:]
        new.ply = self.ply
        return new
