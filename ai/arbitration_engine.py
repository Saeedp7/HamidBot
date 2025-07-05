import math
from collections import defaultdict
from typing import Iterable


class ArbitrationEngine:
    """Simple UCB1 based strategy arbitration engine."""

    def __init__(self, decay: float = 0.99) -> None:
        self.decay = decay
        self.counts = defaultdict(int)
        self.values = defaultdict(float)

    # ------------------------------------------------------------------
    def select_strategy(
        self, symbol: str, timeframe: str, strategies: Iterable[str]
    ) -> str:
        """Return the strategy with highest UCB1 score."""
        strategies = list(strategies)
        # ensure each strategy tried once
        for name in strategies:
            if self.counts[name] == 0:
                return name

        total = sum(self.counts[s] for s in strategies)
        ucb_scores = {}
        for name in strategies:
            avg_reward = self.values[name] / self.counts[name]
            bonus = math.sqrt(2 * math.log(total) / self.counts[name])
            ucb_scores[name] = avg_reward + bonus
        return max(ucb_scores, key=ucb_scores.get)

    def update_rewards(self, strategy_name: str, trade_result: float) -> None:
        """Update reward statistics based on trade outcome."""
        self.counts[strategy_name] += 1
        self.values[strategy_name] += trade_result

    def decay_scores(self) -> None:
        """Apply exponential decay to older performance."""
        for name in list(self.values.keys()):
            self.values[name] *= self.decay
            self.counts[name] = max(1, int(self.counts[name] * self.decay))
