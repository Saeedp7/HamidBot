import numpy as np


def encode_state(symbol: str, timeframe: str, market_data: dict, strategy_scores: dict) -> np.ndarray:
    """Return a normalized state vector for the RL agent."""
    volatility_5 = market_data.get("volatility_5", 0.0)
    volatility_20 = market_data.get("volatility_20", 0.0)
    recent_return = market_data.get("recent_return", 0.0)
    drawdown = market_data.get("drawdown", 0.0)
    hit_ratio = strategy_scores.get("strategy_hit_ratio", 0.0)
    confidence_avg = strategy_scores.get("confidence_average", 0.0)
    symbol_id = (hash(symbol) % 1000) / 1000.0
    timeframe_id = (hash(timeframe) % 1000) / 1000.0

    state = np.array([
        volatility_5,
        volatility_20,
        recent_return,
        drawdown,
        hit_ratio,
        confidence_avg,
        symbol_id,
        timeframe_id,
    ], dtype=np.float32)

    # basic normalization using tanh to keep values bounded
    return np.tanh(state)