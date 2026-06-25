"""Compact VDN components for smoke training."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn


class VDNAgentNetwork(nn.Module):
    def __init__(self, obs_dim: int, hidden_dim: int, action_dim: int) -> None:
        super().__init__()
        self.obs_dim = obs_dim
        self.hidden_dim = hidden_dim
        self.action_dim = action_dim
        self.net = nn.Sequential(
            nn.Linear(obs_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
        )

    def forward(self, observations: torch.Tensor) -> torch.Tensor:
        original_shape = observations.shape
        flat = observations.reshape(-1, original_shape[-1])
        q_values = self.net(flat)
        return q_values.reshape(*original_shape[:-1], self.action_dim)


def team_value_sum(q_values: torch.Tensor, actions: torch.Tensor) -> torch.Tensor:
    selected = q_values.gather(-1, actions.unsqueeze(-1)).squeeze(-1)
    return selected.sum(dim=-1)


def masked_argmax(q_values: torch.Tensor, action_mask: torch.Tensor) -> torch.Tensor:
    masked = q_values.masked_fill(action_mask <= 0, -1.0e9)
    return masked.argmax(dim=-1)


class VDNPolicy:
    def __init__(
        self,
        obs_dim: int,
        action_dim: int,
        *,
        hidden_dim: int = 32,
        seed: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        if seed is not None:
            torch.manual_seed(seed)
        self.obs_dim = obs_dim
        self.action_dim = action_dim
        self.hidden_dim = hidden_dim
        self.network = VDNAgentNetwork(obs_dim, hidden_dim, action_dim)
        self.metadata = metadata or {}

    def act(self, agent_id: str, observation: np.ndarray, info: dict[str, Any]) -> int:
        del agent_id
        obs = torch.as_tensor(observation, dtype=torch.float32).reshape(1, 1, -1)
        mask = torch.as_tensor(info.get("action_mask", np.ones(self.action_dim)), dtype=torch.int64).reshape(1, -1)
        with torch.no_grad():
            q_values = self.network(obs).reshape(1, -1)
            action = masked_argmax(q_values, mask)
        return int(action.item())

    def save_checkpoint(self, path: str | Path, *, metadata: dict[str, Any] | None = None) -> Path:
        checkpoint_path = Path(path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        merged_metadata = dict(self.metadata)
        if metadata:
            merged_metadata.update(metadata)
        torch.save(
            {
                "obs_dim": self.obs_dim,
                "action_dim": self.action_dim,
                "hidden_dim": self.hidden_dim,
                "state_dict": self.network.state_dict(),
                "metadata": merged_metadata,
            },
            checkpoint_path,
        )
        self.metadata = merged_metadata
        return checkpoint_path

    @classmethod
    def load_checkpoint(cls, path: str | Path) -> "VDNPolicy":
        payload = torch.load(Path(path), map_location="cpu")
        policy = cls(
            obs_dim=int(payload["obs_dim"]),
            action_dim=int(payload["action_dim"]),
            hidden_dim=int(payload["hidden_dim"]),
            metadata=dict(payload.get("metadata", {})),
        )
        policy.network.load_state_dict(payload["state_dict"])
        policy.network.eval()
        return policy
