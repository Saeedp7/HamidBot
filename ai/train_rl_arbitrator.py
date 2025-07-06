import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.rl_arbitrator import RLArbitrator
from core.rl_trainer import RLTrainer

if __name__ == "__main__":
    strategies = ["ScalperBot", "SwingBot", "GridBot", "DCAInvestmentBot"]
    state_dim = 10
    agent = RLArbitrator(strategies=strategies, state_dim=state_dim)
    trainer = RLTrainer(arbitrator=agent)

    for _ in range(1000):
        state = np.random.rand(state_dim).astype(np.float32)
        action_idx = agent.model.predict(state, deterministic=True)[0]
        reward = np.random.normal(loc=1.0 if action_idx == 1 else 0.2)  # Fake reward logic
        next_state = np.random.rand(state_dim).astype(np.float32)

        trainer.record_transition(
            state=state,
            action=action_idx,
            reward=reward,
            next_state=next_state
        )

    print("✅ RL training completed and model saved.")
