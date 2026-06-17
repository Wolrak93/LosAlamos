from bots.evaluator import Evaluator
from engine.board import BitBoard, Color, PieceType


def _empty_board() -> BitBoard:
    b = BitBoard()
    b.set_piece(0, Color.WHITE, PieceType.KING)
    b.set_piece(35, Color.BLACK, PieceType.KING)
    return b


def test_material_equal_position_scores_zero():
    b = _empty_board()
    ev = Evaluator(material=True)
    assert ev.evaluate(b) == 0


def test_material_white_extra_queen():
    b = _empty_board()
    b.set_piece(10, Color.WHITE, PieceType.QUEEN)
    ev = Evaluator(material=True)
    assert ev.evaluate(b) == 900


def test_material_black_extra_rook():
    b = _empty_board()
    b.set_piece(10, Color.BLACK, PieceType.ROOK)
    ev = Evaluator(material=True)
    assert ev.evaluate(b) == -500


def test_material_symmetric_position_scores_zero():
    b = _empty_board()
    b.set_piece(12, Color.WHITE, PieceType.ROOK)
    b.set_piece(23, Color.BLACK, PieceType.ROOK)
    ev = Evaluator(material=True)
    assert ev.evaluate(b) == 0


def test_positional_knight_center_beats_edge():
    b = _empty_board()
    ev_center = Evaluator(material=True, positional=True)
    ev_edge = Evaluator(material=True, positional=True)

    # Center knight (c3 = square 14)
    b_center = b.copy()
    b_center.set_piece(14, Color.WHITE, PieceType.KNIGHT)
    score_center = ev_center.evaluate(b_center)

    # Edge knight (a2 = square 6)
    b_edge = b.copy()
    b_edge.set_piece(6, Color.WHITE, PieceType.KNIGHT)
    score_edge = ev_edge.evaluate(b_edge)

    assert score_center > score_edge


def test_positional_symmetric_scores_zero():
    b = _empty_board()
    b.set_piece(14, Color.WHITE, PieceType.KNIGHT)  # c3
    b.set_piece(20, Color.BLACK, PieceType.KNIGHT)  # c4 (mirror of c3)
    ev = Evaluator(material=True, positional=True)
    assert ev.evaluate(b) == 0
