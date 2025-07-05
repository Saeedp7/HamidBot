from data.market_data_collector import MarketDataCollector


def main() -> None:
    collector = MarketDataCollector()

    # Single symbol/timeframe
    single = collector.get_ohlcv(symbol="BTCUSDT", timeframe="1h", limit=100)
    print(single.head())

    # Multiple symbols and timeframes
    multi = collector.get_ohlcv(symbol=["BTCUSDT", "ETHUSDT"], timeframe=["1h", "4h"], limit=10)
    for key, df in multi.items():
        print(key, df.head())


if __name__ == "__main__":
    main()
