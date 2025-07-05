import itertools
from typing import Any, Dict, List, Tuple, Type

import yfinance as yf

from strategies.base import BaseStrategy
from backtest.backtester import Backtester


class StrategyOptimizer:
    """Optimize strategy parameters using historical data from yfinance."""

    def __init__(self, strategy_cls: Type[BaseStrategy], param_grid: Dict[str, List[Any]], symbol: str, start: str, end: str):
        self.strategy_cls = strategy_cls
        self.param_grid = param_grid
        self.symbol = symbol
        self.start = start
        self.end = end

    def _load_prices(self) -> List[float]:
        df = yf.download(self.symbol, start=self.start, end=self.end, progress=False)
        return df['Close'].dropna().tolist()

    def _evaluate(self, trades: List[Tuple[str, float]], prices: List[float]) -> float:
        position = 0
        cash = 0.0
        for side, price in trades:
            if side == 'buy':
                cash -= price
                position += 1
            elif side == 'sell':
                cash += price
                position -= 1
        if position:
            cash += position * prices[-1]
        return cash

    def optimize(self) -> Tuple[Dict[str, Any], float]:
        prices = self._load_prices()
        best_params: Dict[str, Any] = {}
        best_score = float('-inf')
        keys = list(self.param_grid.keys())
        for values in itertools.product(*self.param_grid.values()):
            params = dict(zip(keys, values))
            strategy = self.strategy_cls(**params)
            trades = Backtester(strategy).run(prices)
            score = self._evaluate(trades, prices)
            if score > best_score:
                best_score = score
                best_params = params
        return best_params, best_score
