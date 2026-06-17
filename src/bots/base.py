from __future__ import annotations

from abc import ABC, abstractmethod

from bots.progress import BotProgress
from engine.board import BitBoard
from engine.move import Move


class Bot(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def choose_move(
        self,
        board: BitBoard,
        time_budget_seconds: float | None = None,
        progress: BotProgress | None = None,
    ) -> Move: ...
