import ccxt


def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100) -> list:
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return ohlcv
