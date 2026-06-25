"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from marlctf.models import Scenario


class ConfigError(ValueError):
    """Raised when a run configuration is invalid."""


REQUIRED_REWARD_KEYS = {
    "step",
    "flag_pickup",
    "tag",
    "tagged_while_carrying",
    "score",
    "terminal_win",
    "terminal_loss",
}

LEGAL_ACTIONS = {
    0: "stay",
    1: "move_north",
    2: "move_south",
    3: "move_west",
    4: "move_east",
    5: "tag",
}


def load_config(path: str | Path) -> dict[str, Any]:
    """Load and validate a YAML run config."""

    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"config file does not exist: {config_path}")

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ConfigError("config root must be a mapping")

    validate_config(data)
    return data


def validate_config(config: dict[str, Any]) -> None:
    """Validate common and command-specific config shape."""

    run_type = _required_str(config, "run_type")
    if run_type not in {"match", "train", "evaluate"}:
        raise ConfigError("run_type must be match, train, or evaluate")

    _required_str(config, "scenario_id")
    _required_int(config, "max_steps", minimum=1)
    _required_int(config, "capture_target", minimum=1)
    _required_str(config, "artifact_dir")
    _validate_reward_config(_required_mapping(config, "reward_config"))
    _validate_observation_config(_required_mapping(config, "observation"))
    _validate_policy_config(_required_mapping(config, "policy_config"))

    if run_type in {"match", "train"}:
        _required_int(config, "seed")
    else:
        seeds = config.get("seeds")
        if not isinstance(seeds, list) or not seeds or not all(isinstance(seed, int) for seed in seeds):
            raise ConfigError("evaluate configs require a non-empty integer seeds list")

    if run_type == "match":
        _validate_match_config(config)
    elif run_type == "train":
        _validate_train_config(config)
    else:
        _validate_evaluate_config(config)


def scenario_from_config(config: dict[str, Any]) -> Scenario:
    """Build a Scenario from a fully specified match config."""

    validate_config(config)
    if "map" not in config or "teams" not in config:
        raise ConfigError("scenario construction requires map and teams sections")

    map_config = _required_mapping(config, "map")
    teams = _required_mapping(config, "teams")
    width = _required_int(map_config, "width", minimum=1)
    height = _required_int(map_config, "height", minimum=1)
    walls = frozenset(_coordinate(coord, "wall") for coord in map_config.get("walls", []))
    spawn_zones = {
        team_id: tuple(_coordinate(coord, f"{team_id} spawn") for coord in _required_list(team, "spawn_zone"))
        for team_id, team in teams.items()
    }
    flag_homes = {
        team_id: _coordinate(_required_list(team, "flag_home"), f"{team_id} flag_home")
        for team_id, team in teams.items()
    }
    return Scenario(
        scenario_id=config["scenario_id"],
        map_width=width,
        map_height=height,
        walls=walls,
        spawn_zones=spawn_zones,
        flag_homes=flag_homes,
        legal_actions=_normalize_actions(config.get("actions", LEGAL_ACTIONS)),
        capture_target=config["capture_target"],
        max_steps=config["max_steps"],
        reward_config={key: float(value) for key, value in config["reward_config"].items()},
        observation_config=dict(config["observation"]),
        seed_policy="reset",
    )


def _validate_match_config(config: dict[str, Any]) -> None:
    teams = _required_mapping(config, "teams")
    if set(teams) != {"red", "blue"}:
        raise ConfigError("match teams must contain red and blue")
    if "map" not in config:
        raise ConfigError("match configs require map")
    scenario_from_config_without_revalidation(config)


def scenario_from_config_without_revalidation(config: dict[str, Any]) -> Scenario:
    map_config = _required_mapping(config, "map")
    teams = _required_mapping(config, "teams")
    width = _required_int(map_config, "width", minimum=1)
    height = _required_int(map_config, "height", minimum=1)
    walls = frozenset(_coordinate(coord, "wall") for coord in map_config.get("walls", []))
    spawn_zones: dict[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = {}
    flag_homes: dict[str, tuple[int, int]] = {}
    for team_id, team_config in teams.items():
        if not isinstance(team_config, dict):
            raise ConfigError(f"team {team_id} must be a mapping")
        zone = tuple(_coordinate(coord, f"{team_id} spawn") for coord in _required_list(team_config, "spawn_zone"))
        if len(zone) != 3:
            raise ConfigError(f"team {team_id} must have exactly three spawn coordinates")
        spawn_zones[team_id] = zone  # type: ignore[assignment]
        flag_homes[team_id] = _coordinate(_required_list(team_config, "flag_home"), f"{team_id} flag_home")
    return Scenario(
        scenario_id=config["scenario_id"],
        map_width=width,
        map_height=height,
        walls=walls,
        spawn_zones=spawn_zones,
        flag_homes=flag_homes,
        legal_actions=_normalize_actions(config.get("actions", LEGAL_ACTIONS)),
        capture_target=config["capture_target"],
        max_steps=config["max_steps"],
        reward_config={key: float(value) for key, value in config["reward_config"].items()},
        observation_config=dict(config["observation"]),
    )


def _validate_train_config(config: dict[str, Any]) -> None:
    training = _required_mapping(config, "training")
    _required_int(training, "episodes", minimum=1)
    _required_int(training, "batch_size", minimum=1)
    _required_int(training, "replay_capacity", minimum=1)
    if _required_str(config, "algorithm") != "vdn":
        raise ConfigError("phase 2 smoke training config must use vdn")


def _validate_evaluate_config(config: dict[str, Any]) -> None:
    _required_mapping(config, "candidate")
    _required_mapping(config, "baseline")
    metrics = _required_mapping(config, "metrics")
    acceptance = _required_mapping(metrics, "acceptance")
    min_win_rate = acceptance.get("min_win_rate")
    if not isinstance(min_win_rate, (int, float)) or not 0 <= float(min_win_rate) <= 1:
        raise ConfigError("metrics.acceptance.min_win_rate must be in [0, 1]")


def _validate_reward_config(reward_config: dict[str, Any]) -> None:
    missing = REQUIRED_REWARD_KEYS - set(reward_config)
    if missing:
        raise ConfigError(f"reward_config missing keys: {sorted(missing)}")
    for key in REQUIRED_REWARD_KEYS:
        if not isinstance(reward_config[key], (int, float)):
            raise ConfigError(f"reward_config.{key} must be numeric")


def _validate_observation_config(observation: dict[str, Any]) -> None:
    view_radius = observation.get("view_radius")
    if not isinstance(view_radius, int) or view_radius < 0:
        raise ConfigError("observation.view_radius must be a non-negative integer")


def _validate_policy_config(policy_config: dict[str, Any]) -> None:
    if set(policy_config) != {"red", "blue"}:
        raise ConfigError("policy_config must contain red and blue")
    for team_id, policy in policy_config.items():
        if not isinstance(policy, dict):
            raise ConfigError(f"policy_config.{team_id} must be a mapping")
        policy_type = policy.get("type")
        if policy_type not in {"random", "scripted", "vdn", "qmix"}:
            raise ConfigError(f"unsupported policy type for {team_id}: {policy_type}")


def _required_mapping(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"{key} must be a mapping")
    return value


def _required_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ConfigError(f"{key} must be a list")
    return value


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ConfigError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str, *, minimum: int | None = None) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ConfigError(f"{key} must be an integer")
    if minimum is not None and value < minimum:
        raise ConfigError(f"{key} must be >= {minimum}")
    return value


def _coordinate(value: Any, label: str) -> tuple[int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 2
        or not all(isinstance(part, int) for part in value)
    ):
        raise ConfigError(f"{label} coordinate must be [x, y]")
    return value[0], value[1]


def _normalize_actions(raw_actions: Any) -> dict[int, str]:
    if not isinstance(raw_actions, dict):
        raise ConfigError("actions must be a mapping")
    actions: dict[int, str] = {}
    for key, value in raw_actions.items():
        try:
            action_id = int(key)
        except (TypeError, ValueError) as exc:
            raise ConfigError(f"invalid action id: {key}") from exc
        if not isinstance(value, str) or not value:
            raise ConfigError(f"action {key} must have a non-empty name")
        actions[action_id] = value
    if actions != LEGAL_ACTIONS:
        raise ConfigError("actions must match the phase 1 discrete CTF action contract")
    return actions
