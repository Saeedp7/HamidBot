import json
import csv
from concurrent import futures
import grpc
from datetime import datetime
from typing import Dict, Any

from services.grpc import strategy_manager_pb2, strategy_manager_pb2_grpc
from engine.score_manager import ScoreManager
from core.signal import Signal


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
        self.execution_router = ExecutionRouter()
        self.risk_profiles = {
            "default": {"max_risk": 0.02, "preferred_timeframes": ["1m", "5m"]},
        }
        self.active_symbols: Dict[str, str] = {}
        self._load_scores()
        self._log_writer = None

    # ------------------------------------------------------------------
    @staticmethod
    def _pb_to_signal(msg: strategy_manager_pb2.SignalMessage) -> Signal:
        return Signal(
            action=msg.signal_type,
            confidence=msg.confidence,
            sl=msg.sl if msg.sl else None,
            tp=msg.tp if msg.tp else None,
            symbol=msg.symbol,
            timeframe=msg.timeframe,
            timestamp=int(datetime.utcnow().timestamp() * 1000),
            strategy_name=msg.strategy_name,
        )

    @staticmethod
    def _signal_to_pb(signal: Signal, entry_price: float = 0.0) -> strategy_manager_pb2.SignalMessage:
        return strategy_manager_pb2.SignalMessage(
            strategy_name=signal.strategy_name,
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            signal_type=signal.action,
            confidence=signal.confidence,
            entry_price=entry_price,
            sl=signal.sl or 0.0,
            tp=signal.tp or 0.0,
        )

    # ------------------------------------------------------------------
    def _load_scores(self) -> None:
        try:
            with open(self.scores_file, "r") as f:
                data = json.load(f)
            for name, score in data.items():
                self.score_manager.scores[name] = score
        except FileNotFoundError:
            pass

    def _save_scores(self) -> None:
        with open(self.scores_file, "w") as f:
            json.dump(self.score_manager.get_all(), f)

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
        sig = self._pb_to_signal(request)
        print(
            f"Received {sig.strategy_name} signal {sig.action} ({sig.confidence:.2f}) for {sig.symbol}"
        )
        name = sig.strategy_name
        profile = self.risk_profiles.get(name, self.risk_profiles["default"])
        regime_match = 1.0 if sig.timeframe in profile.get("preferred_timeframes", []) else 0.5
        reward = sig.confidence * regime_match
        score = self.score_manager.update_score(name, reward)

        scores = self.score_manager.get_all()
        top_total = sum(scores.values())
        allocation = self.capital * (score / top_total) if top_total else 0.0
        size = allocation / request.entry_price if request.entry_price else 0.0

        # basic safety: prevent duplicate orders per symbol
        last_side = self.active_symbols.get(sig.symbol)
        if last_side and last_side == sig.action:
            message = "duplicate signal ignored"
            return strategy_manager_pb2.ExecutionResponse(message=message)
        self.active_symbols[sig.symbol] = sig.action

        order = {
            "symbol": sig.symbol,
            "side": sig.action,
            "size": size,
            "sl": sig.sl,
            "tp": sig.tp,
        }
        self.execution_router.execute(order)

        writer = self._get_log_writer()
        writer.writerow([
            datetime.utcnow().isoformat(),
            name,
            sig.symbol,
            sig.action,
            f"{size:.6f}",
            sig.sl,
            sig.tp,
        ])
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
