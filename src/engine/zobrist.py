from __future__ import annotations

import random

from engine.board import BitBoard, Color

_rng = random.Random(0xABCDEF42)
_PIECE_TABLE: list[list[list[int]]] = [
    [[_rng.getrandbits(64) for _ in range(36)] for _ in range(5)]
    for _ in range(2)
]
_SIDE_KEY: int = _rng.getrandbits(64)


def compute_hash(board: BitBoard) -> int:
    h = 0
    for color in range(2):
        for pt in range(5):
            bb = board.pieces[color][pt]
            while bb:
                lsb = bb & -bb
                sq = lsb.bit_length() - 1
                h ^= _PIECE_TABLE[color][pt][sq]
                bb ^= lsb
    if board.side_to_move == Color.BLACK:
        h ^= _SIDE_KEY
    return h
