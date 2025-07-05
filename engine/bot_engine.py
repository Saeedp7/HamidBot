from strategies.base import BaseStrategy
from execution.order_manager import OrderManager
from risk.risk_manager import RiskManager
from dashboard.dashboard import PerformanceMetrics
from utils.telegram_notifier import send_telegram_alert


class BotEngine:
    """Orchestrates strategy signals and order execution."""

    def __init__(
        self,
        strategy: BaseStrategy,
        order_manager: OrderManager,
        risk_manager: RiskManager,
        metrics: PerformanceMetrics | None = None,
        notifier:  None = None,
        initial_balance: float = 1.0,
    ) -> None:
        self.strategy = strategy
        self.order_manager = order_manager
        self.risk_manager = risk_manager
        self.metrics = metrics
        self.notifier = notifier
        self.balance = initial_balance
        if self.metrics:
            self.metrics.initial_balance = initial_balance
            self.metrics.balance = initial_balance

    def on_price_update(self, price: float) -> None:
        self.strategy.on_data(price)
        if self.strategy.should_buy():
            qty = self.risk_manager.size_position(self.balance, price)
            order = self.order_manager.place_order("BUY", "BTCUSDT", qty, price)
            if self.metrics:
                self.metrics.record_trade("buy", qty, price)
                self.balance = self.metrics.balance
            if self.notifier:
                self.notifier.send_telegram_alert(order)
        elif self.strategy.should_sell():
            qty = self.risk_manager.size_position(self.balance, price)
            order = self.order_manager.place_order("SELL", "BTCUSDT", qty, price)
            if self.metrics:
                self.metrics.record_trade("sell", qty, price)
                self.balance = self.metrics.balance
            if self.notifier:
                self.notifier.send_telegram_alert(order)
