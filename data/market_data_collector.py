from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

from .fetch_api import get_klines

RAW_DATA_DIR = Path(__file__).resolve().parent / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_market_data(symbol: str, interval: str, limit: int = 100,
                      force_refresh: bool = False) -> pd.DataFrame:
    """Fetch OHLCV market data and cache the result.

    Parameters
    ----------
    symbol : str
        Trading pair symbol, e.g. ``"BTCUSDT"``.
    interval : str
        Kline interval, e.g. ``"1m"`` or ``"1h"``.
    limit : int, optional
        Number of data points to fetch, by default ``100``.
    force_refresh : bool, optional
        Ignore cached file and fetch from API, by default ``False``.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing OHLCV data sorted by time.
    """
    cache_file = RAW_DATA_DIR / f"{symbol}_{interval}_{limit}.csv"
    if cache_file.exists() and not force_refresh:
        return _load_cached(cache_file)

    klines = get_klines(symbol, interval, limit)
    df = _convert_to_dataframe(klines)
    df.to_csv(cache_file, index=False)
    return df


def _load_cached(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["time"] = pd.to_datetime(df["time"])
    return df


def _convert_to_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    # Ensure correct dtypes
    numeric_cols = [c for c in df.columns if c != "time"]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df["time"] = pd.to_datetime(df["time"].astype(int), unit="ms")
    df = df.sort_values("time").reset_index(drop=True)
    return df
