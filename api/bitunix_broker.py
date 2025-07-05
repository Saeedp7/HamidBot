import requests

def fetch_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100) -> list:
    """Fetch OHLCV from Bitunix API and return as list of [timestamp, open, high, low, close, volume]"""
    url = f"https://api.bitunix.com/api/v1/market/candles?symbol={symbol}&interval={timeframe}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Bitunix API error: {response.text}")
    data = response.json().get('data', [])
    return data[::-1]  # oldest to newest
