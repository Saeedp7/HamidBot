import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from data.market_data_collector import MarketDataCollector


def test_get_ohlcv_creates_file(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    # Patch save path
    import os
    original_makedirs = os.makedirs
    original_to_csv = pd.DataFrame.to_csv

    def mocked_makedirs(path, *args, **kwargs):
        # Redirect "data/raw" to our test folder
        if path == "data/raw":
            path = str(raw_dir)
        return original_makedirs(path, *args, **kwargs)

    def mocked_to_csv(self, path, *args, **kwargs):
        # Redirect saving path
        if isinstance(path, str) and "data/raw" in path:
            filename = path.split("/")[-1]
            path = raw_dir / filename
        return original_to_csv(self, path, *args, **kwargs)

    os.makedirs = mocked_makedirs
    pd.DataFrame.to_csv = mocked_to_csv

    try:
        collector = MarketDataCollector()
        df = collector.get_ohlcv("BTCUSDT", "1m", limit=1)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        print("GG")

        expected_file = raw_dir / "BTCUSDT_1m.csv"
        assert expected_file.exists(), f"Expected file not found: {expected_file}"
        print("Saved file:", expected_file)

    finally:
        # Restore original methods
        os.makedirs = original_makedirs
        pd.DataFrame.to_csv = original_to_csv

if __name__ == "__main__":
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / "test"
        tmp_path.mkdir(parents=True, exist_ok=True)
        test_get_ohlcv_creates_file(tmp_path)