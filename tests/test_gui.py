from bots.greedy_bot import GreedyBot
from bots.random_bot import RandomBot
from engine.board import BitBoard, Color, PieceType
from gui.game_screen import _is_evaluating_bot, _net_captured_count, _next_selection


def test_human_is_not_evaluating():
    assert _is_evaluating_bot(None) is False


def test_random_bot_is_not_evaluating():
    assert _is_evaluating_bot(RandomBot("r")) is False


def test_greedy_bot_is_evaluating():
    assert _is_evaluating_bot(GreedyBot("g")) is True


def _board_with(white_pawns: int, black_pawns: int) -> BitBoard:
    """Minimal board with only pawns set for the two sides."""
    board = BitBoard()
    for i in range(white_pawns):
        board.set_piece(i, Color.WHITE, PieceType.PAWN)
    for i in range(black_pawns):
        board.set_piece(i + 10, Color.BLACK, PieceType.PAWN)
    return board


def test_net_captured_equal_shows_zero():
    # Both sides have 4 pawns remaining — no advantage for either
    board = _board_with(white_pawns=4, black_pawns=4)
    assert _net_captured_count(board, Color.WHITE, PieceType.PAWN) == 0
    assert _net_captured_count(board, Color.BLACK, PieceType.PAWN) == 0


def test_net_captured_white_advantage():
    # White has 4 pawns, Black has 3 → white captured one more pawn net
    board = _board_with(white_pawns=4, black_pawns=3)
    assert _net_captured_count(board, Color.WHITE, PieceType.PAWN) == 1
    assert _net_captured_count(board, Color.BLACK, PieceType.PAWN) == 0


def test_net_captured_black_advantage():
    # White has 3 pawns, Black has 5 → black shows 2
    board = _board_with(white_pawns=3, black_pawns=5)
    assert _net_captured_count(board, Color.WHITE, PieceType.PAWN) == 0
    assert _net_captured_count(board, Color.BLACK, PieceType.PAWN) == 2


def test_reclick_selected_piece_deselects():
    # Clicking the same square as the selected piece should deselect
    result = _next_selection(
        selected_sq=5,
        sq=5,
        piece_info=(Color.WHITE, PieceType.PAWN),
        color=Color.WHITE,
    )
    assert result is None


def test_click_different_own_piece_selects():
    # Clicking a different own piece while another is selected → switch
    result = _next_selection(
        selected_sq=5,
        sq=12,
        piece_info=(Color.WHITE, PieceType.ROOK),
        color=Color.WHITE,
    )
    assert result == 12


def test_click_empty_square_deselects():
    result = _next_selection(
        selected_sq=5,
        sq=8,
        piece_info=None,
        color=Color.WHITE,
    )
    assert result is None


def test_click_opponent_piece_deselects():
    result = _next_selection(
        selected_sq=5,
        sq=20,
        piece_info=(Color.BLACK, PieceType.PAWN),
        color=Color.WHITE,
    )
    assert result is None


def test_first_click_own_piece_selects():
    # No prior selection (selected_sq=None)
    result = _next_selection(
        selected_sq=None,
        sq=10,
        piece_info=(Color.BLACK, PieceType.KNIGHT),
        color=Color.BLACK,
    )
    assert result == 10


def test_grouped_dropdown_value_and_selection():
    import pygame
    pygame.init()
    from gui.widgets import GroupedDropdown
    entries = [
        (True,  "── A ──", ""),
        (False, "Alpha",   "sub1"),
        (False, "Beta",    "sub2"),
        (True,  "── B ──", ""),
        (False, "Gamma",   "sub3"),
    ]
    dd = GroupedDropdown(pygame.Rect(0, 0, 200, 32), entries, selected=0)
    assert dd.value == "Alpha"
    dd.selected = 2
    assert dd.value == "Gamma"
    pygame.quit()
