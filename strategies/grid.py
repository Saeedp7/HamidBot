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
        if len(df) < 15:
            return Signal("hold")
        atr_val = atr(df["high"].tolist(), df["low"].tolist(), df["close"].tolist(), 14)
        if atr_val is None:
            return Signal("hold")
        price = df["close"].iloc[-1]
        grid_size = atr_val * self.grid_mult
        if self.last_level is None:
            self.last_level = price
            return Signal("hold")
        if price >= self.last_level + grid_size:
            self.last_level = price
            return Signal("sell", 0.5)
        if price <= self.last_level - grid_size:
            self.last_level = price
            return Signal("buy", 0.5)
        return Signal("hold")
