from __future__ import annotations

import math
from typing import Optional

from .base import BaseStrategy, Signal

try:
    from py_vollib.black_scholes.implied_volatility import implied_volatility
    from py_vollib.black_scholes.greeks.analytical import delta
except Exception:  # pragma: no cover - optional dependency
    implied_volatility = None
    delta = None


class OptionsHedgerBot(BaseStrategy):
    """Calculate option greeks and hedge using spot price."""

    def __init__(self, symbol: str, timeframe: str = "1h", risk_pct: float = 0.02) -> None:
        super().__init__("OptionsHedgerBot", symbol, timeframe, risk_pct)

    def generate_signal(self, data: dict) -> Signal:
        if not implied_volatility or not delta:
            return Signal("hold")
        spot = data.get("spot")
        option_price = data.get("option_price")
        strike = data.get("strike")
        t = data.get("t", 0.0)
        r = data.get("r", 0.0)
        if not all(v is not None for v in [spot, option_price, strike]):
            return Signal("hold")
        try:
            iv = implied_volatility(option_price, spot, strike, t, r, "c")
            d = delta("c", spot, strike, t, r, iv)
        except Exception:
            return Signal("hold")
        if abs(d) > 0.5:
            return Signal("buy" if d > 0 else "sell", min(1.0, abs(d)))
        return Signal("hold")
