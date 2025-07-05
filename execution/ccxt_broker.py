import os
from typing import Any, Dict, Optional

import ccxt

from .broker_api import BrokerAPI


class CcxtBroker(BrokerAPI):
    """Generic broker implementation using the ccxt library."""

    def __init__(self, exchange_id: str, api_key: str | None = None, secret: str | None = None, **kwargs):
        exchange_class = getattr(ccxt, exchange_id)
        api_key = api_key or os.getenv(f"{exchange_id.upper()}_API_KEY")
        secret = secret or os.getenv(f"{exchange_id.upper()}_SECRET_KEY")
        self.client = exchange_class({
            "apiKey": api_key,
            "secret": secret,
            **kwargs,
        })

    def buy(self, symbol: str, qty: float, price: Optional[float] = None) -> Dict[str, Any]:
        if price is None:
            return self.client.create_market_buy_order(symbol, qty)
        return self.client.create_limit_buy_order(symbol, qty, price)

    def sell(self, symbol: str, qty: float, price: Optional[float] = None) -> Dict[str, Any]:
        if price is None:
            return self.client.create_market_sell_order(symbol, qty)
        return self.client.create_limit_sell_order(symbol, qty, price)
