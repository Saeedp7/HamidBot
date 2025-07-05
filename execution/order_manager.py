from typing import Any, Dict

from .broker_api import BrokerAPI


class OrderManager:
    """Basic order manager that forwards orders to the broker."""

    def __init__(self, broker: BrokerAPI):
        self.broker = broker
        self.orders: list[Dict[str, Any]] = []

    def place_order(self, side: str, symbol: str, qty: float, price: float | None = None) -> Dict[str, Any]:
        if side.upper() == "BUY":
            order = self.broker.buy(symbol, qty, price)
        elif side.upper() == "SELL":
            order = self.broker.sell(symbol, qty, price)
        else:
            raise ValueError("side must be BUY or SELL")
        self.orders.append(order)
        return order
