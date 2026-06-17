from bots.greedy_bot import GreedyBot
from bots.random_bot import RandomBot
from gui.game_screen import _is_evaluating_bot


def test_human_is_not_evaluating():
    assert _is_evaluating_bot(None) is False


def test_random_bot_is_not_evaluating():
    assert _is_evaluating_bot(RandomBot("r")) is False


def test_greedy_bot_is_evaluating():
    assert _is_evaluating_bot(GreedyBot("g")) is True
