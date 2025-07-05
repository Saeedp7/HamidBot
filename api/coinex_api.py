import ccxt


def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100) -> list:
    """Fetch OHLCV data from Coinex via ccxt."""
    exchange = ccxt.coinex()
    return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
