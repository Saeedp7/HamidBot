import random
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np

try:
    from stable_baselines3 import DQN
except Exception as e:  # pragma: no cover - optional dependency may not be installed
    DQN = None  # type: ignore
    IMPORT_ERROR = e
else:
    IMPORT_ERROR = None


class RLArbitrator:
    """Deep RL based strategy selector using DQN."""

    def __init__(
        self,
        strategy_names: Iterable[str],
        model_path: str | Path = "models/rl_arbitrator.zip",
        epsilon: float = 0.1,
        buffer_size: int = 10_000,
    ) -> None:
        self.strategy_names: List[str] = list(strategy_names)
        self.epsilon = epsilon
        self.model_path = Path(model_path)
        self.last_state: np.ndarray | None = None
        self.last_action: int | None = None
        self.rewards: List[float] = []

        self.model: DQN | None = None
        self.replay_buffer: object | None = None
        if DQN is None:
            print(f"RLArbitrator disabled, import error: {IMPORT_ERROR}")
            return
        obs_dim = len(self._state_to_vector({}))
        self.model = DQN(
            "MlpPolicy",
            FakeEnv(obs_dim, len(self.strategy_names)),
            verbose=0,
            buffer_size=buffer_size,
        )
        self.replay_buffer = self.model.replay_buffer
        if self.model_path.exists():
            try:
                self.model = DQN.load(str(self.model_path))
            except Exception as exc:  # pragma: no cover
                print(f"Failed to load RL model: {exc}")

    # ------------------------------------------------------------------
    def _state_to_vector(self, state: Dict[str, float]) -> np.ndarray:
        if not state:
            return np.zeros(7, dtype=np.float32)
        keys = [
            "volatility",
            "trend_strength",
            "drawdown",
            "recent_return",
            "capital",
            "time_step",
            "strategy_idx",
        ]
        return np.array([float(state.get(k, 0.0)) for k in keys], dtype=np.float32)

    # ------------------------------------------------------------------
    def select_strategy(self, context: Dict[str, float]) -> str:
        if self.model is None:
            return random.choice(self.strategy_names)
        state_vec = self._state_to_vector(context)
        if random.random() < self.epsilon:
            action = random.randrange(len(self.strategy_names))
        else:
            action, _ = self.model.predict(state_vec, deterministic=True)
        self.last_state = state_vec
        self.last_action = int(action)
        return self.strategy_names[int(action)]

    # ------------------------------------------------------------------
    def update(
        self, reward: float, next_context: Dict[str, float], done: bool = False
    ) -> None:
        if self.model is None or self.replay_buffer is None:
            return
        next_state = self._state_to_vector(next_context)
        if self.last_state is None or self.last_action is None:
            return
        self.replay_buffer.add(
            self.last_state,
            next_state,
            [self.last_action],
            [reward],
            [float(done)],
        )
        self.rewards.append(reward)

    # ------------------------------------------------------------------
    def train(self, timesteps: int = 1000) -> None:
        if self.model is None:
            return
        self.model.learn(total_timesteps=timesteps, progress_bar=False)
        self.model.save(str(self.model_path))
        self.replay_buffer = self.model.replay_buffer


class FakeEnv:
    """Minimal gym-like interface used to initialise the agent."""

    def __init__(self, obs_dim: int, action_dim: int) -> None:
        self.observation_space = _Box(low=-np.inf, high=np.inf, shape=(obs_dim,))
        self.action_space = _Discrete(action_dim)

    def reset(self):  # pragma: no cover - dummy env
        return np.zeros(self.observation_space.shape, dtype=np.float32)

    def step(self, action):  # pragma: no cover - dummy env
        return self.reset(), 0.0, True, False, {}


class _Box:
    def __init__(self, low: float, high: float, shape: tuple[int, ...]):
        self.low = low
        self.high = high
        self.shape = shape


class _Discrete:
    def __init__(self, n: int):
        self.n = n

    def sample(self) -> int:  # pragma: no cover - helper
        return random.randrange(self.n)