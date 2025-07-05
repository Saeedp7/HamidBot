from __future__ import annotations

from typing import Optional
from core.signal import Signal
import time


class BaseStrategy:
    """Base class for trading strategies."""

    def __init__(self, name: str = "Base", symbol: str = "", timeframe: str = "", risk_pct: float = 0.01) -> None:
        self.name = name
        self.symbol = symbol
        self.timeframe = timeframe
        self.risk_pct = risk_pct

    # --------------------------------------------------------------
    def _signal(
        self,
        action: str = "hold",
        confidence: float = 0.0,
        sl: Optional[float] = None,
        tp: Optional[float] = None,
    ) -> Signal:
        return Signal(
            action=action,
            confidence=confidence,
            sl=sl,
            tp=tp,
            symbol=self.symbol,
            timeframe=self.timeframe,
            timestamp=int(time.time() * 1000),
            strategy_name=self.name,
        )

    def on_data(self, price: float) -> None:
        """Receive new price data."""
        raise NotImplementedError

    def generate_signal(self, df=None):
        """Return :class:`Signal` or string based on latest data."""
        raise NotImplementedError

    def should_buy(self) -> bool:
        """Return True if a buy signal is generated."""
        sig = self.generate_signal()
        if isinstance(sig, Signal):
            return sig.action == "buy"
        return sig == "buy"

    def should_sell(self) -> bool:
        """Return True if a sell signal is generated."""
        sig = self.generate_signal()
        if isinstance(sig, Signal):
            return sig.action == "sell"
        return sig == "sell"
