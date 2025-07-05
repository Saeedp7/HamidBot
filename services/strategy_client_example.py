import grpc
from services.grpc import strategy_manager_pb2, strategy_manager_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = strategy_manager_pb2_grpc.StrategyManagerStub(channel)
    msg = strategy_manager_pb2.SignalMessage(
        strategy_name='demo_strategy',
        symbol='BTCUSDT',
        timeframe='1m',
        signal_type='buy',
        confidence=0.8,
        entry_price=30000.0,
        sl=29900.0,
        tp=30500.0,
    )
    response = stub.SendSignal(msg)
    print('Response:', response)


if __name__ == '__main__':
    run()
