from __future__ import annotations

from typing import Iterable
import numpy as np
import gymnasium as gym

from stable_baselines3.common.base_class import BaseAlgorithm
from stable_baselines3 import PPO, DQN


class ReplayEnv(gym.Env):
    """Environment that replays recorded transitions."""

    def __init__(self, transitions: Iterable[tuple], obs_space: gym.Space, act_space: gym.Space) -> None:
        super().__init__()
        self.transitions = list(transitions)
        self.observation_space = obs_space
        self.action_space = act_space
        self.idx = 0

    def reset(self, *, seed=None, options=None):
        self.idx = 0
        return self.transitions[0][0], {}

    def step(self, action):  # pragma: no cover - simple replay
        s, a, r, n, d = self.transitions[self.idx]
        self.idx += 1
        return n, r, d, False, {}


class RLTrainer:
    """Train RL arbitrator from recorded transitions."""

    def __init__(self, arbitrator, batch_size: int = 32) -> None:
        self.arbitrator = arbitrator
        self.batch_size = batch_size

    # --------------------------------------------------------------
    def train(self, epochs: int = 1) -> None:
        if not self.arbitrator.memory:
            return
        env = ReplayEnv(
            self.arbitrator.memory,
            self.arbitrator.env.observation_space,
            self.arbitrator.env.action_space,
        )
        self.arbitrator.model.set_env(env)
        steps = len(self.arbitrator.memory) * epochs
        if isinstance(self.arbitrator.model, PPO):
            self.arbitrator.model.learn(total_timesteps=steps)
        else:
            self.arbitrator.model.learn(total_timesteps=steps)
        self.arbitrator.memory.clear()
        env.close()
