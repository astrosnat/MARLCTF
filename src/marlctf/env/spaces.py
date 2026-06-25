"""Small space fallbacks used when Gymnasium is not installed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class Discrete:
    n: int

    def sample(self) -> int:
        return int(np.random.randint(self.n))

    def contains(self, value: Any) -> bool:
        return isinstance(value, int) and 0 <= value < self.n


@dataclass(frozen=True)
class Box:
    low: float
    high: float
    shape: tuple[int, ...]
    dtype: Any = np.float32

    def sample(self) -> np.ndarray:
        return np.zeros(self.shape, dtype=self.dtype)

    def contains(self, value: Any) -> bool:
        arr = np.asarray(value)
        return arr.shape == self.shape


def make_discrete(n: int):
    try:
        from gymnasium import spaces

        return spaces.Discrete(n)
    except ImportError:
        return Discrete(n)


def make_box(*, low: float, high: float, shape: tuple[int, ...], dtype: Any = np.float32):
    try:
        from gymnasium import spaces

        return spaces.Box(low=low, high=high, shape=shape, dtype=dtype)
    except ImportError:
        return Box(low=low, high=high, shape=shape, dtype=dtype)
