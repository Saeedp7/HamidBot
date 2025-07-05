import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from data import market_data_collector as mdc


def test_fetch_market_data(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    monkeypatch.setattr(mdc, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(
        mdc,
        "get_klines",
        lambda *args, **kwargs: [
            {"time": 0, "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}
        ],
    )
    df = mdc.fetch_market_data("BTCUSDT", "1m", limit=1, force_refresh=True)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"open", "high", "low", "close", "time"}.issubset(df.columns)
    assert (raw_dir / "BTCUSDT_1m_1.csv").exists()
