from __future__ import annotations

import pandas as pd
from datetime import datetime, timedelta

from .base import BaseStrategy, Signal


class DCAInvestmentBot(BaseStrategy):
    """Time-based value averaging DCA bot."""

    def __init__(
        self,
        symbol: str,
        timeframe: str = "1d",
        risk_pct: float = 0.05,
        interval_days: int = 7,
    ) -> None:
        super().__init__("DCAInvestmentBot", symbol, timeframe, risk_pct)
        self.interval = timedelta(days=interval_days)
        self.last_buy: datetime | None = None

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        now = df.index[-1] if isinstance(df.index[-1], datetime) else datetime.utcnow()
        if self.last_buy is None or now - self.last_buy >= self.interval:
            self.last_buy = now
            return Signal("buy", 0.3)
        return Signal("hold")
