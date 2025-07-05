from __future__ import annotations

import math
from typing import Optional
import pandas as pd

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

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        try:
            if not implied_volatility or not delta or not isinstance(df, pd.DataFrame) or df.empty:
                return self._signal("hold")
            row = df.iloc[-1]
            spot = float(row.get("spot", math.nan))
            option_price = float(row.get("option_price", math.nan))
            strike = float(row.get("strike", math.nan))
            t = float(row.get("t", 0.0))
            r = float(row.get("r", 0.0))
            if math.isnan(spot) or math.isnan(option_price) or math.isnan(strike):
                return self._signal("hold")
            try:
                iv = implied_volatility(option_price, spot, strike, t, r, "c")
                d = delta("c", spot, strike, t, r, iv)
            except Exception:
                return self._signal("hold")
            if abs(d) > 0.5:
                return self._signal("buy" if d > 0 else "sell", min(1.0, abs(d)))
            return self._signal("hold")
        except Exception as e:
            print(f"Strategy {self.name} failed: {e}")
            return self._signal("hold")
