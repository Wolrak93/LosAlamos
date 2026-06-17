from __future__ import annotations

from engine.board import PIECE_VALUES, BitBoard, Color, PieceType

_CP = 100  # centipawn multiplier (PIECE_VALUES use pawn=1; we work in centipawns)

_PIECE_CP: dict[PieceType, int] = {pt: PIECE_VALUES[pt] * _CP for pt in PIECE_VALUES}


class Evaluator:
    def __init__(
        self,
        material: bool = True,
        positional: bool = False,
        mobility: bool = False,
    ) -> None:
        self._material = material
        self._positional = positional
        self._mobility = mobility

    def evaluate(self, board: BitBoard) -> int:
        """Return score in centipawns: positive = White advantage."""
        score = 0
        if self._material:
            score += self._material_score(board)
        return score

    def _material_score(self, board: BitBoard) -> int:
        score = 0
        for pt in (PieceType.PAWN, PieceType.KNIGHT, PieceType.ROOK, PieceType.QUEEN):
            w = bin(board.pieces[Color.WHITE][pt]).count("1")
            b = bin(board.pieces[Color.BLACK][pt]).count("1")
            score += (w - b) * _PIECE_CP[pt]
        return score
