class BrokerAPI:
    """Abstract broker API used by the bot."""

    def buy(self, symbol: str, qty: float, price: float | None = None):
        """Place a buy order."""
        raise NotImplementedError

    def sell(self, symbol: str, qty: float, price: float | None = None):
        """Place a sell order."""
        raise NotImplementedError
