from collections import Counter

from engine.board import PIECE_VALUES, BitBoard, Color, PieceType
from engine.move import Move
from engine.positions import make_starting_board
from engine.zobrist import compute_hash


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


def test_hash_empty_board():
    board = BitBoard()
    h = compute_hash(board)
    assert isinstance(h, int)


def test_hash_differs_by_piece():
    b1 = BitBoard()
    b1.set_piece(0, Color.WHITE, PieceType.KING)
    b2 = BitBoard()
    b2.set_piece(1, Color.WHITE, PieceType.KING)
    assert compute_hash(b1) != compute_hash(b2)


def test_hash_differs_by_side():
    b1 = BitBoard()
    b1.set_piece(3, Color.WHITE, PieceType.KING)
    b1.side_to_move = Color.WHITE
    b2 = b1.copy()
    b2.side_to_move = Color.BLACK
    assert compute_hash(b1) != compute_hash(b2)


def test_hash_same_position_same_hash():
    b1 = BitBoard()
    b1.set_piece(3, Color.WHITE, PieceType.KING)
    b2 = BitBoard()
    b2.set_piece(3, Color.WHITE, PieceType.KING)
    assert compute_hash(b1) == compute_hash(b2)


def test_normal_starting_position():
    b = make_starting_board("normal")
    # White back rank: R-N-Q-K-N-R at squares 0-5
    assert b.get_piece_at(0) == (Color.WHITE, PieceType.ROOK)
    assert b.get_piece_at(1) == (Color.WHITE, PieceType.KNIGHT)
    assert b.get_piece_at(2) == (Color.WHITE, PieceType.QUEEN)
    assert b.get_piece_at(3) == (Color.WHITE, PieceType.KING)
    assert b.get_piece_at(4) == (Color.WHITE, PieceType.KNIGHT)
    assert b.get_piece_at(5) == (Color.WHITE, PieceType.ROOK)
    # White pawns on rank 1 (squares 6-11)
    for sq in range(6, 12):
        assert b.get_piece_at(sq) == (Color.WHITE, PieceType.PAWN)
    # Black back rank rank 5 (squares 30-35)
    assert b.get_piece_at(30) == (Color.BLACK, PieceType.ROOK)
    assert b.get_piece_at(33) == (Color.BLACK, PieceType.KING)
    # Black pawns on rank 4 (squares 24-29)
    for sq in range(24, 30):
        assert b.get_piece_at(sq) == (Color.BLACK, PieceType.PAWN)


def test_random_sym_same_back_ranks():
    b = make_starting_board("random_sym")
    white_back = [b.get_piece_at(sq)[1] for sq in range(6)]
    black_back = [b.get_piece_at(sq)[1] for sq in range(30, 36)]
    assert white_back == black_back


def test_random_asym_piece_counts():
    b = make_starting_board("random_asym")
    # Each side must still have exactly 1K, 1Q, 2R, 2N
    white_back = Counter(b.get_piece_at(sq)[1] for sq in range(6))
    assert white_back[PieceType.KING] == 1
    assert white_back[PieceType.QUEEN] == 1
    assert white_back[PieceType.ROOK] == 2
    assert white_back[PieceType.KNIGHT] == 2
