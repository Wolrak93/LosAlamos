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


def test_minimax_sets_mate_in_when_checkmate_found():
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)
    b.set_piece(5, Color.WHITE, PieceType.ROOK)
    b.set_piece(24, Color.WHITE, PieceType.QUEEN)
    from bots.progress import BotProgress
    bot = _make_minimax()
    p = BotProgress()
    bot.choose_move(b, time_budget_seconds=5.0, progress=p)
    assert p.mate_in is not None
    assert p.mate_in > 0  # White wins


def test_minimax_exits_early_on_forced_mate():
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)
    b.set_piece(5, Color.WHITE, PieceType.ROOK)
    b.set_piece(24, Color.WHITE, PieceType.QUEEN)
    from bots.progress import BotProgress
    bot = _make_minimax()
    p = BotProgress()
    start = time.monotonic()
    bot.choose_move(b, time_budget_seconds=60.0, progress=p)
    elapsed = time.monotonic() - start
    assert elapsed < 5.0
    assert p.mate_in is not None


def test_minimax_tiny_budget_no_crash():
    """Even with 1ms budget, bot returns a legal move without crashing."""
    from engine.positions import make_starting_board
    board = make_starting_board()
    bot = _make_minimax()
    move = bot.choose_move(board, time_budget_seconds=0.001)
    assert move in generate_legal_moves(board)


def test_minimax_single_legal_move():
    """Bot returns the only legal move when exactly one exists."""
    # WK a1 in check from BR a3; BQ c3 covers b2; only escape is Kb1.
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)    # a1
    b.set_piece(12, Color.BLACK, PieceType.ROOK)   # a3 — gives check
    b.set_piece(14, Color.BLACK, PieceType.QUEEN)  # c3 — covers b2 diagonally
    b.set_piece(35, Color.BLACK, PieceType.KING)   # f6
    bot = _make_minimax()
    legal = generate_legal_moves(b)
    assert len(legal) == 1, f"Expected 1 legal move, got {len(legal)}"
    move = bot.choose_move(b, time_budget_seconds=1.0)
    assert move in legal


def test_minimax_captures_hanging_queen():
    """Bot takes a completely undefended enemy queen for free."""
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)    # a1
    b.set_piece(12, Color.WHITE, PieceType.ROOK)   # a3
    b.set_piece(24, Color.BLACK, PieceType.QUEEN)  # a5 — hanging
    b.set_piece(35, Color.BLACK, PieceType.KING)   # f6
    bot = _make_minimax()
    move = bot.choose_move(b, time_budget_seconds=1.0)
    assert move.to_sq == 24
    assert move.captured == PieceType.QUEEN
