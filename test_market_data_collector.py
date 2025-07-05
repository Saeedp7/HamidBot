from data.market_data_collector import MarketDataCollector

collector = MarketDataCollector()

# Single symbol/timeframe
single = collector.get_ohlcv(symbol="BTC/USDT", timeframe="1h", limit=100)
print(single.head())

# Multiple symbols and timeframes
multi = collector.get_ohlcv(symbol=["BTC/USDT", "ETH/USDT"], timeframe=["1h", "4h"], limit=10)
for key, df in multi.items():
    print(key, df.head())

