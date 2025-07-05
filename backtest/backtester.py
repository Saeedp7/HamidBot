from strategies.base import BaseStrategy


class Backtester:
    """Very simple backtesting engine."""

    def __init__(self, strategy: BaseStrategy):
        self.strategy = strategy
        self.trades = []

    def run(self, prices: list[float]):
        for price in prices:
            self.strategy.on_data(price)
            if self.strategy.should_buy():
                self.trades.append(("buy", price))
            elif self.strategy.should_sell():
                self.trades.append(("sell", price))
        return self.trades
