import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from data.market_data_collector import MarketDataCollector

def test_get_ohlcv_creates_file(tmp_path):
    # Use tmp_path for raw and save dir
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    collector = MarketDataCollector(raw_save_dir=raw_dir, save_dir=raw_dir)

    df = collector.get_ohlcv("BTCUSDT", "1m", limit=1)

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    print("GG")

    expected_file = raw_dir / "BTCUSDT_1m.csv"
    assert expected_file.exists(), f"Expected file not found: {expected_file}"
    print("Saved file:", expected_file)

    # Debug: Print first few rows of the DataFrame
    print("Sample data:")
    print(df.head())

    # Simulate passing data to a strategy for signal testing
    from strategies.scalper import ScalperBot
    bot = ScalperBot(symbol="BTCUSDT", timeframe="1m", risk_pct=0.005)
    signal = bot.generate_signal(df.tail(50))
    print(f"Generated Signal: {signal}")
