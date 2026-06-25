"""Observation and global-state builders."""

from __future__ import annotations

import numpy as np

from marlctf.env.mechanics import AGENT_IDS, legal_action_mask
from marlctf.models import FlagStatus, Match, Scenario


def build_action_mask(match: Match, agent_id: str, scenario: Scenario) -> np.ndarray:
    return np.asarray(legal_action_mask(match, agent_id, scenario), dtype=np.int8)


def build_observation(match: Match, agent_id: str, scenario: Scenario) -> np.ndarray:
    agent = match.agents[agent_id]
    view_radius = int(scenario.observation_config.get("view_radius", 3))
    max_dim = float(max(scenario.map_width - 1, scenario.map_height - 1, 1))
    obs: list[float] = []

    obs.extend(
        [
            agent.position[0] / max_dim,
            agent.position[1] / max_dim,
            1.0 if agent.team_id == "red" else 0.0,
            1.0 if agent.alive else 0.0,
            1.0 if agent.has_flag else 0.0,
        ]
    )

    allies = [other for other in match.agents.values() if other.team_id == agent.team_id and other.agent_id != agent_id]
    opponents = [other for other in match.agents.values() if other.team_id != agent.team_id]
    for other in allies:
        obs.extend(_visible_agent_features(agent.position, other.position, other.alive, view_radius, max_dim))
    for other in opponents:
        obs.extend(_visible_agent_features(agent.position, other.position, other.alive, view_radius, max_dim))

    own_flag = match.flags[agent.team_id]
    opp_flag = match.flags["blue" if agent.team_id == "red" else "red"]
    obs.extend(_flag_features(agent.position, own_flag.position, own_flag.status, view_radius, max_dim))
    obs.extend(_flag_features(agent.position, opp_flag.position, opp_flag.status, view_radius, max_dim))

    obs.extend(
        [
            match.score["red"] / float(scenario.capture_target),
            match.score["blue"] / float(scenario.capture_target),
            max(0.0, (scenario.max_steps - match.step_count) / float(scenario.max_steps)),
        ]
    )
    return np.asarray(obs, dtype=np.float32)


def build_global_state(match: Match, scenario: Scenario) -> np.ndarray:
    max_dim = float(max(scenario.map_width - 1, scenario.map_height - 1, 1))
    state: list[float] = []
    for agent_id in AGENT_IDS:
        agent = match.agents[agent_id]
        state.extend(
            [
                agent.position[0] / max_dim,
                agent.position[1] / max_dim,
                1.0 if agent.alive else 0.0,
                1.0 if agent.has_flag else 0.0,
            ]
        )
    for team_id in ("red", "blue"):
        flag = match.flags[team_id]
        if flag.position is None:
            state.extend([0.0, 0.0])
        else:
            state.extend([flag.position[0] / max_dim, flag.position[1] / max_dim])
        state.append(_flag_status_value(flag.status))
    state.extend(
        [
            match.score["red"] / float(scenario.capture_target),
            match.score["blue"] / float(scenario.capture_target),
            max(0.0, (scenario.max_steps - match.step_count) / float(scenario.max_steps)),
        ]
    )
    return np.asarray(state, dtype=np.float32)


def _visible_agent_features(
    observer: tuple[int, int],
    target: tuple[int, int],
    alive: bool,
    view_radius: int,
    max_dim: float,
) -> list[float]:
    dx = target[0] - observer[0]
    dy = target[1] - observer[1]
    if abs(dx) + abs(dy) > view_radius:
        return [0.0, 0.0, 0.0]
    return [dx / max_dim, dy / max_dim, 1.0 if alive else 0.0]


def _flag_features(
    observer: tuple[int, int],
    position: tuple[int, int] | None,
    status: FlagStatus,
    view_radius: int,
    max_dim: float,
) -> list[float]:
    if position is None:
        return [0.0, 0.0, _flag_status_value(status)]
    dx = position[0] - observer[0]
    dy = position[1] - observer[1]
    if abs(dx) + abs(dy) > view_radius:
        return [0.0, 0.0, 0.0]
    return [dx / max_dim, dy / max_dim, _flag_status_value(status)]


def _flag_status_value(status: FlagStatus) -> float:
    if status == FlagStatus.HOME:
        return 0.0
    if status == FlagStatus.CARRIED:
        return 1.0
    return 0.5
