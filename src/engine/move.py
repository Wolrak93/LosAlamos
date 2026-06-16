from __future__ import annotations
from dataclasses import dataclass
from engine.board import BitBoard, Color, PieceType

_FILE_NAMES = "abcdef"
_PIECE_CHARS = {
    PieceType.KNIGHT: "N",
    PieceType.ROOK: "R",
    PieceType.QUEEN: "Q",
    PieceType.KING: "K",
}
_PROMO_CHARS = {
    PieceType.QUEEN: "Q",
    PieceType.ROOK: "R",
    PieceType.KNIGHT: "N",
}


@dataclass
class Move:
    from_sq: int
    to_sq: int
    piece: PieceType
    color: Color
    captured: PieceType | None = None
    promotion: PieceType | None = None

    def apply(self, board: BitBoard) -> None:
        opp = Color(1 - int(self.color))
        board.remove_piece(self.from_sq, self.color, self.piece)
        if self.captured is not None:
            board.remove_piece(self.to_sq, opp, self.captured)
        dest_piece = self.promotion if self.promotion is not None else self.piece
        board.set_piece(self.to_sq, self.color, dest_piece)
        if self.piece == PieceType.PAWN or self.captured is not None:
            board.halfmove_clock = 0
        else:
            board.halfmove_clock += 1
        board.side_to_move = Color(1 - int(board.side_to_move))
        board.ply += 1

    @staticmethod
    def sq_name(sq: int) -> str:
        return f"{_FILE_NAMES[sq % 6]}{sq // 6 + 1}"

    def to_pgn(self) -> str:
        to_file = self.to_sq % 6
        to_rank = self.to_sq // 6 + 1
        dest = f"{_FILE_NAMES[to_file]}{to_rank}"
        if self.piece == PieceType.PAWN:
            if self.captured is not None:
                base = f"{_FILE_NAMES[self.from_sq % 6]}x{dest}"
            else:
                base = dest
            if self.promotion is not None:
                return f"{base}={_PROMO_CHARS[self.promotion]}"
            return base
        pc = _PIECE_CHARS[self.piece]
        x = "x" if self.captured is not None else ""
        return f"{pc}{x}{dest}"
