from typing import Iterable, Tuple, Optional

from utils.indicators import atr


class RiskManager:
    """Position sizing using ATR-based stop loss and take profit."""

    def __init__(
        self,
        max_position: float = 1.0,
        risk_percent: float = 0.01,
        atr_period: int = 14,
        sl_mult: float = 1.0,
        tp_mult: float = 2.0,
    ) -> None:
        self.max_position = max_position
        self.risk_percent = risk_percent
        self.atr_period = atr_period
        self.sl_mult = sl_mult
        self.tp_mult = tp_mult

    def size_position(
        self,
        balance: float,
        price: float,
        stop_price: float | None = None,
    ) -> float:
        """Return position size based on risk percent."""
        if stop_price is None:
            qty = balance / price if price > 0 else 0.0
        else:
            risk_per_unit = abs(price - stop_price)
            if risk_per_unit <= 0:
                return 0.0
            qty = (balance * self.risk_percent) / risk_per_unit
        return min(qty, self.max_position)

    def atr_levels(
        self,
        highs: Iterable[float],
        lows: Iterable[float],
        closes: Iterable[float],
    ) -> Optional[Tuple[float, float]]:
        """Calculate stop loss and take profit based on ATR."""
        highs_list = list(highs)
        lows_list = list(lows)
        closes_list = list(closes)
        atr_val = atr(highs_list, lows_list, closes_list, self.atr_period)
        if atr_val is None or not closes_list:
            return None
        price = closes_list[-1]
        sl = price - atr_val * self.sl_mult
        tp = price + atr_val * self.tp_mult
        return sl, tp
