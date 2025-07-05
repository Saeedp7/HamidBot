from execution.broker_api import BrokerAPI
from execution.order_manager import OrderManager
from engine.bot_engine import BotEngine
from risk.risk_manager import RiskManager
from strategies.ema_crossover import EMACrossoverStrategy


class DummyBroker(BrokerAPI):
    """A very naive broker implementation for demonstration."""

    def buy(self, symbol: str, qty: float, price: float | None = None):
        order = {"side": "BUY", "symbol": symbol, "qty": qty, "price": price}
        print(f"Buying: {order}")
        return order

    def sell(self, symbol: str, qty: float, price: float | None = None):
        order = {"side": "SELL", "symbol": symbol, "qty": qty, "price": price}
        print(f"Selling: {order}")
        return order


def run_demo():
    strategy = EMACrossoverStrategy()
    broker = DummyBroker()
    order_manager = OrderManager(broker)
    risk_manager = RiskManager()
    engine = BotEngine(strategy, order_manager, risk_manager)

    prices = [100, 101, 102, 103, 102, 101, 104, 105, 104]
    for price in prices:
        engine.on_price_update(price)


if __name__ == "__main__":
    run_demo()
