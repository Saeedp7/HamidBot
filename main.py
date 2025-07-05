from api.broker_api import BrokerAPI
from execution.order_manager import OrderManager
from engine.bot_engine import BotEngine
from risk.risk_manager import RiskManager
from strategies.ema_crossover import EMACrossoverStrategy
from strategies.mean_reversion import MeanReversionStrategy
from engine.score_manager import ScoreManager
from engine.strategy_selector import StrategySelector
from engine.regime_detector import RegimeDetector
from analysis.replay_engine import ReplayEngine
from utils.trade_logger import TradeLogger
from data.market_data_collector import MarketDataCollector
from utils.logger import get_logger
from utils.telegram_notifier import send_telegram_alert
from dashboard.dashboard import metrics, start_dashboard
import schedule
import threading
import os
import time

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

def _extract_hlc(candle: object) -> dict[str, float] | None:
    """Best-effort extraction of high/low/close data from a candle."""
    if isinstance(candle, dict):
        try:
            return {
                "high": float(candle.get("high", candle.get("h"))),
                "low": float(candle.get("low", candle.get("l"))),
                "close": float(candle.get("close", candle.get("c", candle.get("closePrice")))),
            }
        except (TypeError, ValueError):
            return None
    if isinstance(candle, (list, tuple)) and len(candle) >= 5:
        try:
            return {"high": float(candle[2]), "low": float(candle[3]), "close": float(candle[4])}
        except (TypeError, ValueError):
            return None
    return None

def _extract_close(candle: object) -> float | None:
    data = _extract_hlc(candle)
    return data["close"] if data else None


def run_demo(use_real_api: bool = False, use_collector: bool = True) -> None:
    logger = get_logger("main")

    strategies = {
        "trend": EMACrossoverStrategy(),
        "mean": MeanReversionStrategy(),
    }
    score_manager = ScoreManager()
    selector = StrategySelector(strategies, score_manager, epsilon=0.2)
    regime_detector = RegimeDetector()
    broker = BrokerAPI() if use_real_api else DummyBroker()
    trade_logger = TradeLogger()
    order_manager = OrderManager(broker, logger=trade_logger)
    risk_manager = RiskManager()

    if use_collector:
        collector = MarketDataCollector("ETHUSDT", timeframe="5m", limit=20)
        candles = collector.fetch_ohlcv()
        logger.info("Fetched %d candles", len(candles))
        logger.info("First candle: %s", candles[0] if candles else "no data")
    else:
        candles = [[0, p, p, p, p, 1] for p in [100, 101, 102, 103, 102, 101, 104, 105, 104]]

    prices = []
    for candle in candles:
        data = _extract_hlc(candle)
        if not data:
            continue
        regime_detector.on_data(data)
        prices.append(data["close"])

    # Score strategies using historical replay
    scores = ReplayEngine(selector).run(prices)
    logger.info("Strategy scores: %s", scores)

    # Pick the best strategy based on scores
    active_strategy = selector.select()
    logger.info("Selected strategy: %s", active_strategy.name)

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notifier = None
    if token and chat_id:
        notifier = send_telegram_alert(metrics)
        notifier.schedule_summary()

    dashboard_thread = threading.Thread(target=start_dashboard, daemon=True)
    dashboard_thread.start()

    engine = BotEngine(active_strategy, order_manager, risk_manager, metrics, notifier)
    for price in prices:
        logger.info("Price %.2f (%s)", price, regime_detector.detect())
        engine.on_price_update(price)
        schedule.run_pending()
        time.sleep(0.1)

    trade_logger.close()


if __name__ == "__main__":
    # Set use_real_api=True to place real orders on Bitunix
    run_demo()
