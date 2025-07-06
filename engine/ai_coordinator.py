from __future__ import annotations

from typing import Dict, Iterable, Any

from strategies.base import BaseStrategy, Signal
from strategies import load_strategy
from .score_manager import ScoreManager
from core.arbitration_engine import ArbitrationEngine
from ai import RLArbitrator
from storage.strategy_score_store import StrategyScoreStore


class AICoordinator:
    """Coordinate multiple strategies and rank signals."""

    def __init__(
        self,
        strategy_configs: Dict[str, Dict[str, Any]],
        capital: float = 1.0,
        use_rl: bool = False,
    ) -> None:
        self.score_manager = ScoreManager()
        self.score_store = StrategyScoreStore()
        self.capital = capital
        self.use_rl = use_rl
        self.strategies: Dict[str, BaseStrategy] = {}
        for name, cfg in strategy_configs.items():
            cls = load_strategy(cfg.pop("module"))
            self.strategies[name] = cls(**cfg)
        self.arbitration_engine = ArbitrationEngine(self.strategies.keys(), self.score_manager)
        if use_rl:
            try:
                self.arbitration_engine = RLArbitrator(self.strategies.keys())
            except Exception as exc:  # pragma: no cover
                print(f"Falling back to MAB: {exc}")

    def choose_strategy(self, symbol: str, timeframe: str, market_state: Dict[str, Any]) -> BaseStrategy:
        name = self.arbitration_engine.select_strategy(symbol, timeframe, market_state)
        return self.strategies[name]

    def process(self, market_data: Dict[str, Any]) -> Dict[str, Signal]:
        signals: Dict[str, Signal] = {}
        for name, strat in self.strategies.items():
            data = market_data.get(name)
            if data is None:
                continue
            sig = strat.generate_signal(data)
            if isinstance(sig, Signal):
                signals[name] = sig
            else:
                signals[name] = strat._signal(action=str(sig))
            print(
                f"Generated signal {signals[name].action} ({signals[name].confidence:.2f}) for {signals[name].symbol} via {signals[name].strategy_name}"
            )
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
                allocations[name] = (
                    self.capital * (score / total_score) if total_score else 0.0
                )
        return allocations

    # ------------------------------------------------------------------
    def update_performance(self, strategy_name: str, result: float, market_state: Dict[str, Any]) -> None:
        """Update internal reward trackers."""
        self.arbitration_engine.update_rewards(strategy_name, result, market_state.get("symbol", ""), market_state.get("timeframe", ""), market_state)
        self.score_store.update_score(strategy_name, result)
        self.score_store.save()