from engine.board import BitBoard, Color, PieceType
from engine.movegen import generate_legal_moves, is_square_attacked


def _place(board, color, pt, sq):
    board.set_piece(sq, color, pt)


def _kings_only(white_sq, black_sq):
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, white_sq)
    _place(b, Color.BLACK, PieceType.KING, black_sq)
    return b


# --- Pawn tests ---

def test_pawn_single_step_white():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.PAWN, 6)  # a2
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.PAWN]
    dests = {m.to_sq for m in moves}
    assert 12 in dests  # a3


def test_pawn_blocked():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.PAWN, 6)
    _place(b, Color.BLACK, PieceType.PAWN, 12)  # blocker on a3
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.PAWN]
    dests = {m.to_sq for m in moves}
    assert 12 not in dests


def test_pawn_diagonal_capture():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.PAWN, 6)   # a2
    _place(b, Color.BLACK, PieceType.PAWN, 13)  # b3 — capturable
    moves = [m for m in generate_legal_moves(b)
             if m.piece == PieceType.PAWN and m.captured is not None]
    dests = {m.to_sq for m in moves}
    assert 13 in dests


def test_pawn_no_capture_forward():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.PAWN, 6)
    _place(b, Color.BLACK, PieceType.PAWN, 13)
    moves = [m for m in generate_legal_moves(b)
             if m.piece == PieceType.PAWN and m.to_sq == 13]
    captures = [m for m in moves if m.captured is not None]
    non_captures = [m for m in moves if m.captured is None]
    assert len(captures) == 1
    assert len(non_captures) == 0  # can't step diagonally without capturing


def test_pawn_promotion_generates_three_moves():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.PAWN, 28)  # e5 — one step from rank 5
    promos = [m for m in generate_legal_moves(b)
              if m.piece == PieceType.PAWN and m.promotion is not None]
    assert len(promos) == 3
    promo_types = {m.promotion for m in promos}
    assert promo_types == {PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT}


# --- Knight tests ---

def test_knight_moves_from_center():
    b = _kings_only(0, 35)
    _place(b, Color.WHITE, PieceType.KNIGHT, 14)  # c3
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.KNIGHT]
    dests = {m.to_sq for m in moves}
    # From c3 (sq 14 = rank2, file2):
    # rank+2,file+1 = rank4,file3 = sq27 (d5) ✓
    # rank+2,file-1 = rank4,file1 = sq25 (b5) ✓
    # rank+1,file+2 = rank3,file4 = sq22 (e4) ✓
    # rank+1,file-2 = rank3,file0 = sq18 (a4) ✓
    # rank-1,file+2 = rank1,file4 = sq10 (e2) ✓
    # rank-1,file-2 = rank1,file0 = sq6 (a2) ✓
    # rank-2,file+1 = rank0,file3 = sq3 (d1) — but king is there! so not in legal
    # rank-2,file-1 = rank0,file1 = sq1 (b1) ✓
    assert {25, 27, 22, 18, 10, 6, 1}.issubset(dests)


def test_knight_cannot_move_off_board():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.KNIGHT, 0)  # a1 corner
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.KNIGHT]
    dests = {m.to_sq for m in moves}
    for sq in dests:
        assert 0 <= sq <= 35


# --- Rook tests ---

def test_rook_open_file():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.ROOK, 0)  # a1
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.ROOK]
    dests = {m.to_sq for m in moves}
    assert {6, 12, 18, 24, 30} <= dests   # up the a-file
    assert {1, 2} <= dests                 # along rank 0 (king at 3 blocks 3+)


def test_rook_blocked_by_own_piece():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.ROOK, 0)
    _place(b, Color.WHITE, PieceType.PAWN, 12)  # a3 — blocks upward
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.ROOK]
    dests = {m.to_sq for m in moves}
    assert 12 not in dests
    assert 18 not in dests


def test_rook_captures_opponent():
    b = _kings_only(3, 33)
    _place(b, Color.WHITE, PieceType.ROOK, 0)
    _place(b, Color.BLACK, PieceType.PAWN, 12)
    moves = [m for m in generate_legal_moves(b)
             if m.piece == PieceType.ROOK and m.to_sq == 12]
    assert len(moves) == 1
    assert moves[0].captured == PieceType.PAWN


# --- Queen tests ---

def test_queen_moves_orthogonally_and_diagonally():
    b = _kings_only(0, 35)
    _place(b, Color.WHITE, PieceType.QUEEN, 14)  # c3
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.QUEEN]
    dests = {m.to_sq for m in moves}
    assert 20 in dests   # d4 diagonal
    assert 8 in dests    # b2 diagonal
    assert 15 in dests   # d3 horizontal
    assert 13 in dests   # b3 horizontal
    assert 20 in dests   # d4 (up-right diagonal)


# --- King tests ---

def test_king_moves_one_step():
    b = _kings_only(14, 35)  # c3 vs f6
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.KING]
    dests = {m.to_sq for m in moves}
    assert {7, 8, 9, 13, 15, 19, 20, 21}.issubset(dests)


def test_king_cannot_move_into_check():
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 3)   # d1
    _place(b, Color.BLACK, PieceType.KING, 15)  # d3 — defends rook on d2
    _place(b, Color.BLACK, PieceType.ROOK, 9)   # d2 — controls d-file
    moves = [m for m in generate_legal_moves(b) if m.piece == PieceType.KING]
    dests = {m.to_sq for m in moves}
    assert 9 not in dests   # can't capture defended rook
    assert 3 not in dests   # can't stay


# --- Check detection ---

def test_is_square_attacked():
    b = BitBoard()
    _place(b, Color.BLACK, PieceType.ROOK, 3)   # d1
    # d-file squares are attacked by the rook
    assert is_square_attacked(b, 9, Color.BLACK)   # d2 attacked
    assert not is_square_attacked(b, 10, Color.BLACK)  # e2 not attacked


# --- Checkmate ---

def test_no_legal_moves_in_checkmate():
    # Simple back-rank mate: White king at a1, Black queen at a6+rook at b6
    b = BitBoard()
    _place(b, Color.WHITE, PieceType.KING, 0)   # a1
    _place(b, Color.BLACK, PieceType.KING, 35)  # f6
    _place(b, Color.BLACK, PieceType.QUEEN, 30) # a6 — checks king via a-file
    _place(b, Color.BLACK, PieceType.ROOK, 31)  # b6 — cuts off b1 and b2
    moves = generate_legal_moves(b)
    assert moves == []
