from typing import List, Optional


def simple_moving_average(prices: List[float], period: int) -> Optional[float]:
    """Calculate simple moving average."""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def exponential_moving_average(prices: List[float], period: int) -> Optional[float]:
    """Calculate exponential moving average."""
    if len(prices) < period:
        return None
    ema = prices[0]
    alpha = 2 / (period + 1)
    for price in prices[1:]:
        ema = alpha * price + (1 - alpha) * ema
    return ema
