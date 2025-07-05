from __future__ import annotations

from typing import Iterable
import pandas as pd

from .base import BaseStrategy, Signal

try:
    from transformers import pipeline
    _sentiment = pipeline("sentiment-analysis")
except Exception:  # pragma: no cover - optional dependency
    _sentiment = None


class NewsSentimentBot(BaseStrategy):
    """Analyze real-time news sentiment."""

    def __init__(self, symbol: str, timeframe: str = "1h", risk_pct: float = 0.01) -> None:
        super().__init__("NewsSentimentBot", symbol, timeframe, risk_pct)

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        if not _sentiment or df.empty or "text" not in df.columns:
            return self._signal("hold")
        texts: Iterable[str] = df["text"].astype(str).tolist()
        joined = "\n".join(texts)
        result = _sentiment(joined[:512])[0]
        label = result.get("label", "neutral").lower()
        score = float(result.get("score", 0))
        if label == "positive" and score > 0.6:
            return self._signal("buy", score)
        if label == "negative" and score > 0.6:
            return self._signal("sell", score)
        return self._signal("hold")
