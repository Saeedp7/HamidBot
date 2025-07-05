import grpc
from proto import strategy_pb2, strategy_pb2_grpc
from datetime import datetime


def run():
    channel = grpc.insecure_channel("localhost:50051")
    stub = strategy_pb2_grpc.StrategyManagerStub(channel)
    msg = strategy_pb2.SignalMessage(
        strategy_name="demo",
        symbol="BTCUSDT",
        timeframe="1m",
        action="buy",
        confidence=0.8,
        entry_price=30000.0,
        stop_loss=29900.0,
        take_profit=30500.0,
        timestamp=int(datetime.utcnow().timestamp()),
    )
    response = stub.SendSignal(msg)
    print("Execution response:", response)


if __name__ == "__main__":
    run()
