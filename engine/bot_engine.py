from strategies.base import BaseStrategy
from execution.order_manager import OrderManager
from risk.risk_manager import RiskManager


class BotEngine:
    """Orchestrates strategy signals and order execution."""

    def __init__(self, strategy: BaseStrategy, order_manager: OrderManager, risk_manager: RiskManager):
        self.strategy = strategy
        self.order_manager = order_manager
        self.risk_manager = risk_manager
        self.balance = 1.0  # pretend account balance

    def on_price_update(self, price: float) -> None:
        self.strategy.on_data(price)
        if self.strategy.should_buy():
            qty = self.risk_manager.size_position(self.balance, price)
            self.order_manager.place_order("BUY", "BTCUSDT", qty, price)
        elif self.strategy.should_sell():
            qty = self.risk_manager.size_position(self.balance, price)
            self.order_manager.place_order("SELL", "BTCUSDT", qty, price)
