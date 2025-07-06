from __future__ import annotations

from typing import Dict, Iterable, Any

from strategies.base import BaseStrategy, Signal
from strategies import load_strategy
from .score_manager import ScoreManager
from ai.arbitration_engine import ArbitrationEngine
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
        self.arbitration_engine = ArbitrationEngine()
        self.capital = capital
        self.use_rl = use_rl
        self.strategies: Dict[str, BaseStrategy] = {}
        for name, cfg in strategy_configs.items():
            cls = load_strategy(cfg.pop("module"))
            self.strategies[name] = cls(**cfg)
        if use_rl:
            try:
                self.arbitration_engine = RLArbitrator(self.strategies.keys())
            except Exception as exc:  # pragma: no cover
                print(f"Falling back to MAB: {exc}")

    def choose_strategy(
        self, symbol: str, timeframe: str, context: Dict[str, Any] | None = None
    ) -> BaseStrategy:
        if self.use_rl and context is not None:
            name = self.arbitration_engine.select_strategy(context)
        else:
            name = self.arbitration_engine.select_strategy(
                symbol, timeframe, self.strategies.keys()
            )
        name = self.arbitration_engine.select_strategy(symbol, timeframe, self.strategies.keys())
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
    def update_performance(
        self,
        strategy_name: str,
        result: float,
        context: Dict[str, Any] | None = None,
        next_context: Dict[str, Any] | None = None,
        done: bool = False,
    ) -> None:
        """Update internal reward trackers."""
        if self.use_rl and context is not None and next_context is not None:
            self.arbitration_engine.update(result, next_context, done)
        else:
            self.arbitration_engine.update_rewards(strategy_name, result)
        self.score_store.update_score(strategy_name, result)
        self.score_store.save()