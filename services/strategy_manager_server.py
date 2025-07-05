import json
import csv
from concurrent import futures
import grpc
from datetime import datetime
from typing import Dict, Any

from services.grpc import strategy_manager_pb2, strategy_manager_pb2_grpc
from engine.score_manager import ScoreManager
from risk.risk_manager import RiskManager
from storage.strategy_score_store import StrategyScoreStore

class ExecutionRouter:
    """Stub execution router that just prints orders."""

    def execute(self, order: Dict[str, Any]) -> None:
        print(f"Executing order: {order}")


class StrategyManager(strategy_manager_pb2_grpc.StrategyManagerServicer):
    def __init__(self, capital: float = 1.0, scores_file: str = "strategy_scores.json", log_file: str = "execution_log.csv") -> None:
        self.capital = capital
        self.scores_file = scores_file
        self.log_file = log_file
        self.score_manager = ScoreManager()
        self.score_store = StrategyScoreStore(scores_file)
        self.execution_router = ExecutionRouter()
        self.risk_manager = RiskManager()
        self.risk_profiles = {
            "default": {"max_risk": 0.02, "preferred_timeframes": ["1m", "5m"]},
        }
        self.active_symbols: Dict[str, str] = {}
        self.daily_loss = 0.0
        self._load_scores()
        self._log_writer = None

    # ------------------------------------------------------------------
    def _load_scores(self) -> None:
        self.score_store.load()
        for name, profile in self.score_store.scores.items():
            self.score_manager.scores[name] = profile.get("avg_return", 0.0)
    def _save_scores(self) -> None:
        for name, value in self.score_manager.get_all().items():
            self.score_store.update_score(name, value)
        self.score_store.save()

    def _get_log_writer(self) -> csv.writer:
        if self._log_writer is None:
            header = ["timestamp", "strategy", "symbol", "side", "size", "sl", "tp"]
            need_header = False
            try:
                need_header = not open(self.log_file).readline()
            except Exception:
                need_header = True
            f = open(self.log_file, "a", newline="")
            self._log_writer = csv.writer(f)
            if need_header:
                self._log_writer.writerow(header)
        return self._log_writer

    # ------------------------------------------------------------------
    def SendSignal(self, request: strategy_manager_pb2.SignalMessage, context: grpc.ServicerContext) -> strategy_manager_pb2.ExecutionResponse:
        name = request.strategy_name
        profile = self.risk_profiles.get(name, self.risk_profiles["default"])
        regime_match = 1.0 if request.timeframe in profile.get("preferred_timeframes", []) else 0.5
        reward = request.confidence * regime_match
        score = self.score_manager.update_score(name, reward)

        scores = self.score_manager.get_all()
        top_total = sum(scores.values())
        allocation = self.capital * (score / top_total) if top_total else 0.0
        volatility = abs(request.entry_price - request.sl) if request.sl else request.entry_price * 0.01
        qty = self.risk_manager.compute_position_size(request.confidence, volatility, allocation)
        leverage = self.risk_manager.adjust_leverage(name)
        size = qty * leverage

        # risk check: max drawdown
        if not self.risk_manager.enforce_max_drawdown(self.daily_loss, None):
            return strategy_manager_pb2.ExecutionResponse(message="drawdown limit")

        # basic safety: prevent duplicate orders per symbol
        last_side = self.active_symbols.get(request.symbol)
        if last_side and last_side == request.signal_type:
            message = "duplicate signal ignored"
            return strategy_manager_pb2.ExecutionResponse(message=message)
        self.active_symbols[request.symbol] = request.signal_type

        order = {
            "symbol": request.symbol,
            "side": request.signal_type,
            "size": size,
            "sl": request.sl,
            "tp": request.tp,
        }
        self.execution_router.execute(order)
        self.daily_loss += -reward if reward < 0 else 0.0

        writer = self._get_log_writer()
        writer.writerow([
            datetime.utcnow().isoformat(),
            name,
            request.symbol,
            request.signal_type,
            f"{size:.6f}",
            request.sl,
            request.tp,
        ])
        self.score_store.update_score(name, reward)
        self._save_scores()
        exec_order = strategy_manager_pb2.ExecutionOrder(**order)
        return strategy_manager_pb2.ExecutionResponse(orders=[exec_order], message="ok")


def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    strategy_manager_pb2_grpc.add_StrategyManagerServicer_to_server(StrategyManager(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"StrategyManager gRPC server running on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
