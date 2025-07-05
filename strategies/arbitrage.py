from __future__ import annotations

from typing import Dict
import pandas as pd

from .base import BaseStrategy, Signal


class ArbitrageBot(BaseStrategy):
    """Cross-exchange arbitrage detector."""

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1m",
        risk_pct: float = 0.01,
        threshold: float = 0.002,
    ) -> None:
        super().__init__("ArbitrageBot", symbol, timeframe, risk_pct)
        self.threshold = threshold

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if df.empty:
            return self._signal("hold")
        prices: Dict[str, float] = df.iloc[-1].to_dict()
        max_ex = max(prices, key=prices.get)
        min_ex = min(prices, key=prices.get)
        spread = prices[max_ex] - prices[min_ex]
        if prices[min_ex] and spread / prices[min_ex] > self.threshold:
            confidence = min(1.0, spread / prices[min_ex])
            return self._signal("buy", confidence)
        return self._signal("hold")
