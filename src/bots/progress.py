from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BotProgress:
    depth: int | None = None    # Minimax: completed search depth
    eval: float | None = None   # pawn units, positive = White advantage
    sims: int | None = None     # MCTS: total simulations completed
