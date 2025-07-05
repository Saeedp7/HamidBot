class BaseStrategy:
    """Base class for trading strategies."""

    def __init__(self, name: str = "Base"):
        self.name = name

    def on_data(self, price: float) -> None:
        """Receive new price data."""
        raise NotImplementedError

    def should_buy(self) -> bool:
        """Return True if a buy signal is generated."""
        return False

    def should_sell(self) -> bool:
        """Return True if a sell signal is generated."""
        return False
