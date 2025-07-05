"""Simple mean reversion trading strategy."""

from collections import deque
from typing import Deque
import pandas as pd

from .base import BaseStrategy, Signal
from utils.indicators import simple_moving_average


class MeanReversionStrategy(BaseStrategy):
    """Buy when price dips below the moving average and sell on rallies."""

    def __init__(self, window: int = 10, threshold: float = 0.01) -> None:
        super().__init__(name="Mean Reversion")
        self.window = window
        self.threshold = threshold
        self.prices: Deque[float] = deque(maxlen=window)

    def on_data(self, price: float) -> None:  # type: ignore[override]
        self.prices.append(price)

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if "close" not in df.columns or len(df) < self.window:
            return self._signal("hold")
        prices = df["close"].iloc[-self.window :].tolist()
        sma = simple_moving_average(prices, self.window)
        if sma is None:
            return self._signal("hold")
        last_price = prices[-1]
        if last_price < sma * (1 - self.threshold):
            return self._signal("buy")
        if last_price > sma * (1 + self.threshold):
            return self._signal("sell")
        return self._signal("hold")

