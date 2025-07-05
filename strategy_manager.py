from concurrent import futures
import grpc
from proto import strategy_pb2, strategy_pb2_grpc
from ai.scoring_engine import ScoringEngine
from execution.order_router import OrderRouter


class StrategyManager(strategy_pb2_grpc.StrategyManagerServicer):
    """gRPC server receiving strategy signals and routing orders."""

    def __init__(self, capital: float = 10000.0) -> None:
        self.scorer = ScoringEngine()
        self.router = OrderRouter()
        self.capital = capital

    def evaluate_signal(self, signal) -> float:
        return self.scorer.evaluate_signal(signal)

    def route_order(self, order: dict) -> str:
        return self.router.route_order(order)

    def SendSignal(
        self,
        request: strategy_pb2.SignalMessage,
        context: grpc.ServicerContext,
    ) -> strategy_pb2.ExecutionResponse:
        print(f"Received signal: {request}")
        score = self.evaluate_signal(request)
        allocation = self.capital * score
        order = {
            "symbol": request.symbol,
            "action": request.action,
            "size": allocation / request.entry_price if request.entry_price else 0.0,
            "entry_price": request.entry_price,
            "stop_loss": request.stop_loss,
            "take_profit": request.take_profit,
        }
        status = self.route_order(order)
        print(f"Score: {score:.2f}, allocated capital: {allocation:.2f}")
        return strategy_pb2.ExecutionResponse(
            status=status, score=score, capital=allocation, message="order processed"
        )


def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    strategy_pb2_grpc.add_StrategyManagerServicer_to_server(StrategyManager(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"StrategyManager listening on port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
