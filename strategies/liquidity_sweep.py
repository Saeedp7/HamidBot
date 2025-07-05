from __future__ import annotations

import pandas as pd

from .base import BaseStrategy, Signal


class LiquiditySweepBot(BaseStrategy):
    """Simplified smart money concept strategy."""

    def __init__(self, symbol: str, timeframe: str = "15m", risk_pct: float = 0.03) -> None:
        super().__init__("LiquiditySweepBot", symbol, timeframe, risk_pct)

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        try:
            if not isinstance(df, pd.DataFrame) or len(df) < 5:
                return self._signal("hold")
            if not {"high", "low"}.issubset(df.columns):
                return self._signal("hold")
            highs = df["high"].astype(float)
            lows = df["low"].astype(float)
            recent_high = highs.iloc[-1]
            recent_low = lows.iloc[-1]
            prev_high = highs.iloc[-5:-1].max()
            prev_low = lows.iloc[-5:-1].min()
            if recent_high > prev_high:
                return self._signal("sell", 0.4)
            if recent_low < prev_low:
                return self._signal("buy", 0.4)
            return self._signal("hold")
        except Exception as e:
            print(f"Strategy {self.name} failed: {e}")
            return self._signal("hold")
