import pytest
from engine.board import BitBoard, Color, PieceType, PIECE_VALUES


def test_piece_values():
    assert PIECE_VALUES[PieceType.PAWN] == 1
    assert PIECE_VALUES[PieceType.KNIGHT] == 3
    assert PIECE_VALUES[PieceType.ROOK] == 5
    assert PIECE_VALUES[PieceType.QUEEN] == 9


def test_empty_board_has_no_pieces():
    board = BitBoard()
    for sq in range(36):
        assert board.get_piece_at(sq) is None


def test_set_and_get_piece():
    board = BitBoard()
    board.set_piece(0, Color.WHITE, PieceType.ROOK)
    assert board.get_piece_at(0) == (Color.WHITE, PieceType.ROOK)
    assert board.get_piece_at(1) is None


def test_remove_piece():
    board = BitBoard()
    board.set_piece(5, Color.BLACK, PieceType.QUEEN)
    board.remove_piece(5, Color.BLACK, PieceType.QUEEN)
    assert board.get_piece_at(5) is None


def test_occupancy_single_color():
    board = BitBoard()
    board.set_piece(0, Color.WHITE, PieceType.ROOK)
    board.set_piece(3, Color.WHITE, PieceType.KING)
    occ = board.occupancy(Color.WHITE)
    assert occ == (1 << 0) | (1 << 3)


def test_full_occupancy():
    board = BitBoard()
    board.set_piece(0, Color.WHITE, PieceType.KING)
    board.set_piece(35, Color.BLACK, PieceType.KING)
    assert board.occupancy() == (1 << 0) | (1 << 35)


def test_copy_is_independent():
    board = BitBoard()
    board.set_piece(0, Color.WHITE, PieceType.KING)
    copy = board.copy()
    copy.set_piece(1, Color.WHITE, PieceType.ROOK)
    assert board.get_piece_at(1) is None  # original unchanged


def test_initial_side_to_move():
    board = BitBoard()
    assert board.side_to_move == Color.WHITE
