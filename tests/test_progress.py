from bots.progress import BotProgress


def test_bot_progress_defaults_to_none():
    p = BotProgress()
    assert p.depth is None
    assert p.eval is None
    assert p.sims is None


def test_bot_progress_fields_can_be_set():
    p = BotProgress()
    p.depth = 5
    p.eval = -1.5
    p.sims = 1200
    assert p.depth == 5
    assert p.eval == -1.5
    assert p.sims == 1200


def test_bot_progress_mate_in_defaults_to_none():
    p = BotProgress()
    assert p.mate_in is None


def test_bot_progress_mate_in_can_be_set():
    p = BotProgress()
    p.mate_in = 3
    assert p.mate_in == 3
    p.mate_in = -2
    assert p.mate_in == -2
