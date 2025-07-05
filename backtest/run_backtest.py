import os
import importlib
import inspect
import logging


from strategies.base import BaseStrategy
from backtest.data_loader import CSVDataLoader
from backtest.engine import BacktestEngine

logging.basicConfig(level=logging.INFO)


def _discover_strategy_classes() -> list[type[BaseStrategy]]:
    classes: list[type[BaseStrategy]] = []
    for file in os.listdir("strategies"):
        if not file.endswith(".py"):
            continue
        name = file[:-3]
        if name in {"__init__", "base"}:
            continue
        module = importlib.import_module(f"strategies.{name}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if inspect.isclass(obj) and issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                classes.append(obj)
                break
    return classes


def _instantiate_strategies(data: dict) -> list[BaseStrategy]:
    strategies: list[BaseStrategy] = []
    for cls in _discover_strategy_classes():
        sig = inspect.signature(cls.__init__)
        for (symbol, timeframe) in data.keys():
            kwargs = {}
            if "symbol" in sig.parameters:
                kwargs["symbol"] = symbol
            if "timeframe" in sig.parameters:
                kwargs["timeframe"] = timeframe
            try:
                strategies.append(cls(**kwargs))
            except Exception as exc:  # pragma: no cover - ignore bad init
                logging.warning("Could not instantiate %s: %s", cls.__name__, exc)
    return strategies


def run() -> None:
    loader = CSVDataLoader()
    data = loader.load()
    strategies = _instantiate_strategies(data)
    engine = BacktestEngine(data, strategies)
    engine.run()
    for trade in engine.trade_log:
        logging.info(
            "%s triggered %s on %s %s",
            trade.strategy,
            trade.side,
            trade.symbol,
            trade.entry_time,
        )
    engine.save_trade_log()
    summary = engine.summary()
    logging.info("Backtest summary: %s", summary)


if __name__ == "__main__":
    run()
