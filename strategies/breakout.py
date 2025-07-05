from collections import deque
from typing import Deque

import pandas as pd

from .base import BaseStrategy, Signal


class BreakoutBot(BaseStrategy):
    """Channel breakout strategy."""

    def __init__(self, symbol: str, timeframe: str = "1h", risk_pct: float = 0.02, window: int = 20, vol_mult: float = 1.5) -> None:
        super().__init__("BreakoutBot", symbol, timeframe, risk_pct)
        self.window = window
        self.vol_mult = vol_mult
        self.highs: Deque[float] = deque(maxlen=window)
        self.lows: Deque[float] = deque(maxlen=window)
        self.volumes: Deque[float] = deque(maxlen=window)
        self.close = None

    def on_data(self, candle: dict[str, float]) -> None:
        self.highs.append(candle["high"])
        self.lows.append(candle["low"])
        self.volumes.append(candle["volume"])
        self.close = candle["close"]

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        try:
            if not isinstance(df, pd.DataFrame) or df.empty:
                return self._signal("hold")
            required = {"high", "low", "close", "volume"}
            if not required.issubset(df.columns):
                return self._signal("hold")
            for _, candle in df.tail(1).iterrows():
                self.on_data({
                    "high": float(candle["high"]),
                    "low": float(candle["low"]),
                    "volume": float(candle["volume"]),
                    "close": float(candle["close"]),
                })
            if len(self.highs) < self.window:
                return self._signal("hold")
            avg_vol = sum(self.volumes) / len(self.volumes)
            prev_high = max(list(self.highs)[:-1])
            prev_low = min(list(self.lows)[:-1])
            if self.close is None:
                return self._signal("hold")
            if self.close > prev_high and self.volumes[-1] > avg_vol * self.vol_mult:
                return self._signal("buy", 0.5)
            if self.close < prev_low and self.volumes[-1] > avg_vol * self.vol_mult:
                return self._signal("sell", 0.5)
            return self._signal("hold")
        except Exception as e:
            print(f"Strategy {self.name} failed: {e}")
        return self._signal("hold")
