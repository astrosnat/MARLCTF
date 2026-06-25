"""VDN policy adapter for match and evaluation runs."""

from __future__ import annotations

from pathlib import Path

from marlctf.policies.random_policy import RandomPolicy
from marlctf.training.vdn import VDNPolicy as _VDNPolicy


class VDNPolicy:
    def __init__(self, checkpoint_path: str | Path | None = None, *, seed: int | None = None) -> None:
        self.fallback = RandomPolicy(seed=seed)
        self.policy: _VDNPolicy | None = None
        if checkpoint_path:
            path = Path(checkpoint_path)
            if path.exists():
                self.policy = _VDNPolicy.load_checkpoint(path)

    def act(self, agent_id: str, observation, info: dict) -> int:
        if self.policy is None:
            return self.fallback.act(agent_id, observation, info)
        return self.policy.act(agent_id, observation, info)
