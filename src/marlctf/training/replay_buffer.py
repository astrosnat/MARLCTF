"""Episode replay buffer for local smoke training."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class Transition:
    observations: dict[str, np.ndarray]
    actions: dict[str, int]
    rewards: dict[str, float]
    next_observations: dict[str, np.ndarray]
    dones: dict[str, bool]
    infos: dict[str, dict[str, Any]]
    next_infos: dict[str, dict[str, Any]] | None = None


class EpisodeReplayBuffer:
    def __init__(self, capacity: int, seed: int | None = None) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.rng = random.Random(seed)
        self.transitions: list[Transition] = []
        self.episodes: list[list[Transition]] = []
        self._current_episode: list[Transition] | None = None

    @property
    def episode_count(self) -> int:
        return len(self.episodes)

    def __len__(self) -> int:
        return len(self.transitions)

    def start_episode(self) -> None:
        if self._current_episode is not None:
            raise RuntimeError("episode already started")
        self._current_episode = []

    def append(self, transition: Transition) -> None:
        if self._current_episode is None:
            raise RuntimeError("start_episode must be called before append")
        self.transitions.append(transition)
        self._current_episode.append(transition)
        while len(self.transitions) > self.capacity:
            removed = self.transitions.pop(0)
            for episode in self.episodes:
                if episode and episode[0] is removed:
                    episode.pop(0)
                    break

    def end_episode(self) -> None:
        if self._current_episode is None:
            raise RuntimeError("no active episode")
        self.episodes.append(list(self._current_episode))
        self._current_episode = None
        self.episodes = [episode for episode in self.episodes if episode]

    def sample(self, batch_size: int) -> list[Transition]:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if not self.transitions:
            return []
        if batch_size >= len(self.transitions):
            return list(self.transitions)
        return self.rng.sample(self.transitions, batch_size)
