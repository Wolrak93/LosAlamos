from engine.board import BitBoard, Color, PieceType
from engine.gamestate import (
    GameResult,
    get_game_outcome,
    has_insufficient_material,
    is_in_check,
    play_move,
)
from engine.move import Move


def _place(board, color, pt, sq):
    board.set_piece(sq, color, pt)


def test_is_in_check_false_when_safe():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.BLACK, PieceType.KING, 33)
    assert not is_in_check(b)


def test_is_in_check_true_when_attacked():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)   # d1
    _place(b, Color.BLACK, PieceType.KING, 33)
    _place(b, Color.BLACK, PieceType.ROOK, 9)   # d2 attacks d1
    assert is_in_check(b)


def test_checkmate_returns_loss():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 0)   # a1
    _place(b, Color.BLACK, PieceType.KING, 35)
    _place(b, Color.BLACK, PieceType.QUEEN, 30) # a6
    _place(b, Color.BLACK, PieceType.ROOK, 31)  # b6
    outcome = get_game_outcome(b)
    assert outcome is not None
    assert outcome.result == GameResult.BLACK_WINS
    assert outcome.reason == "Schachmatt"


def test_stalemate_returns_draw():
    # White king at a1 (sq 0), Black queen at c2 (sq 8) covers b1,a2,b2 — not a1
    # King has no legal moves and is not in check = stalemate
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 0)   # a1
    _place(b, Color.BLACK, PieceType.KING, 35)  # f6
    _place(b, Color.BLACK, PieceType.QUEEN, 8)  # c2 — covers b1, a2, b2, not a1
    outcome = get_game_outcome(b)
    assert outcome is not None
    assert outcome.result == GameResult.DRAW
    assert outcome.reason == "Patt"


def test_fifty_move_rule():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.BLACK, PieceType.KING, 33)
    b.halfmove_clock = 100
    outcome = get_game_outcome(b)
    assert outcome is not None
    assert outcome.result == GameResult.DRAW
    assert outcome.reason == "50-Züge-Regel"


def test_threefold_repetition():
    from engine.zobrist import compute_hash
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.BLACK, PieceType.KING, 33)
    h = compute_hash(b)

    # 2 occurrences in history → not a threefold repetition draw (need 3)
    b.position_history = [h, h]
    outcome_two = get_game_outcome(b)
    assert outcome_two is None or outcome_two.reason != "Dreifache Stellungswiederholung"

    # 3 occurrences in history → draw
    b.position_history = [h, h, h]
    outcome_three = get_game_outcome(b)
    assert outcome_three is not None
    assert outcome_three.result == GameResult.DRAW
    assert outcome_three.reason == "Dreifache Stellungswiederholung"


def test_insufficient_material_lone_kings():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.BLACK, PieceType.KING, 33)
    assert has_insufficient_material(b)


def test_insufficient_material_king_and_knight():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.WHITE, PieceType.KNIGHT, 1)
    _place(b, Color.BLACK, PieceType.KING, 33)
    assert has_insufficient_material(b)


def test_sufficient_material_with_rook():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.WHITE, PieceType.ROOK, 0)
    _place(b, Color.BLACK, PieceType.KING, 33)
    assert not has_insufficient_material(b)


def test_play_move_updates_history():
    from engine.zobrist import compute_hash
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)
    _place(b, Color.BLACK, PieceType.KING, 33)
    _place(b, Color.WHITE, PieceType.PAWN, 6)
    move = Move(6, 12, PieceType.PAWN, Color.WHITE)
    play_move(b, move)
    assert len(b.position_history) == 1
    assert b.position_history[0] == compute_hash(b)
