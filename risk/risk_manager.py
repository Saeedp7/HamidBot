class RiskManager:
    """Basic position sizing and risk checks."""

    def __init__(self, max_position: float = 1.0):
        self.max_position = max_position

    def size_position(self, balance: float, price: float) -> float:
        qty = balance / price
        return min(qty, self.max_position)
