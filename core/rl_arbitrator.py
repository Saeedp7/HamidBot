from __future__ import annotations

import os
from typing import Iterable

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import DQN


class _DummyEnv(gym.Env):
    """Minimal env to satisfy Stable Baselines"""

    def __init__(self, state_dim: int, n_actions: int) -> None:
        super().__init__()
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(state_dim,), dtype=np.float32)
        self.action_space = spaces.Discrete(n_actions)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        return np.zeros(self.observation_space.shape, dtype=np.float32), {}

    def step(self, action):
        obs = np.zeros(self.observation_space.shape, dtype=np.float32)
        return obs, 0.0, False, False, {}


class RLArbitrator:
    """Wrapper around a DQN agent for strategy selection."""

    def __init__(
        self,
        strategies: Iterable[str],
        state_dim: int,
        model_path: str = "models/rl_arbitrator.zip",
        trainer: "RLTrainer | None" = None,
    ) -> None:
        self.strategy_names = list(strategies)
        self.state_dim = state_dim
        self.model_path = model_path
        self.trainer = trainer
        self.env = _DummyEnv(state_dim, len(self.strategy_names))
        if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
            self.model = DQN.load(model_path, env=self.env)
        else:
            self.model = DQN("MlpPolicy", self.env, verbose=0)
        self.name_from_action = {i: n for i, n in enumerate(self.strategy_names)}
        self.last_state: np.ndarray | None = None
        self.last_action: int | None = None

    def select_strategy(self, state: np.ndarray) -> str:
        action, _ = self.model.predict(state, deterministic=True)
        self.last_state = state
        self.last_action = int(action)
        return self.name_from_action[self.last_action]

    def update(self, reward: float, next_state: np.ndarray) -> None:
        if self.last_state is None or self.last_action is None:
            return
        if self.trainer is not None:
            self.trainer.record_transition(self.last_state, self.last_action, reward, next_state)