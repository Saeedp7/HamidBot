from collections import deque
from typing import Deque, Dict

from .base import BaseStrategy


class BreakoutStrategy(BaseStrategy):
    """Channel breakout strategy."""

    def __init__(self, window: int = 20, vol_mult: float = 1.5):
        super().__init__(name="Breakout")
        self.window = window
        self.vol_mult = vol_mult
        self.highs: Deque[float] = deque(maxlen=window)
        self.lows: Deque[float] = deque(maxlen=window)
        self.volumes: Deque[float] = deque(maxlen=window)
        self.close = None

    def on_data(self, candle: Dict[str, float]) -> None:
        self.highs.append(candle["high"])
        self.lows.append(candle["low"])
        self.volumes.append(candle["volume"])
        self.close = candle["close"]

    def generate_signal(self) -> str:
        if len(self.highs) < self.window:
            return "hold"
        avg_vol = sum(self.volumes) / len(self.volumes)
        prev_high = max(list(self.highs)[:-1])
        prev_low = min(list(self.lows)[:-1])
        if self.close is None:
            return "hold"
        if self.close > prev_high and self.volumes[-1] > avg_vol * self.vol_mult:
            return "buy"
        if self.close < prev_low and self.volumes[-1] > avg_vol * self.vol_mult:
            return "sell"
        return "hold"
