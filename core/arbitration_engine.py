from __future__ import annotations

from typing import Iterable, Dict, Any

from engine.score_manager import ScoreManager
from .state_encoder import encode_state
from .rl_arbitrator import RLArbitrator
from .rl_trainer import RLTrainer


class ArbitrationEngine:
    """RL-powered strategy arbitration."""

    def __init__(self, strategies: Iterable[str], score_manager: ScoreManager) -> None:
        self.score_manager = score_manager
        self.arbitrator = RLArbitrator(strategies, state_dim=8)
        self.trainer = RLTrainer(self.arbitrator)
        # link arbitrator to trainer
        self.arbitrator.trainer = self.trainer

    def select_strategy(self, symbol: str, timeframe: str, market_data: Dict[str, Any]) -> str:
        scores = {name: self.score_manager.get_score(name) for name in market_data.keys()}
        state = encode_state(symbol, timeframe, market_data, scores)
        try:
            return self.arbitrator.select_strategy(state)
        except Exception:
            return max(scores, key=scores.get)

    def update_rewards(
        self,
        strategy_name: str,
        reward: float,
        symbol: str,
        timeframe: str,
        market_data: Dict[str, Any],
    ) -> None:
        scores = {name: self.score_manager.get_score(name) for name in market_data.keys()}
        next_state = encode_state(symbol, timeframe, market_data, scores)
        try:
            self.arbitrator.update(reward, next_state)
        except Exception:
            pass