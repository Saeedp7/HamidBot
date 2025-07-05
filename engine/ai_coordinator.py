from __future__ import annotations

from typing import Dict, Iterable, Any

from strategies.base import BaseStrategy, Signal
from strategies import load_strategy
from .score_manager import ScoreManager
from ai.arbitration_engine import ArbitrationEngine
from storage.strategy_score_store import StrategyScoreStore


class AICoordinator:
    """Coordinate multiple strategies and rank signals."""

    def __init__(self, strategy_configs: Dict[str, Dict[str, Any]], capital: float = 1.0) -> None:
        self.score_manager = ScoreManager()
        self.score_store = StrategyScoreStore()
        self.arbitration_engine = ArbitrationEngine()
        self.capital = capital
        self.strategies: Dict[str, BaseStrategy] = {}
        for name, cfg in strategy_configs.items():
            cls = load_strategy(cfg.pop("module"))
            self.strategies[name] = cls(**cfg)

    def choose_strategy(self, symbol: str, timeframe: str) -> BaseStrategy:
        name = self.arbitration_engine.select_strategy(symbol, timeframe, self.strategies.keys())
        return self.strategies[name]

    def process(self, market_data: Dict[str, Any]) -> Dict[str, Signal]:
        signals: Dict[str, Signal] = {}
        for name, strat in self.strategies.items():
            data = market_data.get(name)
            if data is None:
                continue
            sig = strat.generate_signal(data)
            signals[name] = sig if isinstance(sig, Signal) else Signal(str(sig))
        return signals

    def allocate(self, signals: Dict[str, Signal]) -> Dict[str, float]:
        allocations = {}
        total_score = 0.0
        for name, sig in signals.items():
            score = self.score_manager.get_score(name)
            if sig.action != "hold":
                total_score += score
        for name, sig in signals.items():
            if sig.action == "hold":
                allocations[name] = 0.0
            else:
                score = self.score_manager.get_score(name)
                allocations[name] = self.capital * (score / total_score) if total_score else 0.0
        return allocations

    # ------------------------------------------------------------------
    def update_performance(self, strategy_name: str, result: float) -> None:
        """Update internal reward trackers."""
        self.arbitration_engine.update_rewards(strategy_name, result)
        self.score_store.update_score(strategy_name, result)
        self.score_store.save()
