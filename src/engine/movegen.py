from __future__ import annotations

from engine.board import BitBoard, Color, PieceType
from engine.move import Move

# --- Pre-computed attack tables ---

def _compute_knight_attacks() -> list[int]:
    table = [0] * 36
    offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for sq in range(36):
        rank, file = divmod(sq, 6)
        bb = 0
        for dr, df in offsets:
            r, f = rank + dr, file + df
            if 0 <= r < 6 and 0 <= f < 6:
                bb |= 1 << (r * 6 + f)
        table[sq] = bb
    return table


def _compute_king_attacks() -> list[int]:
    table = [0] * 36
    for sq in range(36):
        rank, file = divmod(sq, 6)
        bb = 0
        for dr in (-1, 0, 1):
            for df in (-1, 0, 1):
                if dr == 0 and df == 0:
                    continue
                r, f = rank + dr, file + df
                if 0 <= r < 6 and 0 <= f < 6:
                    bb |= 1 << (r * 6 + f)
        table[sq] = bb
    return table


KNIGHT_ATTACKS: list[int] = _compute_knight_attacks()
KING_ATTACKS: list[int] = _compute_king_attacks()

_ROOK_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
_QUEEN_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]


def _sliding_attacks(sq: int, occ: int, directions: list[tuple[int, int]]) -> int:
    attacks = 0
    rank, file = divmod(sq, 6)
    for dr, df in directions:
        r, f = rank + dr, file + df
        while 0 <= r < 6 and 0 <= f < 6:
            target = r * 6 + f
            attacks |= 1 << target
            if (occ >> target) & 1:
                break
            r, f = r + dr, f + df
    return attacks


# --- Attack detection ---

def is_square_attacked(board: BitBoard, sq: int, by_color: Color) -> bool:
    occ = board.occupancy()

    # Pawn attacks (attacking pawns move toward sq)
    rank, file = divmod(sq, 6)
    pawn_bb = board.pieces[by_color][PieceType.PAWN]
    if by_color == Color.WHITE:
        # White pawns attack upward, so they attack sq from below
        for df in (-1, 1):
            f = file + df
            r = rank - 1
            if 0 <= r < 6 and 0 <= f < 6:
                if pawn_bb & (1 << (r * 6 + f)):
                    return True
    else:
        for df in (-1, 1):
            f = file + df
            r = rank + 1
            if 0 <= r < 6 and 0 <= f < 6:
                if pawn_bb & (1 << (r * 6 + f)):
                    return True

    if KNIGHT_ATTACKS[sq] & board.pieces[by_color][PieceType.KNIGHT]:
        return True
    if KING_ATTACKS[sq] & board.pieces[by_color][PieceType.KING]:
        return True

    rook_attacks = _sliding_attacks(sq, occ, _ROOK_DIRS)
    if rook_attacks & board.pieces[by_color][PieceType.ROOK]:
        return True

    queen_attacks = _sliding_attacks(sq, occ, _QUEEN_DIRS)
    if queen_attacks & board.pieces[by_color][PieceType.QUEEN]:
        return True

    return False


# --- Pseudo-legal move generation ---

def _gen_pawn_moves(board: BitBoard, color: Color) -> list[Move]:
    moves = []
    pawns = board.pieces[color][PieceType.PAWN]
    occ = board.occupancy()
    opp = Color(1 - int(color))
    opp_occ = board.occupancy(opp)
    # Never capture the king — exclude its square from capturable squares
    opp_king_bb = board.pieces[opp][PieceType.KING]
    capturable = opp_occ & ~opp_king_bb
    direction = 1 if color == Color.WHITE else -1
    promo_rank = 5 if color == Color.WHITE else 0

    bb = pawns
    while bb:
        lsb = bb & -bb
        sq = lsb.bit_length() - 1
        bb ^= lsb
        rank, file = divmod(sq, 6)

        # Forward step
        target_rank = rank + direction
        if 0 <= target_rank < 6:
            target_sq = target_rank * 6 + file
            if not (occ & (1 << target_sq)):
                if target_rank == promo_rank:
                    for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT):
                        moves.append(Move(sq, target_sq, PieceType.PAWN, color, promotion=pt))
                else:
                    moves.append(Move(sq, target_sq, PieceType.PAWN, color))

        # Diagonal captures
        for df in (-1, 1):
            cap_file = file + df
            cap_rank = rank + direction
            if 0 <= cap_rank < 6 and 0 <= cap_file < 6:
                cap_sq = cap_rank * 6 + cap_file
                if capturable & (1 << cap_sq):
                    cap_piece = board.get_piece_at(cap_sq)
                    assert cap_piece is not None
                    captured_pt = cap_piece[1]
                    if cap_rank == promo_rank:
                        for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT):
                            moves.append(Move(sq, cap_sq, PieceType.PAWN, color,
                                              captured=captured_pt, promotion=pt))
                    else:
                        moves.append(Move(sq, cap_sq, PieceType.PAWN, color,
                                          captured=captured_pt))
    return moves


def _gen_piece_moves(
    board: BitBoard, color: Color, pt: PieceType, attack_bb_fn
) -> list[Move]:
    moves = []
    own_occ = board.occupancy(color)
    opp = Color(1 - int(color))
    opp_king_bb = board.pieces[opp][PieceType.KING]
    bb = board.pieces[color][pt]
    while bb:
        lsb = bb & -bb
        sq = lsb.bit_length() - 1
        bb ^= lsb
        attacks = attack_bb_fn(sq) & ~own_occ & ~opp_king_bb
        tgt = attacks
        while tgt:
            t_lsb = tgt & -tgt
            t_sq = t_lsb.bit_length() - 1
            tgt ^= t_lsb
            cap = board.get_piece_at(t_sq)
            moves.append(Move(sq, t_sq, pt, color,
                               captured=cap[1] if cap else None))
    return moves


def _gen_sliding_moves(board: BitBoard, color: Color, pt: PieceType,
                       directions: list[tuple[int, int]]) -> list[Move]:
    moves = []
    own_occ = board.occupancy(color)
    opp = Color(1 - int(color))
    opp_king_bb = board.pieces[opp][PieceType.KING]
    occ = board.occupancy()
    bb = board.pieces[color][pt]
    while bb:
        lsb = bb & -bb
        sq = lsb.bit_length() - 1
        bb ^= lsb
        attacks = _sliding_attacks(sq, occ, directions) & ~own_occ & ~opp_king_bb
        tgt = attacks
        while tgt:
            t_lsb = tgt & -tgt
            t_sq = t_lsb.bit_length() - 1
            tgt ^= t_lsb
            cap = board.get_piece_at(t_sq)
            moves.append(Move(sq, t_sq, pt, color,
                               captured=cap[1] if cap else None))
    return moves


def find_king_sq(board: BitBoard, color: Color) -> int:
    bb = board.pieces[color][PieceType.KING]
    return (bb & -bb).bit_length() - 1


def generate_pseudo_legal_moves(board: BitBoard) -> list[Move]:
    color = board.side_to_move
    moves = _gen_pawn_moves(board, color)
    moves += _gen_piece_moves(board, color, PieceType.KNIGHT,
                               lambda sq: KNIGHT_ATTACKS[sq])
    moves += _gen_piece_moves(board, color, PieceType.KING,
                               lambda sq: KING_ATTACKS[sq])
    moves += _gen_sliding_moves(board, color, PieceType.ROOK, _ROOK_DIRS)
    moves += _gen_sliding_moves(board, color, PieceType.QUEEN, _QUEEN_DIRS)
    return moves


def generate_legal_moves(board: BitBoard) -> list[Move]:
    opp = Color(1 - int(board.side_to_move))
    legal = []
    for move in generate_pseudo_legal_moves(board):
        copy = board.copy()
        move.apply(copy)
        king_sq = find_king_sq(copy, move.color)
        if not is_square_attacked(copy, king_sq, opp):
            legal.append(move)
    return legal
