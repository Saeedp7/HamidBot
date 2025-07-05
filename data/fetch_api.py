import requests
from typing import List, Dict, Any

BASE_URL = "https://fapi.bitunix.com/api/v1/futures/market/kline"


def get_klines(symbol: str, interval: str, limit: int = 100,
               start_time: int | None = None,
               end_time: int | None = None) -> List[Dict[str, Any]]:
    """Fetch OHLCV data from Bitunix public API."""
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
        "type": "LAST_PRICE",
    }
    if start_time is not None:
        params["startTime"] = start_time
    if end_time is not None:
        params["endTime"] = end_time

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()
    payload = response.json()
    if payload.get("code") != 0:
        raise RuntimeError(payload.get("msg", "API error"))
    return payload.get("data", [])
