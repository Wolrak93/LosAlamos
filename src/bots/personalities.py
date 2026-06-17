# src/bots/personalities.py
from __future__ import annotations

from bots.evaluator import Evaluator
from bots.mcts_bot import MCTSBot
from bots.minimax_bot import MinimaxBot


def calculate_time_budget(
    remaining_seconds: float | None,
    move_number: int,
    increment_seconds: float = 0.0,
) -> float:
    """Compute how many seconds a bot should spend on this move."""
    if remaining_seconds is None:
        return 120.0
    if move_number <= 30:
        early_moves_left = max(1, 30 - move_number + 1)
        budget = remaining_seconds * 0.80 / early_moves_left
    else:
        budget = remaining_seconds * 0.10
    return budget + increment_seconds


def create_fermi(name: str = "Fermi") -> MinimaxBot:
    return MinimaxBot(Evaluator(material=True), name)


def create_von_neumann(name: str = "von Neumann") -> MinimaxBot:
    return MinimaxBot(Evaluator(material=True, positional=True), name)


def create_oppenheimer(name: str = "Oppenheimer") -> MinimaxBot:
    return MinimaxBot(Evaluator(material=True, positional=True, mobility=True), name)


def create_feynman(name: str = "Feynman") -> MCTSBot:
    return MCTSBot(Evaluator(material=True), name)


def create_teller(name: str = "Teller") -> MCTSBot:
    return MCTSBot(Evaluator(material=True, positional=True), name)


def create_bethe(name: str = "Bethe") -> MCTSBot:
    return MCTSBot(Evaluator(material=True, positional=True, mobility=True), name)


ALL_SCIENTISTS: list[tuple[str, callable]] = [
    ("Fermi",       create_fermi),
    ("von Neumann", create_von_neumann),
    ("Oppenheimer", create_oppenheimer),
    ("Feynman",     create_feynman),
    ("Teller",      create_teller),
    ("Bethe",       create_bethe),
]
