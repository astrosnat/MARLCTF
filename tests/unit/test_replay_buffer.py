from __future__ import annotations

import numpy as np

from marlctf.training.replay_buffer import EpisodeReplayBuffer, Transition


def _transition(step: int) -> Transition:
    obs = {"red_0": np.full((3,), step, dtype=np.float32)}
    next_obs = {"red_0": np.full((3,), step + 1, dtype=np.float32)}
    return Transition(
        observations=obs,
        actions={"red_0": step % 6},
        rewards={"red_0": float(step)},
        next_observations=next_obs,
        dones={"red_0": False},
        infos={"red_0": {"step": step}},
    )


def test_replay_buffer_records_episode_boundaries():
    buffer = EpisodeReplayBuffer(capacity=10, seed=123)
    buffer.start_episode()
    buffer.append(_transition(0))
    buffer.append(_transition(1))
    buffer.end_episode()

    assert len(buffer) == 2
    assert buffer.episode_count == 1
    assert len(buffer.episodes[0]) == 2


def test_replay_buffer_enforces_capacity():
    buffer = EpisodeReplayBuffer(capacity=3, seed=123)
    buffer.start_episode()
    for step in range(5):
        buffer.append(_transition(step))
    buffer.end_episode()

    assert len(buffer) == 3
    assert [transition.actions["red_0"] for transition in buffer.transitions] == [2, 3, 4]


def test_replay_buffer_sampling_is_deterministic():
    left = EpisodeReplayBuffer(capacity=10, seed=7)
    right = EpisodeReplayBuffer(capacity=10, seed=7)
    for buffer in (left, right):
        buffer.start_episode()
        for step in range(5):
            buffer.append(_transition(step))
        buffer.end_episode()

    sample_left = left.sample(3)
    sample_right = right.sample(3)

    assert [item.actions["red_0"] for item in sample_left] == [item.actions["red_0"] for item in sample_right]
