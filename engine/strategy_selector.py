from strategies.base import BaseStrategy


class StrategySelector:
    """Selects which strategy to run based on market regime."""

    def __init__(self, strategies: dict[str, BaseStrategy]):
        self.strategies = strategies
        self.active: BaseStrategy | None = None

    def select(self, regime: str) -> BaseStrategy:
        self.active = self.strategies.get(regime, next(iter(self.strategies.values())))
        return self.active
