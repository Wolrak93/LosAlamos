# tests/test_personalities.py
from bots.personalities import (
    ALL_SCIENTISTS,
    calculate_time_budget,
    create_bethe,
    create_fermi,
    create_feynman,
    create_oppenheimer,
    create_teller,
    create_von_neumann,
)
from bots.minimax_bot import MinimaxBot
from bots.mcts_bot import MCTSBot
from engine.gamestate import get_game_outcome
from engine.movegen import generate_legal_moves
from engine.positions import make_starting_board
from engine.gamestate import play_move


def test_all_factories_create_correct_types():
    assert isinstance(create_fermi(), MinimaxBot)
    assert isinstance(create_von_neumann(), MinimaxBot)
    assert isinstance(create_oppenheimer(), MinimaxBot)
    assert isinstance(create_feynman(), MCTSBot)
    assert isinstance(create_teller(), MCTSBot)
    assert isinstance(create_bethe(), MCTSBot)


def test_all_scientists_list_has_six_entries():
    assert len(ALL_SCIENTISTS) == 6


def test_calculate_time_budget_no_clock():
    assert calculate_time_budget(None, 1) == 120.0


def test_calculate_time_budget_early_moves():
    # Move 1, 60s remaining → 80% / 30 moves = 1.6s
    budget = calculate_time_budget(60.0, 1)
    assert abs(budget - 1.6) < 0.01


def test_calculate_time_budget_late_moves():
    # Move 40, 30s remaining → 10% = 3.0s
    budget = calculate_time_budget(30.0, 40)
    assert abs(budget - 3.0) < 0.01


def test_calculate_time_budget_with_increment():
    budget = calculate_time_budget(60.0, 1, increment_seconds=2.0)
    assert abs(budget - 3.6) < 0.01  # 1.6 + 2.0


def test_all_bots_complete_game_without_crash():
    """Each scientist plays a full game vs RandomBot with a short budget."""
    from bots.random_bot import RandomBot
    from engine.board import Color
    for name, factory in ALL_SCIENTISTS:
        board = make_starting_board()
        scientist = factory()
        opponent = RandomBot("Rnd")
        for _ in range(200):
            if get_game_outcome(board) is not None:
                break
            color = board.side_to_move
            bot = scientist if color == Color.WHITE else opponent
            move = bot.choose_move(board, time_budget_seconds=0.1)
            assert move in generate_legal_moves(board), f"{name} returned illegal move"
            play_move(board, move)
