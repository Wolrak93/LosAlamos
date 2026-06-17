from __future__ import annotations

import random

from bots.base import Bot
from engine.board import BitBoard
from engine.move import Move
from engine.movegen import generate_legal_moves


class RandomBot(Bot):
    def choose_move(self, board: BitBoard) -> Move:
        return random.choice(generate_legal_moves(board))
