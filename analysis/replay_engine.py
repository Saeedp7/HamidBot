from typing import Dict, List, Tuple

from backtest.backtester import Backtester
from engine.strategy_selector import StrategySelector


class ReplayEngine:
    """Simulate historical trades and update strategy scores."""

    def __init__(self, selector: StrategySelector) -> None:
        self.selector = selector

    def _pnl(self, trades: List[Tuple[str, float]], prices: List[float]) -> float:
        position = 0
        cash = 0.0
        for side, price in trades:
            if side == "buy":
                cash -= price
                position += 1
            elif side == "sell":
                cash += price
                position -= 1
        if position:
            cash += position * prices[-1]
        return cash

    def run(self, prices: List[float]) -> Dict[str, float]:
        for name, strategy in self.selector.strategies.items():
            trades = Backtester(strategy).run(prices)
            reward = self._pnl(trades, prices)
            self.selector.score_manager.update_score(name, reward)
        return self.selector.score_manager.get_all()
