from __future__ import annotations

from engine.board import PIECE_VALUES, BitBoard, Color, PieceType

_CP = 100  # centipawn multiplier (PIECE_VALUES use pawn=1; we work in centipawns)

_PIECE_CP: dict[PieceType, int] = {pt: PIECE_VALUES[pt] * _CP for pt in PIECE_VALUES}

# Piece-Square Tables for White (index = square, rank 0 at bottom).
# Black uses vertical mirror: index = (5 - rank)*6 + file.

_PAWN_PST = [
     0,  0,  0,  0,  0,  0,   # rank 0 (back rank — no pawns)
     0,  0,  5,  5,  0,  0,   # rank 1 (start)
     5,  5, 10, 10,  5,  5,   # rank 2
    10, 10, 20, 20, 10, 10,   # rank 3
    20, 20, 30, 30, 20, 20,   # rank 4
    30, 30, 40, 40, 30, 30,   # rank 5 (promotion)
]

_KNIGHT_PST = [
   -30, -20, -10, -10, -20, -30,
   -20,   0,  10,  10,   0, -20,
   -10,  10,  20,  20,  10, -10,
   -10,  10,  20,  20,  10, -10,
   -20,   0,  10,  10,   0, -20,
   -30, -20, -10, -10, -20, -30,
]

_ROOK_PST = [
     0,  0,  5,  5,  0,  0,
     0,  0,  5,  5,  0,  0,
     0,  0,  5,  5,  0,  0,
     5,  5, 10, 10,  5,  5,
    10, 10, 15, 15, 10, 10,
    10, 10, 15, 15, 10, 10,
]

_QUEEN_PST = [
   -10, -5,  0,  0, -5,-10,
    -5,  5, 10, 10,  5, -5,
     0, 10, 15, 15, 10,  0,
     0, 10, 15, 15, 10,  0,
    -5,  5, 10, 10,  5, -5,
   -10, -5,  0,  0, -5,-10,
]

_KING_MG_PST = [   # midgame: safety near own corners
    20, 15, -5, -5, 15, 20,
    10,  5,-10,-10,  5, 10,
   -10,-20,-30,-30,-20,-10,
   -20,-30,-40,-40,-30,-20,
   -30,-40,-50,-50,-40,-30,
   -40,-50,-60,-60,-50,-40,
]

_KING_EG_PST = [   # endgame (<=6 pieces): activity in center
   -20,-10,  0,  0,-10,-20,
   -10,  5, 10, 10,  5,-10,
     0, 10, 20, 20, 10,  0,
     0, 10, 20, 20, 10,  0,
   -10,  5, 10, 10,  5,-10,
   -20,-10,  0,  0,-10,-20,
]

_PST: dict[PieceType, list[int]] = {
    PieceType.PAWN:   _PAWN_PST,
    PieceType.KNIGHT: _KNIGHT_PST,
    PieceType.ROOK:   _ROOK_PST,
    PieceType.QUEEN:  _QUEEN_PST,
    PieceType.KING:   _KING_MG_PST,  # replaced dynamically in endgame
}


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
        if self._positional:
            score += self._positional_score(board)
        return score

    def _material_score(self, board: BitBoard) -> int:
        score = 0
        for pt in (PieceType.PAWN, PieceType.KNIGHT, PieceType.ROOK, PieceType.QUEEN):
            w = bin(board.pieces[Color.WHITE][pt]).count("1")
            b = bin(board.pieces[Color.BLACK][pt]).count("1")
            score += (w - b) * _PIECE_CP[pt]
        return score

    def _positional_score(self, board: BitBoard) -> int:
        is_endgame = bin(board.occupancy()).count("1") <= 6
        king_pst = _KING_EG_PST if is_endgame else _KING_MG_PST
        score = 0
        for pt in PieceType:
            pst = king_pst if pt == PieceType.KING else _PST[pt]
            # White pieces
            bb = board.pieces[Color.WHITE][pt]
            while bb:
                lsb = bb & -bb
                sq = lsb.bit_length() - 1
                score += pst[sq]
                bb ^= lsb
            # Black pieces (mirror rank)
            bb = board.pieces[Color.BLACK][pt]
            while bb:
                lsb = bb & -bb
                sq = lsb.bit_length() - 1
                rank, file = divmod(sq, 6)
                mirrored = (5 - rank) * 6 + file
                score -= pst[mirrored]
                bb ^= lsb
        return score
