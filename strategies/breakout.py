from collections import deque
from typing import Deque

from .base import BaseStrategy


class BreakoutStrategy(BaseStrategy):
    """Channel breakout strategy."""

    def __init__(self, window: int = 20):
        super().__init__(name="Breakout")
        self.window = window
        self.prices: Deque[float] = deque(maxlen=window)

    def on_data(self, price: float) -> None:
        self.prices.append(price)

    def should_buy(self) -> bool:
        return len(self.prices) == self.window and self.prices[-1] == max(self.prices)

    def should_sell(self) -> bool:
        return len(self.prices) == self.window and self.prices[-1] == min(self.prices)
