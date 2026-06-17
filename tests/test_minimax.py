# tests/test_minimax.py
import time

from bots.evaluator import Evaluator
from bots.minimax_bot import MinimaxBot
from engine.board import BitBoard, Color, PieceType
from engine.gamestate import GameResult, get_game_outcome, play_move
from engine.movegen import generate_legal_moves


def _make_minimax(positional=False, mobility=False) -> MinimaxBot:
    return MinimaxBot(Evaluator(material=True, positional=positional, mobility=mobility), "Test")


def test_minimax_returns_legal_move():
    from engine.positions import make_starting_board
    board = make_starting_board()
    bot = _make_minimax()
    move = bot.choose_move(board, time_budget_seconds=1.0)
    assert move in generate_legal_moves(board)


def test_minimax_finds_checkmate_in_1():
    b2 = BitBoard()
    b2.set_piece(0, Color.WHITE, PieceType.KING)
    b2.set_piece(35, Color.BLACK, PieceType.KING)  # f6
    b2.set_piece(5, Color.WHITE, PieceType.ROOK)   # f1
    b2.set_piece(24, Color.WHITE, PieceType.QUEEN) # a5 — Qa6# wins
    bot = _make_minimax()
    move = bot.choose_move(b2, time_budget_seconds=5.0)
    copy = b2.copy()
    play_move(copy, move)
    outcome = get_game_outcome(copy)
    assert outcome is not None and outcome.result == GameResult.WHITE_WINS


def test_minimax_respects_time_budget():
    from engine.positions import make_starting_board
    board = make_starting_board()
    bot = _make_minimax()
    start = time.monotonic()
    bot.choose_move(board, time_budget_seconds=1.0)
    elapsed = time.monotonic() - start
    assert elapsed < 3.0  # generous margin for slow CI


def test_minimax_writes_progress():
    from bots.progress import BotProgress
    from engine.positions import make_starting_board
    board = make_starting_board()
    bot = _make_minimax()
    p = BotProgress()
    bot.choose_move(board, time_budget_seconds=1.0, progress=p)
    assert p.depth is not None
    assert p.depth >= 1
    assert p.eval is not None
    assert isinstance(p.eval, float)
