from collections import deque
from typing import Deque

from .base import BaseStrategy
from utils.indicators import exponential_moving_average


class EMACrossoverStrategy(BaseStrategy):
    """Simple EMA crossover strategy."""

    def __init__(self, fast: int = 12, slow: int = 26):
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
            self.fast_ema = exponential_moving_average(price_list, self.fast)
            self.slow_ema = exponential_moving_average(price_list, self.slow)

    def should_buy(self) -> bool:
        if self.fast_ema is None or self.slow_ema is None:
            return False
        return self.fast_ema > self.slow_ema

    def should_sell(self) -> bool:
        if self.fast_ema is None or self.slow_ema is None:
            return False
        return self.fast_ema < self.slow_ema
