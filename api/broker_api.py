from typing import Any, Dict

from .config import Config
from .open_api_http_future_private import OpenApiHttpFuturePrivate


class BrokerAPI:
    """Wrapper around Bitunix HTTP API for order execution."""

    def __init__(self, config_path: str = "api/config.yaml") -> None:
        self.config = Config(config_path)
        self.client = OpenApiHttpFuturePrivate(self.config)

    def market_order(self, symbol: str, side: str, qty: float) -> Dict[str, Any]:
        """Place a market order."""
        return self.client.place_order(
            symbol=symbol,
            side=side.upper(),
            order_type="MARKET",
            qty=str(qty),
        )

    def limit_order(self, symbol: str, side: str, qty: float, price: float) -> Dict[str, Any]:
        """Place a limit order."""
        return self.client.place_order(
            symbol=symbol,
            side=side.upper(),
            order_type="LIMIT",
            qty=str(qty),
            price=str(price),
        )
