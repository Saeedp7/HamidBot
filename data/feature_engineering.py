import pandas as pd
import numpy as np


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Return the Relative Strength Index."""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def preprocess_and_engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess OHLCV data and create simple technical features.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least ``timestamp``, ``open``, ``high``, ``low``,
        ``close`` and ``volume`` columns.

    Returns
    -------
    pandas.DataFrame
        DataFrame with engineered features appended.
    """
    processed = df.copy()
    if "timestamp" in processed.columns:
        processed = processed.sort_values("timestamp").reset_index(drop=True)

    numeric_cols = [c for c in ["open", "high", "low", "close", "volume"] if c in processed.columns]
    processed[numeric_cols] = processed[numeric_cols].apply(pd.to_numeric, errors="coerce")

    processed["returns"] = processed["close"].pct_change()
    processed["log_returns"] = np.log(processed["close"] / processed["close"].shift(1))

    # Simple moving averages for backward compatibility
    processed["close_ma_5"] = processed["close"].rolling(window=5).mean()
    processed["close_ma_10"] = processed["close"].rolling(window=10).mean()

    processed["volatility_5"] = processed["returns"].rolling(window=5).std()
    processed["volatility_20"] = processed["returns"].rolling(window=20).std()

    processed["ema_10"] = processed["close"].ewm(span=10, adjust=False).mean()
    processed["ema_20"] = processed["close"].ewm(span=20, adjust=False).mean()

    processed["rsi_14"] = compute_rsi(processed["close"], 14)

    processed["macd"] = (
        processed["close"].ewm(span=12, adjust=False).mean()
        - processed["close"].ewm(span=26, adjust=False).mean()
    )
    processed["macd_signal"] = processed["macd"].ewm(span=9, adjust=False).mean()

    sma_20 = processed["close"].rolling(window=20).mean()
    std_20 = processed["close"].rolling(window=20).std()
    processed["bb_upper"] = sma_20 + 2 * std_20
    processed["bb_lower"] = sma_20 - 2 * std_20

    return processed