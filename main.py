from execution.broker_api import BrokerAPI
from execution.order_manager import OrderManager
from engine.bot_engine import BotEngine
from risk.risk_manager import RiskManager
from strategies.ema_crossover import EMACrossoverStrategy
from execution.bitunix_broker import BitunixBroker
from data.market_data_collector import MarketDataCollector
from utils.logger import get_logger

class DummyBroker(BrokerAPI):
    """A very naive broker implementation for demonstration."""

    def buy(self, symbol: str, qty: float, price: float | None = None):
        order = {"side": "BUY", "symbol": symbol, "qty": qty, "price": price}
        print(f"Buying: {order}")
        return order

    def sell(self, symbol: str, qty: float, price: float | None = None):
        order = {"side": "SELL", "symbol": symbol, "qty": qty, "price": price}
        print(f"Selling: {order}")
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
    broker = BitunixBroker() if use_real_api else DummyBroker()
    order_manager = OrderManager(broker)
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


if __name__ == "__main__":
    # Set use_real_api=True to place real orders using Bitunix
    run_demo()
