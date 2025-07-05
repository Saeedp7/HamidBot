from collections import defaultdict
from typing import Dict


class ScoreManager:
    """Store and update strategy scores using exponential decay."""

    def __init__(self, decay: float = 0.9) -> None:
        self.decay = decay
        self.scores: Dict[str, float] = defaultdict(float)

    def update_score(self, name: str, reward: float) -> float:
        """Update and return the EMA-weighted score."""
        current = self.scores.get(name, 0.0)
        new_score = current * self.decay + reward
        self.scores[name] = new_score
        return new_score

    def get_score(self, name: str) -> float:
        return self.scores.get(name, 0.0)

    def get_all(self) -> Dict[str, float]:
        return dict(self.scores)
