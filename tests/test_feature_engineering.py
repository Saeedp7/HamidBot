import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from data.feature_engineering import preprocess_and_engineer_features


def test_preprocess_and_engineer_features():
    data = {
        "timestamp": pd.date_range("2024-01-01", periods=15, freq="min"),
        "open": range(15),
        "high": range(1, 16),
        "low": range(15),
        "close": range(1, 16),
        "volume": [10] * 15,
    }
    df = pd.DataFrame(data)
    processed = preprocess_and_engineer_features(df)
    expected_cols = {
        "returns",
        "log_returns",
        "volatility_5",
        "volatility_20",
        "ema_10",
        "ema_20",
        "rsi_14",
        "macd",
        "macd_signal",
        "bb_upper",
        "bb_lower",
    }
    assert expected_cols.issubset(processed.columns)
    # Ensure returned DataFrame retains original length
    assert len(processed) == len(df)