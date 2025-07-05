from __future__ import annotations

import pandas as pd
from typing import Optional

from .base import BaseStrategy, Signal
from utils.indicators import rsi, macd


class SwingBot(BaseStrategy):
    """Swing trading strategy using EMA/SMA cross and MACD."""

    def __init__(
        self,
        symbol: str,
        timeframe: str = "4h",
        risk_pct: float = 0.02,
        ema_fast: int = 20,
        sma_slow: int = 50,
    ) -> None:
        super().__init__("SwingBot", symbol, timeframe, risk_pct)
        self.ema_fast = ema_fast
        self.sma_slow = sma_slow

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if len(df) < max(self.ema_fast, self.sma_slow) + 2:
            return Signal("hold")
        ema_fast = df["close"].ewm(span=self.ema_fast, adjust=False).mean().iloc[-1]
        sma_slow = df["close"].rolling(self.sma_slow).mean().iloc[-1]
        macd_val = macd(df["close"].tolist())
        rsi_val = rsi(df["close"].tolist())
        if not macd_val or rsi_val is None:
            return Signal("hold")
        macd_line, macd_signal = macd_val
        if (
            ema_fast > sma_slow
            and macd_line > macd_signal
            and rsi_val < 70
        ):
            return Signal("buy", 0.6)
        if (
            ema_fast < sma_slow
            and macd_line < macd_signal
            and rsi_val > 30
        ):
            return Signal("sell", 0.6)
        return Signal("hold")
