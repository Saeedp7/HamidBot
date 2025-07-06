from __future__ import annotations

import os
from typing import List

import numpy as np
from stable_baselines3.common.buffers import ReplayBuffer


class RLTrainer:
    """Simple replay buffer trainer for RLArbitrator."""

    def __init__(
        self,
        arbitrator,
        save_path: str = "models/rl_arbitrator.zip",
        buffer_size: int = 10000,
        batch_size: int = 32,
        train_freq: int = 10,
    ) -> None:
        self.arbitrator = arbitrator
        self.save_path = save_path
        self.batch_size = batch_size
        self.train_freq = train_freq
        self.env = arbitrator.env
        self.replay_buffer = ReplayBuffer(
            buffer_size,
            self.env.observation_space,
            self.env.action_space,
            device=arbitrator.model.device,
            optimize_memory_usage=False,
            handle_timeout_termination=False,
        )
        self.steps = 0

    def record_transition(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
    ) -> None:
        self.replay_buffer.add(
            state,
            next_state,
            np.array([action]),
            np.array([reward], dtype=np.float32),
            np.array([0.0], dtype=np.float32),
            [{}],
        )
        self.steps += 1
        if self.steps % self.train_freq == 0:
            self._train()

    def _train(self) -> None:
        if self.replay_buffer.size() < self.batch_size:
            return
        self.arbitrator.model.replay_buffer = self.replay_buffer
        self.arbitrator.model.learn(
            total_timesteps=self.batch_size,
            reset_num_timesteps=False,
            log_interval=None
        )
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        self.arbitrator.model.save(self.save_path)