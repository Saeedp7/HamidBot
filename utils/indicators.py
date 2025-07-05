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

import pandas as pd


def ema(prices: List[float], period: int) -> Optional[float]:
    """Calculate exponential moving average using pandas."""
    if len(prices) < period:
        return None
    return pd.Series(prices).ewm(span=period, adjust=False).mean().iloc[-1]


def rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Compute Relative Strength Index."""
    if len(prices) < period + 1:
        return None
    series = pd.Series(prices)
    diff = series.diff().dropna()
    up = diff.clip(lower=0)
    down = -diff.clip(upper=0)
    ma_up = up.ewm(com=period - 1, adjust=False).mean()
    ma_down = down.ewm(com=period - 1, adjust=False).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs.iloc[-1]))


def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[tuple[float, float]]:
    """Return MACD line and signal line."""
    if len(prices) < slow:
        return None
    series = pd.Series(prices)
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line.iloc[-1], signal_line.iloc[-1]


def atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[float]:
    """Calculate Average True Range."""
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None
    df = pd.DataFrame({"high": highs, "low": lows, "close": closes})
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean().iloc[-1]