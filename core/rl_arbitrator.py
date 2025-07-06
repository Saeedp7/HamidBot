from __future__ import annotations

from typing import Iterable, List
import numpy as np
import gymnasium as gym
from stable_baselines3 import DQN, PPO


class ArbitrationEnv(gym.Env):
    """Simple environment to satisfy RL algorithms."""

    def __init__(self, n_actions: int, state_size: int = 1) -> None:
        super().__init__()
        self.action_space = gym.spaces.Discrete(n_actions)
        self.observation_space = gym.spaces.Box(
            low=-np.inf, high=np.inf, shape=(state_size,), dtype=np.float32
        )
        self.state = np.zeros(state_size, dtype=np.float32)

    def reset(self, *, seed=None, options=None):
        return self.state, {}

    def step(self, action):  # pragma: no cover - dummy env
        return self.state, 0.0, True, False, {}


class RLArbitrator:
    """Strategy selector powered by reinforcement learning."""

    def __init__(self, strategies: Iterable[str], state_size: int = 1, algo: str = "dqn") -> None:
        self.strategies = list(strategies)
        self.env = ArbitrationEnv(len(self.strategies), state_size)
        self.algo = algo
        if algo == "ppo":
            self.model = PPO("MlpPolicy", self.env, verbose=0)
        else:
            self.model = DQN("MlpPolicy", self.env, verbose=0)
        self.last_state: np.ndarray | None = None
        self.last_action: int | None = None
        self.memory: List[tuple] = []

    # --------------------------------------------------------------
    def add_strategy(self, name: str) -> None:
        """Add a new strategy to the action space."""
        self.strategies.append(name)
        self.env.action_space = gym.spaces.Discrete(len(self.strategies))
        self.model.set_env(self.env)

    # --------------------------------------------------------------
    def select_strategy(self, symbol: str, timeframe: str, strategies: Iterable[str], state: Iterable[float] | None = None) -> str:
        obs = np.array(state if state is not None else [0.0], dtype=np.float32)
        action, _ = self.model.predict(obs, deterministic=True)
        self.last_state = obs
        self.last_action = int(action)
        # fall back if action out of range
        idx = self.last_action % len(self.strategies)
        return self.strategies[idx]

    # --------------------------------------------------------------
    def update(self, reward: float, next_state: Iterable[float], done: bool = True) -> None:
        if self.last_state is None or self.last_action is None:
            return
        next_obs = np.array(next_state, dtype=np.float32)
        self.memory.append((self.last_state, self.last_action, reward, next_obs, done))