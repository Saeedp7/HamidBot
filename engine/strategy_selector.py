import random
from typing import Dict

from strategies.base import BaseStrategy
from .score_manager import ScoreManager


class StrategySelector:
    """Pick strategies using an epsilon-greedy MAB approach."""

    def __init__(
        self,
        strategies: Dict[str, BaseStrategy],
        score_manager: ScoreManager,
        epsilon: float = 0.1,
    ) -> None:
        self.strategies = strategies
        self.score_manager = score_manager
        self.epsilon = epsilon
        self.active: BaseStrategy | None = None

    def select(self) -> BaseStrategy:
        if not self.strategies:
            raise ValueError("no strategies available")
        if random.random() < self.epsilon:
            self.active = random.choice(list(self.strategies.values()))
        else:
            scores = {
                name: self.score_manager.get_score(name) for name in self.strategies
            }
            best = max(scores, key=scores.get)
            self.active = self.strategies[best]
        return self.active
