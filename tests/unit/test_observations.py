from __future__ import annotations

import numpy as np

from marlctf.env.mechanics import create_initial_match
from marlctf.env.observations import build_action_mask, build_global_state, build_observation


def test_observation_shape_and_action_mask_are_fixed(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    obs = build_observation(match, "red_0", smoke_scenario)
    mask = build_action_mask(match, "red_0", smoke_scenario)

    assert obs.shape == (29,)
    assert mask.shape == (6,)
    assert set(mask.tolist()).issubset({0, 1})


def test_global_state_contains_all_agents_flags_score_and_step(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    state = build_global_state(match, smoke_scenario)

    assert state.shape == (33,)
    assert np.isclose(state[-1], 1.0)


def test_hidden_entities_are_zero_filled(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    match.agents["blue_0"].position = (8, 6)

    obs = build_observation(match, "red_0", smoke_scenario)

    opponent_section = obs[11:20]
    assert np.count_nonzero(opponent_section) < opponent_section.size
