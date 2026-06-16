from bots.greedy_bot import GreedyBot
from bots.random_bot import RandomBot
from engine.board import BitBoard, Color, PieceType
from engine.movegen import generate_legal_moves
from engine.positions import make_starting_board


def test_random_bot_returns_legal_move():
    board = make_starting_board()
    bot = RandomBot("Rnd")
    move = bot.choose_move(board)
    legal = generate_legal_moves(board)
    assert move in legal


def test_greedy_bot_captures_over_non_capture():
    b = BitBoard()
    b.set_piece(3, Color.WHITE, PieceType.KING)
    b.set_piece(33, Color.BLACK, PieceType.KING)
    b.set_piece(6, Color.WHITE, PieceType.ROOK)   # a2
    b.set_piece(12, Color.BLACK, PieceType.QUEEN)  # a3 — capturable
    bot = GreedyBot("Greed")
    move = bot.choose_move(b)
    assert move.to_sq == 12
    assert move.captured == PieceType.QUEEN


def test_greedy_bot_prefers_higher_value_capture():
    b = BitBoard()
    b.set_piece(3, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)
    b.set_piece(14, Color.WHITE, PieceType.QUEEN)  # c3
    b.set_piece(13, Color.BLACK, PieceType.PAWN)   # b3 value=1
    b.set_piece(15, Color.BLACK, PieceType.ROOK)   # d3 value=5
    bot = GreedyBot("Greed")
    move = bot.choose_move(b)
    assert move.to_sq == 15  # captures rook, not pawn


def test_greedy_bot_plays_checkmate_over_capture():
    # White to move; there is a checkmate in 1 AND a capture available
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)    # a1
    b.set_piece(35, Color.BLACK, PieceType.KING)   # f6
    b.set_piece(5, Color.WHITE, PieceType.ROOK)    # f1
    b.set_piece(30, Color.WHITE, PieceType.QUEEN)  # a6 — Qa6# would be checkmate
    b.set_piece(31, Color.BLACK, PieceType.PAWN)   # b6 — capturable
    # Verify that Qa6# is indeed checkmate (queen covers b6 escape too after moving)
    # The greedy bot should find and play checkmate
    bot = GreedyBot("Greed")
    move = bot.choose_move(b)
    from engine.gamestate import GameResult, get_game_outcome, play_move
    b_copy = b.copy()
    play_move(b_copy, move)
    outcome = get_game_outcome(b_copy)
    assert outcome is not None and outcome.result == GameResult.WHITE_WINS


def test_greedy_bot_promotion_scored():
    b = BitBoard()
    b.set_piece(3, Color.WHITE, PieceType.KING)
    b.set_piece(33, Color.BLACK, PieceType.KING)
    b.set_piece(28, Color.WHITE, PieceType.PAWN)  # e5 — one step from promotion
    bot = GreedyBot("Greed")
    move = bot.choose_move(b)
    assert move.promotion == PieceType.QUEEN  # always promotes to Queen
