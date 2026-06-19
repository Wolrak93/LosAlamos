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


def test_mobility_more_moves_scores_higher():
    # White queen in center has many moves; black has only king
    b = _empty_board()
    b.set_piece(21, Color.WHITE, PieceType.QUEEN)   # d4 — many moves
    ev = Evaluator(material=True, mobility=True)
    score_with_queen = ev.evaluate(b)

    b2 = _empty_board()
    ev2 = Evaluator(material=True, mobility=True)
    score_kings_only = ev2.evaluate(b2)

    assert score_with_queen > score_kings_only


def test_mobility_additivity():
    b = _empty_board()
    b.set_piece(14, Color.WHITE, PieceType.KNIGHT)
    ev_mat = Evaluator(material=True)
    ev_pos = Evaluator(material=True, positional=True)
    ev_mob = Evaluator(material=True, mobility=True)
    ev_all = Evaluator(material=True, positional=True, mobility=True)
    expected = (
        ev_mat.evaluate(b)
        + (ev_pos.evaluate(b) - ev_mat.evaluate(b))
        + (ev_mob.evaluate(b) - ev_mat.evaluate(b))
    )
    assert ev_all.evaluate(b) == expected


def test_material_white_extra_pawn():
    b = _empty_board()
    b.set_piece(10, Color.WHITE, PieceType.PAWN)
    ev = Evaluator(material=True)
    assert ev.evaluate(b) == 100


def test_material_white_extra_knight():
    b = _empty_board()
    b.set_piece(10, Color.WHITE, PieceType.KNIGHT)
    ev = Evaluator(material=True)
    assert ev.evaluate(b) == 300


def test_positional_pawn_rank4_beats_rank1():
    """Pawn on rank 4 (advanced) scores higher than pawn on rank 1 (starting)."""
    b_advanced = _empty_board()
    b_advanced.set_piece(24, Color.WHITE, PieceType.PAWN)  # a5 — rank 4
    b_start = _empty_board()
    b_start.set_piece(6, Color.WHITE, PieceType.PAWN)      # a2 — rank 1
    ev = Evaluator(material=True, positional=True)
    assert ev.evaluate(b_advanced) > ev.evaluate(b_start)


def test_positional_endgame_pst_active_with_few_pieces():
    """With ≤6 pieces, endgame king PST is used: center king beats corner king."""
    b_center = BitBoard()
    b_center.set_piece(14, Color.WHITE, PieceType.KING)  # c3 — center
    b_center.set_piece(35, Color.BLACK, PieceType.KING)  # f6
    b_corner = BitBoard()
    b_corner.set_piece(0, Color.WHITE, PieceType.KING)   # a1 — corner
    b_corner.set_piece(35, Color.BLACK, PieceType.KING)  # f6
    ev = Evaluator(positional=True)
    assert ev.evaluate(b_center) > ev.evaluate(b_corner)


def test_mobility_symmetric_start_scores_zero():
    """Symmetric starting position has equal mobility for both sides."""
    from engine.positions import make_starting_board
    b = make_starting_board()
    ev = Evaluator(mobility=True)
    assert ev.evaluate(b) == 0
