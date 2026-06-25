from __future__ import annotations

import numpy as np

from marlctf.env.ctf_parallel_env import CTFParallelEnv


def test_parallel_env_reset_contract(smoke_match_config):
    env = CTFParallelEnv(smoke_match_config)
    observations, infos = env.reset(seed=42)

    assert env.metadata["name"] == "marlctf_3v3_v0"
    assert env.agents == ["red_0", "red_1", "red_2", "blue_0", "blue_1", "blue_2"]
    assert set(observations) == set(env.agents)
    assert set(infos) == set(env.agents)
    assert all("action_mask" in info for info in infos.values())
    assert all(len(info["action_mask"]) == 6 for info in infos.values())


def test_spaces_and_state_are_stable(smoke_match_config):
    env = CTFParallelEnv(smoke_match_config)
    observations_a, _ = env.reset(seed=42)
    state_a = env.state()
    observations_b, _ = env.reset(seed=42)
    state_b = env.state()

    assert env.action_space("red_0").n == 6
    assert env.observation_space("red_0").shape == observations_a["red_0"].shape
    assert observations_a["red_0"].shape == observations_b["red_0"].shape
    np.testing.assert_allclose(observations_a["red_0"], observations_b["red_0"])
    np.testing.assert_allclose(state_a, state_b)


def test_invalid_action_is_recorded(smoke_match_config):
    env = CTFParallelEnv(smoke_match_config)
    env.reset(seed=42)
    actions = {agent: 0 for agent in env.agents}
    actions["red_0"] = 99

    _, _, _, _, infos = env.step(actions)

    invalid_events = [
        event
        for info in infos.values()
        for event in info["events"]
        if event["event_type"] == "invalid_action"
    ]
    assert invalid_events
    assert invalid_events[0]["agent_id"] == "red_0"


def test_step_returns_parallel_api_payload(smoke_match_config):
    env = CTFParallelEnv(smoke_match_config)
    env.reset(seed=42)
    actions = {agent: 0 for agent in env.agents}

    observations, rewards, terminations, truncations, infos = env.step(actions)

    assert set(observations) == set(env.possible_agents)
    assert set(rewards) == set(env.possible_agents)
    assert set(terminations) == set(env.possible_agents)
    assert set(truncations) == set(env.possible_agents)
    assert set(infos) == set(env.possible_agents)
    assert all(isinstance(reward, float) for reward in rewards.values())
