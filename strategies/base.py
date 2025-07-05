from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Signal:
    """Standard representation for strategy signals."""

    action: str  # 'buy', 'sell' or 'hold'
    confidence: float = 0.0
    sl: Optional[float] = None
    tp: Optional[float] = None


class BaseStrategy:
    """Base class for trading strategies."""

    def __init__(self, name: str = "Base", symbol: str = "", timeframe: str = "", risk_pct: float = 0.01) -> None:
        self.name = name
        self.symbol = symbol
        self.timeframe = timeframe
        self.risk_pct = risk_pct

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
