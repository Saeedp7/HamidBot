import ccxt

def fetch_ohlcv(symbol: str = 'BTC/USDT', timeframe: str = '1h', limit: int = 100):
    exchange = ccxt.kucoin()
    try:
        exchange.load_markets()
        print(exchange.symbols[:20])  # Show first 20 symbols
        if symbol not in exchange.symbols:
            raise ValueError(f"Symbol {symbol} not supported by KuCoin. Try one of: {list(exchange.symbols)[:5]}...")

        return exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    except Exception as e:
        print(f"KuCoin failed: {e}")
        return []
