import json
import numpy as np
from typing import Iterable, List
from gym import spaces


class RLArbitrator:
    """Simple epsilon-greedy Q-learning arbitrator."""

    def __init__(
        self,
        strategies: List[str],
        epsilon: float = 0.1,
        lr: float = 0.2,
        decay: float = 0.99,
        model_path: str = "models/rl_arbitrator.json",
    ) -> None:
        self.strategies = list(strategies)
        self.action_space = spaces.Discrete(len(self.strategies))
        self.epsilon = epsilon
        self.lr = lr
        self.decay = decay
        self.model_path = model_path
        self.q_values = np.zeros(len(self.strategies))
        self.load()

    # ------------------------------------------------------------------
    def load(self) -> None:
        try:
            with open(self.model_path, "r") as f:
                data = json.load(f)
                q = data.get("q_values")
                if isinstance(q, list) and len(q) == len(self.strategies):
                    self.q_values = np.array(q, dtype=float)
        except FileNotFoundError:
            pass

    def save(self) -> None:
        with open(self.model_path, "w") as f:
            json.dump({"q_values": self.q_values.tolist()}, f)

    # ------------------------------------------------------------------
    def select_strategy(
        self, symbol: str, timeframe: str, strategies: Iterable[str] | None = None
    ) -> str:
        """Return a strategy name based on epsilon-greedy policy."""
        if np.random.rand() < self.epsilon:
            action = self.action_space.sample()
        else:
            action = int(np.argmax(self.q_values))
        return self.strategies[action]

    def update_rewards(self, strategy_name: str, reward: float) -> None:
        if strategy_name in self.strategies:
            idx = self.strategies.index(strategy_name)
            self.q_values[idx] += self.lr * (reward - self.q_values[idx])

    def decay_scores(self) -> None:
        self.q_values *= self.decay