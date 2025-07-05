import pandas as pd
from pathlib import Path

from backtest.data_loader import CSVDataLoader


def test_csv_data_loader(tmp_path):
    d = tmp_path / "processed"
    d.mkdir()
    file = d / "TEST_1h.csv"
    pd.DataFrame({"timestamp": ["2024-01-01"], "close": [1]}).to_csv(file, index=False)
    loader = CSVDataLoader(str(tmp_path))
    data = loader.load()
    key = ("TEST", "1h")
    assert key in data
    assert not data[key].empty