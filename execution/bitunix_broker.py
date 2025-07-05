from typing import Any, Dict, Optional

from api.config import Config
from api.open_api_http_future_private import OpenApiHttpFuturePrivate
from .broker_api import BrokerAPI


class BitunixBroker(BrokerAPI):
    """BrokerAPI implementation using Bitunix Open API."""

    def __init__(self, config_path: str = "api/config.yaml"):
        self.config = Config(config_path)
        self.client = OpenApiHttpFuturePrivate(self.config)

    def buy(self, symbol: str, qty: float, price: Optional[float] = None) -> Dict[str, Any]:
        order_type = "LIMIT" if price is not None else "MARKET"
        return self.client.place_order(
            symbol=symbol,
            side="BUY",
            order_type=order_type,
            qty=str(qty),
            price=str(price) if price is not None else None,
        )

    def sell(self, symbol: str, qty: float, price: Optional[float] = None) -> Dict[str, Any]:
        order_type = "LIMIT" if price is not None else "MARKET"
        return self.client.place_order(
            symbol=symbol,
            side="SELL",
            order_type=order_type,
            qty=str(qty),
            price=str(price) if price is not None else None,
        )
