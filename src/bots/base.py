from __future__ import annotations

from abc import ABC, abstractmethod

from engine.board import BitBoard
from engine.move import Move


class Bot(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def choose_move(self, board: BitBoard) -> Move: ...
