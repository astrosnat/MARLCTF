"""Random baseline policy."""

from __future__ import annotations

import random
from typing import Any


class RandomPolicy:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def act(self, agent_id: str, observation: Any, info: dict) -> int:
        del agent_id, observation
        mask = list(info.get("action_mask", [1, 1, 1, 1, 1, 1]))
        legal = [idx for idx, allowed in enumerate(mask) if int(allowed) == 1]
        return self.rng.choice(legal or [0])
