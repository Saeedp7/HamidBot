from __future__ import annotations

import pandas as pd
from typing import Optional

from .base import BaseStrategy, Signal
from utils.indicators import atr


class ScalperBot(BaseStrategy):
    """EMA cross scalper with volatility filter."""

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1m",
        risk_pct: float = 0.005,
        fast: int = 3,
        slow: int = 8,
        vol_window: int = 20,
        vol_threshold: float = 0.005,
    ) -> None:
        super().__init__("ScalperBot", symbol, timeframe, risk_pct)
        self.fast = fast
        self.slow = slow
        self.vol_window = vol_window
        self.vol_threshold = vol_threshold

    def _volatility(self, df: pd.DataFrame) -> Optional[float]:
        if len(df) < self.vol_window + 1:
            return None
        return df["close"].pct_change().rolling(self.vol_window).std().iloc[-1]

    def _atr_levels(self, df: pd.DataFrame) -> tuple[float, float] | tuple[None, None]:
        highs = df["high"].tolist()
        lows = df["low"].tolist()
        closes = df["close"].tolist()
        atr_val = atr(highs, lows, closes, 14)
        if atr_val is None:
            return None, None
        price = closes[-1]
        return price - atr_val * 0.3, price + atr_val * 0.3

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if df.empty or len(df) < self.slow + 1:
            return self._signal("hold")
        ema_fast = df["close"].ewm(span=self.fast, adjust=False).mean().iloc[-1]
        ema_slow = df["close"].ewm(span=self.slow, adjust=False).mean().iloc[-1]
        vol = self._volatility(df)
        if vol is None or vol > self.vol_threshold:
            return self._signal("hold")
        sl, tp = self._atr_levels(df)
        if ema_fast > ema_slow:
            return self._signal("buy", 0.7, sl, tp)
        if ema_fast < ema_slow:
            return self._signal("sell", 0.7, sl, tp)
        return self._signal("hold")
