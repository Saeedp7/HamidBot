class RiskManager:
    """Position sizing and basic risk checks."""

    def __init__(self, max_position: float = 1.0, risk_percent: float = 0.01):
        self.max_position = max_position
        self.risk_percent = risk_percent

    def size_position(self, balance: float, price: float, stop_price: float | None = None) -> float:
        if stop_price:
            risk_per_unit = abs(price - stop_price)
            if risk_per_unit == 0:
                qty = 0
            else:
                qty = (balance * self.risk_percent) / risk_per_unit
        else:
            qty = balance / price
        return min(qty, self.max_position)
