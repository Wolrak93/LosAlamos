from engine.board import PIECE_VALUES, BitBoard, Color, PieceType
from engine.move import Move


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


def test_move_apply_simple():
    board = BitBoard()
    board.set_piece(6, Color.WHITE, PieceType.PAWN)  # a2
    move = Move(from_sq=6, to_sq=12, piece=PieceType.PAWN, color=Color.WHITE)
    move.apply(board)
    assert board.get_piece_at(6) is None
    assert board.get_piece_at(12) == (Color.WHITE, PieceType.PAWN)
    assert board.side_to_move == Color.BLACK


def test_move_apply_capture():
    board = BitBoard()
    board.set_piece(6, Color.WHITE, PieceType.PAWN)
    board.set_piece(13, Color.BLACK, PieceType.PAWN)
    move = Move(from_sq=6, to_sq=13, piece=PieceType.PAWN, color=Color.WHITE,
                captured=PieceType.PAWN)
    move.apply(board)
    assert board.get_piece_at(6) is None
    assert board.get_piece_at(13) == (Color.WHITE, PieceType.PAWN)
    assert board.get_piece_at(13) != (Color.BLACK, PieceType.PAWN)


def test_move_apply_promotion():
    board = BitBoard()
    board.set_piece(28, Color.WHITE, PieceType.PAWN)  # e5 — one step from rank 5
    move = Move(from_sq=28, to_sq=34, piece=PieceType.PAWN, color=Color.WHITE,
                promotion=PieceType.QUEEN)
    move.apply(board)
    assert board.get_piece_at(28) is None
    assert board.get_piece_at(34) == (Color.WHITE, PieceType.QUEEN)


def test_move_apply_resets_halfmove_on_pawn():
    board = BitBoard()
    board.halfmove_clock = 10
    board.set_piece(6, Color.WHITE, PieceType.PAWN)
    move = Move(from_sq=6, to_sq=12, piece=PieceType.PAWN, color=Color.WHITE)
    move.apply(board)
    assert board.halfmove_clock == 0


def test_move_apply_increments_halfmove_on_piece():
    board = BitBoard()
    board.halfmove_clock = 5
    board.set_piece(1, Color.WHITE, PieceType.KNIGHT)
    move = Move(from_sq=1, to_sq=14, piece=PieceType.KNIGHT, color=Color.WHITE)
    move.apply(board)
    assert board.halfmove_clock == 6


def test_sq_name():
    assert Move.sq_name(0) == "a1"
    assert Move.sq_name(5) == "f1"
    assert Move.sq_name(6) == "a2"
    assert Move.sq_name(35) == "f6"


def test_to_pgn_pawn_move():
    m = Move(from_sq=6, to_sq=12, piece=PieceType.PAWN, color=Color.WHITE)
    assert m.to_pgn() == "a3"


def test_to_pgn_pawn_capture():
    m = Move(from_sq=6, to_sq=13, piece=PieceType.PAWN, color=Color.WHITE,
             captured=PieceType.PAWN)
    assert m.to_pgn() == "axb3"


def test_to_pgn_promotion():
    m = Move(from_sq=28, to_sq=34, piece=PieceType.PAWN, color=Color.WHITE,
             promotion=PieceType.QUEEN)
    assert m.to_pgn() == "e6=Q"


def test_to_pgn_piece_move():
    m = Move(from_sq=1, to_sq=14, piece=PieceType.KNIGHT, color=Color.WHITE)
    assert m.to_pgn() == "Nc3"


def test_to_pgn_piece_capture():
    m = Move(from_sq=1, to_sq=14, piece=PieceType.KNIGHT, color=Color.WHITE,
             captured=PieceType.PAWN)
    assert m.to_pgn() == "Nxc3"
