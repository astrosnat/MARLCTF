from __future__ import annotations

import copy

import pytest

from marlctf.config import ConfigError, load_config, scenario_from_config, validate_config


def test_all_smoke_configs_load_and_validate(smoke_config_paths):
    for path in smoke_config_paths.values():
        config = load_config(path)
        assert config["scenario_id"] == "tiny-3v3-ctf"
        assert config["max_steps"] > 0
        assert set(config["policy_config"]) == {"red", "blue"}


def test_match_config_builds_scenario(smoke_match_config):
    scenario = scenario_from_config(smoke_match_config)

    assert scenario.scenario_id == "tiny-3v3-ctf"
    assert scenario.map_width == 9
    assert scenario.map_height == 7
    assert set(scenario.spawn_zones) == {"red", "blue"}
    assert scenario.legal_actions[5] == "tag"


def test_config_rejects_missing_reward_key(smoke_match_config):
    config = copy.deepcopy(smoke_match_config)
    del config["reward_config"]["score"]

    with pytest.raises(ConfigError, match="reward_config missing keys"):
        validate_config(config)


def test_config_rejects_out_of_bounds_spawn(smoke_match_config):
    config = copy.deepcopy(smoke_match_config)
    config["teams"]["red"]["spawn_zone"][0] = [99, 99]

    with pytest.raises(ValueError, match="coordinate out of bounds"):
        validate_config(config)


def test_evaluate_config_requires_integer_seed_list(smoke_config_paths):
    config = load_config(smoke_config_paths["evaluate"])
    config["seeds"] = []

    with pytest.raises(ConfigError, match="seeds list"):
        validate_config(config)
