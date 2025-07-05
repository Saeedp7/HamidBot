from __future__ import annotations

from strategies.scalper import ScalperBot
from strategies.swing import SwingBot
from backtest.data_loader import CSVDataLoader
from backtest.engine import BacktestEngine


def main() -> None:
    loader = CSVDataLoader("data/processed")
    data = loader.load()
    strategies = [
        ScalperBot(symbol="BTCUSDT", timeframe="1m", risk_pct=0.005),
        SwingBot(symbol="BTCUSDT", timeframe="4h", risk_pct=0.02),
        ScalperBot(symbol="ETHUSDT", timeframe="1m", risk_pct=0.005),
        SwingBot(symbol="ETHUSDT", timeframe="4h", risk_pct=0.02),
    ]
    engine = BacktestEngine(
        data,
        strategies,
        {
            "initial_balance": 10000,
            "slippage_pct": 0.001,
            "fee_pct": 0.001,
        },
    )
    engine.run()
    engine.save_trade_log()
    summary = engine.summary()
    per_strategy = engine.per_strategy_metrics()
    print("Summary:", summary)
    sorted_strats = sorted(per_strategy.items(), key=lambda x: x[1]["net_return"], reverse=True)
    print("Top strategies:")
    for name, stats in sorted_strats[:3]:
        print(name, stats)


if __name__ == "__main__":
    main()