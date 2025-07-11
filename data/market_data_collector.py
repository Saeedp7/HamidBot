from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple, Union
import os


import os
import pandas as pd

from .fetch_api import get_klines
from api import bitunix_broker, binance_api
from .feature_engineering import preprocess_and_engineer_features


# Create default raw data storage directory
RAW_DATA_DIR = Path(__file__).resolve().parent / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)


def fetch_market_data(symbol: str, interval: str, limit: int = 100, force_refresh: bool = False) -> pd.DataFrame:

    """Fetch OHLCV market data and cache the result."""
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
    numeric_cols = [c for c in df.columns if c != "time"]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df["time"] = pd.to_datetime(df["time"].astype(int), unit="ms")
    df = df.sort_values("time").reset_index(drop=True)
    return df


class MarketDataCollector:
    def __init__(self, raw_save_dir: Path = Path("data/raw"), save_dir: Union[str, Path] = ("data/raw")):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.raw_save_dir = raw_save_dir

    def _get_single_ohlcv(
        self, symbol: str, timeframe: str, limit: int = 200, save: bool = True
    ) -> pd.DataFrame:
        # Only use get_klines now
        data = get_klines(symbol, timeframe, limit)

        df = pd.DataFrame(data)
        df = df.rename(columns={
            "time": "timestamp",
            "baseVol": "volume"
        })
        expected = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in expected:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="ms")
        df[["open", "high", "low", "close", "volume"]] = df[["open", "high", "low", "close", "volume"]].astype(float)
        print("RAW API response sample:", data[:2])

        if save:
            # Save raw CSV
            self.save_dir.mkdir(parents=True, exist_ok=True)
            raw_path = self.save_dir / f"{symbol}_{timeframe}.csv"
            df.to_csv(raw_path, index=False)
            self.raw_save_dir.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.raw_save_dir / f"{symbol}_{timeframe}.csv", index=False)
        # Run feature engineering on the fetched data
        processed_df = preprocess_and_engineer_features(df)

        # Save processed dataset for later use
        if save:
            os.makedirs("data/processed", exist_ok=True)
            processed_df.to_csv(
                f"data/processed/{symbol}_{timeframe}.csv", index=False
            )


        return df

    def get_ohlcv(
        self,
        symbol: Union[str, Iterable[str]],
        timeframe: Union[str, Iterable[str]],
        limit: int = 200,
        save: bool = True,
    ) -> Union[pd.DataFrame, Dict[Tuple[str, str], pd.DataFrame]]:
        if isinstance(symbol, str) and isinstance(timeframe, str):
            return self._get_single_ohlcv(symbol, timeframe, limit, save)
        symbols = [symbol] if isinstance(symbol, str) else list(symbol)
        timeframes = [timeframe] if isinstance(timeframe, str) else list(timeframe)
        results: Dict[Tuple[str, str], pd.DataFrame] = {}
        for sym in symbols:
            for tf in timeframes:
                results[(sym, tf)] = self._get_single_ohlcv(sym, tf, limit, save)
        return results


def load_cached_or_fetch(
    symbol: Union[str, Iterable[str]],
    timeframe: Union[str, Iterable[str]],
    limit: int = 100,
) -> Union[pd.DataFrame, Dict[Tuple[str, str], pd.DataFrame]]:
    if isinstance(symbol, str) and isinstance(timeframe, str):
        path = RAW_DATA_DIR / f"{symbol}_{timeframe}.csv"
        if path.exists():
            return pd.read_csv(path, parse_dates=["timestamp"])
        return MarketDataCollector().get_ohlcv(symbol, timeframe, limit)
    symbols = [symbol] if isinstance(symbol, str) else list(symbol)
    timeframes = [timeframe] if isinstance(timeframe, str) else list(timeframe)

    results: Dict[Tuple[str, str], pd.DataFrame] = {}
    collector = MarketDataCollector()
    for sym in symbols:
        for tf in timeframes:
            path = RAW_DATA_DIR / f"{sym}_{tf}.csv"
            if path.exists():
                results[(sym, tf)] = pd.read_csv(path, parse_dates=["timestamp"])
            else:
                results[(sym, tf)] = collector.get_ohlcv(sym, tf, limit)
    return results
