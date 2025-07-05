from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


class CSVDataLoader:
    """Load preprocessed OHLCV data from a directory."""

    def __init__(self, directory: str = "data/processed") -> None:
        self.directory = Path(directory)

    def load(self) -> Dict[Tuple[str, str], pd.DataFrame]:
        data: Dict[Tuple[str, str], pd.DataFrame] = {}
        for path in self.directory.rglob("*.csv"):
            name = path.stem
            if "_" not in name:
                continue
            symbol, timeframe = name.split("_", 1)
            df = pd.read_csv(path)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            data[(symbol, timeframe)] = df
        return data