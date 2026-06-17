# tests/test_mcts.py
import time

from bots.evaluator import Evaluator
from bots.mcts_bot import MCTSBot
from engine.board import BitBoard, Color, PieceType
from engine.gamestate import GameResult, get_game_outcome, play_move
from engine.movegen import generate_legal_moves
from engine.positions import make_starting_board


def _make_mcts(positional=False, mobility=False) -> MCTSBot:
    return MCTSBot(Evaluator(material=True, positional=positional, mobility=mobility), "Test")


def test_mcts_returns_legal_move():
    board = make_starting_board()
    bot = _make_mcts()
    move = bot.choose_move(board, time_budget_seconds=1.0)
    assert move in generate_legal_moves(board)


def test_mcts_finds_checkmate_in_1():
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)   # f6
    b.set_piece(5, Color.WHITE, PieceType.ROOK)    # f1
    b.set_piece(24, Color.WHITE, PieceType.QUEEN)  # a5 — Qa6# wins
    bot = _make_mcts()
    move = bot.choose_move(b, time_budget_seconds=5.0)
    copy = b.copy()
    play_move(copy, move)
    outcome = get_game_outcome(copy)
    assert outcome is not None and outcome.result == GameResult.WHITE_WINS


def test_mcts_respects_time_budget():
    board = make_starting_board()
    bot = _make_mcts()
    start = time.monotonic()
    bot.choose_move(board, time_budget_seconds=1.0)
    elapsed = time.monotonic() - start
    assert elapsed < 3.0


def test_mcts_writes_progress():
    from bots.progress import BotProgress
    board = make_starting_board()
    bot = _make_mcts()
    p = BotProgress()
    bot.choose_move(board, time_budget_seconds=1.0, progress=p)
    # 1 second is enough for >100 simulations
    assert p.sims is not None
    assert p.sims >= 100
    assert p.eval is not None
    assert isinstance(p.eval, float)
