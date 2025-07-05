from typing import List


class RegimeDetector:
    """Detects market regime based on price data."""

    def detect(self, prices: List[float]) -> str:
        if len(prices) < 2:
            return "unknown"
        return "trend" if prices[-1] > prices[0] else "mean_revert"
