from typing import Any, Dict, Optional

from api.broker_api import BrokerAPI
from utils.trade_logger import TradeLogger


class OrderManager:
    """Send orders through BrokerAPI and log them."""

    def __init__(self, broker: BrokerAPI, logger: Optional[TradeLogger] = None) -> None:
        self.broker = broker
        self.logger = logger
        self.orders: list[Dict[str, Any]] = []

    def place_order(
        self,
        side: str,
        symbol: str,
        qty: float,
        price: float | None = None,
        order_type: str = "market",
    ) -> Dict[str, Any]:
        side = side.lower()
        order_type = order_type.lower()
        if order_type == "market":
            order = self.broker.market_order(symbol, side, qty)
        elif order_type == "limit":
            if price is None:
                raise ValueError("price required for limit order")
            order = self.broker.limit_order(symbol, side, qty, price)
        else:
            raise ValueError("order_type must be 'market' or 'limit'")
        self.orders.append(order)
        if self.logger:
            self.logger.log_trade(order)
        return order
