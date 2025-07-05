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
        try:
            if not isinstance(df, pd.DataFrame) or df.empty:
                return self._signal("hold")
            prices: Dict[str, float] = (
                df.iloc[-1].apply(pd.to_numeric, errors="coerce").dropna().to_dict()
            )
            if not prices:
                return self._signal("hold")
            max_ex = max(prices, key=prices.get)
            min_ex = min(prices, key=prices.get)
            min_price = prices[min_ex]
            spread = prices[max_ex] - min_price
            if min_price and spread / min_price > self.threshold:
                confidence = min(1.0, spread / min_price)
                return self._signal("buy", confidence)
            return self._signal("hold")
        except Exception as e:
            print(f"Strategy {self.name} failed: {e}")
        return self._signal("hold")
