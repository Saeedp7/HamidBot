from strategies import load_strategy
from strategies.scalper import ScalperBot


def test_load_strategy():
    cls = load_strategy("scalper")
    assert cls is ScalperBot
