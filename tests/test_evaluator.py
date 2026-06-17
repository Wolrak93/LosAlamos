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
