from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class Signal:
    """Standard trading signal with metadata."""

    action: str  # 'buy', 'sell' or 'hold'
    confidence: float = 0.0
    sl: Optional[float] = None
    tp: Optional[float] = None
    symbol: str = ""
    timeframe: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    strategy_name: str = ""
