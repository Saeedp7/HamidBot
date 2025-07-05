import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from data.feature_engineering import preprocess_and_engineer_features


def test_feature_pipeline():
    # Create a minimal but valid DataFrame
    data = {
        "timestamp": pd.date_range("2020-01-01", periods=50, freq="1min"),
        "open": [i for i in range(1, 51)],
        "high": [i + 0.1 for i in range(1, 51)],
        "low": [i - 0.1 for i in range(1, 51)],
        "close": [i for i in range(1, 51)],
        "volume": [100 + i * 10 for i in range(50)],
    }
    df = pd.DataFrame(data)

    result = preprocess_and_engineer_features(df)

    # Basic checks
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

    # Check presence of key features
    required_cols = {"rsi_14", "macd", "macd_signal", "bb_upper", "bb_lower", "returns"}
    assert required_cols.issubset(result.columns), f"Missing columns: {required_cols - set(result.columns)}"
