import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.rl_arbitrator import RLArbitrator


STRATEGIES = [
    "ScalperBot",
    "SwingBot",
    "ArbitrageBot",
    "GridBot",
    "NewsSentimentBot",
    "MeanReversionBot",
    "BreakoutBot",
    "LiquiditySweepBot",
    "DCAInvestmentBot",
    "OptionsHedgerBot",
]


def main(episodes: int = 1000) -> None:
    os.makedirs("models", exist_ok=True)
    arbitrator = RLArbitrator(STRATEGIES)
    for _ in range(episodes):
        name = arbitrator.select_strategy("BTCUSDT", "1h")
        reward = random.uniform(-1, 1)
        arbitrator.update_rewards(name, reward)
        arbitrator.decay_scores()
    arbitrator.save()
    print("Training complete. Model saved to", arbitrator.model_path)


if __name__ == "__main__":
    main()