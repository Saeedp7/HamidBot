import argparse
import pandas as pd
import numpy as np

from core.rl_arbitrator import RLArbitrator
from core.rl_trainer import RLTrainer

# Default strategy universe. Extend this list to train on additional strategies.
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


def load_trade_data(path: str):
    df = pd.read_csv(path)
    transitions = []
    for _, row in df.iterrows():
        reward = 1.0 if row['pnl'] > 0 else -1.0
        state = np.array([row['entry_price']], dtype=np.float32)
        next_state = np.array([row['exit_price']], dtype=np.float32)
        transitions.append((state, 0, reward, next_state, True))
    return transitions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--algo", choices=["dqn", "ppo"], default="dqn")
    parser.add_argument("--log", default="backtest_results/trade_log.csv")
    parser.add_argument(
        "--add",
        action="append",
        default=[],
        metavar="STRATEGY",
        help="append additional strategy name",
    )
    args = parser.parse_args()

    data = load_trade_data(args.log)
    strategies = STRATEGIES + args.add
    arbitrator = RLArbitrator(strategies, state_size=1, algo=args.algo)
    arbitrator.memory.extend(data)
    trainer = RLTrainer(arbitrator)
    trainer.train(epochs=1)
    arbitrator.model.save(f"arbitrator_{args.algo}.zip")


if __name__ == "__main__":
    main()
