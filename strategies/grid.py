from __future__ import annotations

import pandas as pd

from .base import BaseStrategy, Signal
from utils.indicators import atr


class GridBot(BaseStrategy):
    """ATR-based dynamic grid trading bot."""

    def __init__(
        self,
        symbol: str,
        timeframe: str = "15m",
        risk_pct: float = 0.02,
        grid_mult: float = 1.0,
    ) -> None:
        super().__init__("GridBot", symbol, timeframe, risk_pct)
        self.grid_mult = grid_mult
        self.last_level = None

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        try:
            if not isinstance(df, pd.DataFrame) or len(df) < 15:
                return self._signal("hold")
            required = {"high", "low", "close"}
            if not required.issubset(df.columns):
                return self._signal("hold")
            highs = df["high"].astype(float).tolist()
            lows = df["low"].astype(float).tolist()
            closes = df["close"].astype(float).tolist()
            atr_val = atr(highs, lows, closes, 14)
            if atr_val is None:
                return self._signal("hold")
            price = closes[-1]
            grid_size = atr_val * self.grid_mult
            if self.last_level is None:
                self.last_level = price
                return self._signal("hold")
            if price >= self.last_level + grid_size:
                self.last_level = price
                return self._signal("sell", 0.5)
            if price <= self.last_level - grid_size:
                self.last_level = price
                return self._signal("buy", 0.5)
            return self._signal("hold")
        except Exception as e:
            print(f"Strategy {self.name} failed: {e}")
            return self._signal("hold")
