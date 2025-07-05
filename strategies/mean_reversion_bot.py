from __future__ import annotations

import pandas as pd

from .base import BaseStrategy, Signal


class MeanReversionBot(BaseStrategy):
    """Bollinger band mean reversion with volume divergence."""

    def __init__(self, symbol: str, timeframe: str = "1h", risk_pct: float = 0.02, window: int = 20) -> None:
        super().__init__("MeanReversionBot", symbol, timeframe, risk_pct)
        self.window = window

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < self.window + 1:
            return self._signal("hold")
        close = df["close"]
        mean = close.rolling(self.window).mean().iloc[-1]
        std = close.rolling(self.window).std().iloc[-1]
        upper = mean + 2 * std
        lower = mean - 2 * std
        vol_mean = df["volume"].rolling(self.window).mean().iloc[-1]
        vol = df["volume"].iloc[-1]
        price = close.iloc[-1]
        if price < lower and vol > vol_mean:
            return self._signal("buy", 0.5)
        if price > upper and vol > vol_mean:
            return self._signal("sell", 0.5)
        return self._signal("hold")
