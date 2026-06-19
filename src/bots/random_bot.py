from __future__ import annotations

import random

from bots.base import Bot
from bots.progress import BotProgress
from engine.board import BitBoard
from engine.move import Move
from engine.movegen import generate_legal_moves


class RandomBot(Bot):
    def choose_move(
        self,
        board: BitBoard,
        time_budget_seconds: float | None = None,
        progress: BotProgress | None = None,
    ) -> Move:
        return random.choice(generate_legal_moves(board))
