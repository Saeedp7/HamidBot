import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class StrategyScoreStore:
    """Persist strategy performance statistics to JSON."""

    def __init__(self, path: str = "strategy_scores.json") -> None:
        self.path = Path(path)
        self.scores: Dict[str, Dict[str, Any]] = {}
        self.load()

    # ------------------------------------------------------------------
    def load(self) -> None:
        try:
            with open(self.path, "r") as f:
                self.scores = json.load(f)
        except FileNotFoundError:
            self.scores = {}

    def save(self) -> None:
        with open(self.path, "w") as f:
            json.dump(self.scores, f)

    # ------------------------------------------------------------------
    def get_score(self, strategy_name: str) -> Dict[str, Any] | None:
        return self.scores.get(strategy_name)

    def update_score(self, strategy_name: str, result: float) -> Dict[str, Any]:
        profile = self.scores.get(
            strategy_name,
            {
                "strategy_name": strategy_name,
                "hit_rate": 0.0,
                "avg_return": 0.0,
                "recent_outcomes": [],
                "last_updated": "",
            },
        )
        outcomes = profile["recent_outcomes"]
        outcomes.append(result)
        if len(outcomes) > 100:
            outcomes.pop(0)
        wins = sum(1 for r in outcomes if r > 0)
        profile["hit_rate"] = wins / len(outcomes)
        profile["avg_return"] = sum(outcomes) / len(outcomes)
        profile["recent_outcomes"] = outcomes
        profile["last_updated"] = datetime.utcnow().isoformat()
        self.scores[strategy_name] = profile
        return profile
