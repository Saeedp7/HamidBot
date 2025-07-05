from typing import Any, List

from api.config import Config
from api.open_api_http_future_public import OpenApiHttpFuturePublic
from utils.logger import get_logger


class MarketDataCollector:
    """Fetch OHLCV data from Bitunix using the HTTP API."""

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1m",
        limit: int = 500,
        config_path: str = "api/config.yaml",
    ) -> None:
        self.client = OpenApiHttpFuturePublic(Config(config_path))
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.logger = get_logger(self.__class__.__name__)

    def fetch_ohlcv(self) -> List[Any]:
        """Return raw OHLCV candles."""
        self.logger.info(
            "Fetching OHLCV for %s timeframe %s limit %d",
            self.symbol,
            self.timeframe,
            self.limit,
        )
        data = self.client.get_kline(self.symbol, self.timeframe, self.limit)
        self.logger.info("Fetched %d candles", len(data))
        return data
