from api.broker_api import BrokerAPI
from execution.order_manager import OrderManager
from engine.bot_engine import BotEngine
from risk.risk_manager import RiskManager
from strategies.ema_crossover import EMACrossoverStrategy
from utils.trade_logger import TradeLogger
from data.market_data_collector import MarketDataCollector
from utils.logger import get_logger

class DummyBroker:
    """Very naive broker for demonstration."""

    def market_order(self, symbol: str, side: str, qty: float):
        order = {"side": side, "symbol": symbol, "qty": qty, "price": None}
        print(f"Market order: {order}")
        return order

    def limit_order(self, symbol: str, side: str, qty: float, price: float):
        order = {"side": side, "symbol": symbol, "qty": qty, "price": price}
        print(f"Limit order: {order}")
        return order
    
def _extract_close(candle: object) -> float | None:
    """Best-effort extraction of close price from a candle."""
    if isinstance(candle, dict):
        for key in ("close", "c", "closePrice"):
            if key in candle:
                try:
                    return float(candle[key])
                except (TypeError, ValueError):
                    return None
    if isinstance(candle, (list, tuple)) and len(candle) >= 5:
        try:
            return float(candle[4])
        except (TypeError, ValueError):
            return None
    return None


def run_demo(use_real_api: bool = False, use_collector: bool = True) -> None:
    logger = get_logger("main")
    strategy = EMACrossoverStrategy()
    broker = BrokerAPI() if use_real_api else DummyBroker()
    trade_logger = TradeLogger()
    order_manager = OrderManager(broker, logger=trade_logger)
    risk_manager = RiskManager()
    engine = BotEngine(strategy, order_manager, risk_manager)

    if use_collector:
        collector = MarketDataCollector("BTCUSDT", timeframe="1m", limit=20)
        candles = collector.fetch_ohlcv()
        logger.info("Fetched %d candles", len(candles))
        logger.info("First candle: %s", candles[0] if candles else "no data")
        prices = [c for c in (_extract_close(c) for c in candles) if c is not None]
    else:
        prices = [100, 101, 102, 103, 102, 101, 104, 105, 104]
    for price in prices:
        logger.info("Price %.2f", price)
        engine.on_price_update(price)

    trade_logger.close()


if __name__ == "__main__":
    # Set use_real_api=True to place real orders on Bitunix
    run_demo()
