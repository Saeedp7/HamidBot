import pandas as pd
import os
from api import bitunix_broker, binance_api
from typing import Dict, Iterable, Tuple, Union


class MarketDataCollector:
    def __init__(self, fallback: bool = True):
        self.fallback = fallback

    def _get_single_ohlcv(
        self, symbol: str, timeframe: str, limit: int = 100, save: bool = True
    ) -> pd.DataFrame:
        try:
            data = bitunix_broker.fetch_ohlcv(symbol, timeframe, limit)
        except Exception as e:
            print(f"Bitunix failed: {e}")
            if not self.fallback:
                raise
            data = binance_api.fetch_ohlcv(symbol, timeframe, limit)

        df = pd.DataFrame(
            data,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        if save:
            os.makedirs("data/raw", exist_ok=True)
            df.to_csv(f"data/raw/{symbol}_{timeframe}.csv", index=False)

        return df

    def get_ohlcv(
        self,
        symbol: Union[str, Iterable[str]],
        timeframe: Union[str, Iterable[str]],
        limit: int = 100,
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
        path = f"data/raw/{symbol}_{timeframe}.csv"
        if os.path.exists(path):
            return pd.read_csv(path, parse_dates=["timestamp"])
        return MarketDataCollector().get_ohlcv(symbol, timeframe, limit)

    symbols = [symbol] if isinstance(symbol, str) else list(symbol)
    timeframes = [timeframe] if isinstance(timeframe, str) else list(timeframe)
    results: Dict[Tuple[str, str], pd.DataFrame] = {}
    collector = MarketDataCollector()
    for sym in symbols:
        for tf in timeframes:
            path = f"data/raw/{sym}_{tf}.csv"
            if os.path.exists(path):
                results[(sym, tf)] = pd.read_csv(path, parse_dates=["timestamp"])
            else:
                results[(sym, tf)] = collector.get_ohlcv(sym, tf, limit)
    return results

