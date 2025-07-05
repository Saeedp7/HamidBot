import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from engine.ai_coordinator import AICoordinator
from strategies.scalper import ScalperBot


def test_ai_coordinator_basic():
    configs = {
        "scalper": {"module": "scalper", "symbol": "BTCUSDT"},
    }
    coordinator = AICoordinator(configs)
    df = pd.DataFrame({"close": [1, 2, 3, 4], "high": [1, 2, 3, 4], "low": [1, 2, 3, 4]})
    market_data = {"scalper": df}
    signals = coordinator.process(market_data)
    assert "scalper" in signals
