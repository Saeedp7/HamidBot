from backtest.backtester import Backtester
from strategies.scalper import ScalperBot
from storage.strategy_score_store import StrategyScoreStore


def run() -> None:
    strat = ScalperBot()
    tester = Backtester(strat)
    prices = [1, 2, 3, 2, 4, 5]
    trades = tester.run(prices)

    store = StrategyScoreStore()
    for side, _ in trades:
        result = 1.0 if side == "buy" else -1.0
        store.update_score(strat.name, result)
    store.save()


if __name__ == "__main__":
    run()
