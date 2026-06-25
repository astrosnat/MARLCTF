from __future__ import annotations

import torch

from marlctf.training.vdn import VDNAgentNetwork, VDNPolicy, masked_argmax, team_value_sum


def test_vdn_network_outputs_per_agent_q_values():
    network = VDNAgentNetwork(obs_dim=29, hidden_dim=16, action_dim=6)
    batch = torch.zeros((2, 3, 29), dtype=torch.float32)

    q_values = network(batch)

    assert q_values.shape == (2, 3, 6)


def test_team_value_sum_adds_selected_agent_values():
    q_values = torch.tensor([[[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]])
    actions = torch.tensor([[1, 0, 1]])

    total = team_value_sum(q_values, actions)

    assert total.shape == (1,)
    assert total.item() == 11.0


def test_masked_argmax_respects_action_mask():
    q_values = torch.tensor([[10.0, 2.0, 3.0]])
    mask = torch.tensor([[0, 1, 1]])

    assert masked_argmax(q_values, mask).item() == 2


def test_vdn_policy_checkpoint_roundtrip(tmp_path):
    policy = VDNPolicy(obs_dim=29, action_dim=6, seed=5)
    checkpoint = tmp_path / "policy.pt"
    policy.save_checkpoint(checkpoint, metadata={"episode": 3})

    loaded = VDNPolicy.load_checkpoint(checkpoint)

    assert loaded.metadata["episode"] == 3
    assert loaded.obs_dim == 29
    assert loaded.action_dim == 6
