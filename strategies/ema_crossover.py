from collections import deque
from typing import Deque

from .base import BaseStrategy
from utils.indicators import ema


class EMACrossoverStrategy(BaseStrategy):
    """Simple EMA crossover strategy."""

    def __init__(self, fast: int = 9, slow: int = 21):
        super().__init__(name="EMA Crossover")
        self.fast = fast
        self.slow = slow
        self.prices: Deque[float] = deque(maxlen=slow)
        self.fast_ema = None
        self.slow_ema = None

    def on_data(self, price: float) -> None:
        self.prices.append(price)
        if len(self.prices) >= self.slow:
            price_list = list(self.prices)
            self.fast_ema = ema(price_list, self.fast)
            self.slow_ema = ema(price_list, self.slow)

    def generate_signal(self) -> str:
        if self.fast_ema is None or self.slow_ema is None:
            return "hold"
        if self.fast_ema > self.slow_ema:
            return "buy"
        if self.fast_ema < self.slow_ema:
            return "sell"
        return "hold"
