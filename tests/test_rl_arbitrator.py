import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.rl_arbitrator import RLArbitrator


def test_action_mapping():
    strategies = [
        "ScalperBot",
        "SwingBot",
        "ArbitrageBot",
        "GridBot",
        "NewsSentimentBot",
        "MeanReversionBot",
        "BreakoutBot",
        "LiquiditySweepBot",
        "DCAInvestmentBot",
        "OptionsHedgerBot",
    ]
    arb = RLArbitrator(strategies)
    assert arb.action_space.n == 10
    assert len(arb.strategies) == 10