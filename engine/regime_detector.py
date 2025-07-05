from collections import deque
from typing import Deque, Dict

from utils.indicators import atr


class RegimeDetector:
    """Classify regime based on ATR and volatility bands."""

    def __init__(self, atr_period: int = 14, band_mult: float = 1.5) -> None:
        self.atr_period = atr_period
        self.band_mult = band_mult
        self.highs: Deque[float] = deque(maxlen=atr_period * 2)
        self.lows: Deque[float] = deque(maxlen=atr_period * 2)
        self.closes: Deque[float] = deque(maxlen=atr_period * 2)

    def on_data(self, candle: Dict[str, float]) -> None:
        self.highs.append(candle["high"])
        self.lows.append(candle["low"])
        self.closes.append(candle["close"])

    def detect(self) -> str:
        if len(self.closes) < self.atr_period + 1:
            return "unknown"
        atr_val = atr(list(self.highs), list(self.lows), list(self.closes), self.atr_period)
        if atr_val is None:
            return "unknown"
        band = max(self.highs) - min(self.lows)
        return "trending" if band > atr_val * self.band_mult else "ranging"
