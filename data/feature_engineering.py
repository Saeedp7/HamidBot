"""
Module: feature_engineering.py

This module preprocesses and engineers features for OHLCV time-series data:
- Missing value handling
- Timestamp normalization
- Financial indicators (returns, volatility, EMA, RSI, MACD, Bollinger Bands)
"""

import pandas as pd
import numpy as np



def preprocess_and_engineer_features(df: pd.DataFrame, freq: str = "1min") -> pd.DataFrame:
    """
    Clean and enhance OHLCV data for strategy or ML input.

    Parameters:
        df (pd.DataFrame): Raw OHLCV data with 'timestamp' column
        freq (str): Resample frequency (e.g. "1min", "1h")

    Returns:
        pd.DataFrame: Cleaned and feature-enriched DataFrame
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.set_index("timestamp")
    df = df.sort_index()

    # Resample to ensure uniform time intervals
    df = df.resample(freq).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum"
    })

    # Handle missing values: forward-fill then drop any remaining
    df = df.ffill().dropna()

    # Convert numeric columns
    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df = df.dropna()

    # === Feature Engineering ===
    df["returns"] = df["close"].pct_change()
    df["log_returns"] = np.log(df["close"] / df["close"].shift(1))
    df["volatility_5"] = df["returns"].rolling(window=5).std()
    df["volatility_20"] = df["returns"].rolling(window=20).std()
    df["ema_10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["ema_20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["rsi_14"] = compute_rsi(df["close"], 14)
    df["macd"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
    df["macd_signal"] = df["macd"].ewm(span=9).mean()
    sma_20 = df["close"].rolling(window=20).mean()
    std_20 = df["close"].rolling(window=20).std()
    df["bb_upper"] = sma_20 + 2 * std_20
    df["bb_lower"] = sma_20 - 2 * std_20

    df = df.dropna()
    return df.reset_index()


def compute_rsi(series: pd.Series, window: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(com=window-1, adjust=False).mean()
    avg_loss = loss.ewm(com=window-1, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))