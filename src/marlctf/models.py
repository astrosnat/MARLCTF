"""Shared data models for MARLCTF."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

Coordinate = tuple[int, int]


class MatchStatus(StrEnum):
    NOT_STARTED = "not_started"
    RUNNING = "running"
    TERMINATED = "terminated"
    TRUNCATED = "truncated"


class FlagStatus(StrEnum):
    HOME = "home"
    CARRIED = "carried"
    DROPPED = "dropped"


class RunStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"
    RUNNING = "running"


class RunType(StrEnum):
    MATCH = "match"
    TRAIN = "train"
    EVALUATE = "evaluate"


class PolicyType(StrEnum):
    RANDOM = "random"
    SCRIPTED = "scripted"
    VDN = "vdn"
    QMIX = "qmix"


class MatchEventType(StrEnum):
    MOVE = "move"
    INVALID_ACTION = "invalid_action"
    TAG = "tag"
    FLAG_PICKUP = "flag_pickup"
    FLAG_RETURN = "flag_return"
    SCORE = "score"
    TERMINAL = "terminal"
    ERROR = "error"


@dataclass(frozen=True)
class Team:
    team_id: str
    agent_ids: tuple[str, str, str]
    spawn_zone: tuple[Coordinate, Coordinate, Coordinate]
    flag_home: Coordinate
    score: int = 0
    policy_id: str = "scripted"

    def __post_init__(self) -> None:
        if self.team_id not in {"red", "blue"}:
            raise ValueError("team_id must be 'red' or 'blue'")
        if len(set(self.agent_ids)) != 3:
            raise ValueError("team must contain exactly three unique agents")


@dataclass
class Agent:
    agent_id: str
    team_id: str
    position: Coordinate
    spawn_position: Coordinate
    alive: bool = True
    has_flag: bool = False
    respawn_timer: int = 0
    last_action: int | None = None
    reward_total: float = 0.0

    def __post_init__(self) -> None:
        if self.team_id not in {"red", "blue"}:
            raise ValueError("agent team_id must be 'red' or 'blue'")
        if self.respawn_timer < 0:
            raise ValueError("respawn_timer must be non-negative")


@dataclass
class Flag:
    flag_id: str
    team_id: str
    home_position: Coordinate
    position: Coordinate | None = None
    carrier_agent_id: str | None = None
    status: FlagStatus = FlagStatus.HOME

    def __post_init__(self) -> None:
        if self.team_id not in {"red", "blue"}:
            raise ValueError("flag team_id must be 'red' or 'blue'")
        if self.position is None:
            self.position = self.home_position
        if self.status == FlagStatus.CARRIED and not self.carrier_agent_id:
            raise ValueError("carried flag must have a carrier_agent_id")
        if self.status != FlagStatus.CARRIED and self.carrier_agent_id:
            raise ValueError("only carried flags may have a carrier_agent_id")


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    map_width: int
    map_height: int
    walls: frozenset[Coordinate]
    spawn_zones: dict[str, tuple[Coordinate, Coordinate, Coordinate]]
    flag_homes: dict[str, Coordinate]
    legal_actions: dict[int, str]
    capture_target: int
    max_steps: int
    reward_config: dict[str, float]
    observation_config: dict[str, Any]
    seed_policy: str = "reset"

    def __post_init__(self) -> None:
        if self.map_width <= 0 or self.map_height <= 0:
            raise ValueError("map dimensions must be positive")
        if self.capture_target <= 0:
            raise ValueError("capture_target must be positive")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
        if set(self.spawn_zones) != {"red", "blue"}:
            raise ValueError("spawn_zones must contain red and blue")
        if set(self.flag_homes) != {"red", "blue"}:
            raise ValueError("flag_homes must contain red and blue")
        for coord in self.walls:
            self._validate_bounds(coord)
        for coord in self.flag_homes.values():
            self._validate_open_coordinate(coord)
        for zone in self.spawn_zones.values():
            if len(zone) != 3:
                raise ValueError("each spawn zone must contain three coordinates")
            for coord in zone:
                self._validate_open_coordinate(coord)

    def _validate_bounds(self, coord: Coordinate) -> None:
        x, y = coord
        if x < 0 or y < 0 or x >= self.map_width or y >= self.map_height:
            raise ValueError(f"coordinate out of bounds: {coord}")

    def _validate_open_coordinate(self, coord: Coordinate) -> None:
        self._validate_bounds(coord)
        if coord in self.walls:
            raise ValueError(f"coordinate is blocked by wall: {coord}")


@dataclass
class Observation:
    agent_id: str
    self_features: tuple[float, ...]
    ally_features: tuple[tuple[float, ...], ...]
    opponent_features: tuple[tuple[float, ...], ...]
    flag_features: tuple[float, ...]
    score_features: tuple[float, ...]
    action_mask: tuple[int, ...]

    def __post_init__(self) -> None:
        if any(value not in {0, 1} for value in self.action_mask):
            raise ValueError("action_mask values must be 0 or 1")


@dataclass(frozen=True)
class GlobalState:
    agent_positions: dict[str, Coordinate]
    agent_alive: dict[str, bool]
    flag_states: dict[str, dict[str, Any]]
    score: dict[str, int]
    remaining_steps: float
    scenario_features: tuple[float, ...]

    def __post_init__(self) -> None:
        if not 0.0 <= self.remaining_steps <= 1.0:
            raise ValueError("remaining_steps must be normalized to [0, 1]")


@dataclass(frozen=True)
class PolicyConfig:
    policy_id: str
    policy_type: PolicyType
    team_id: str
    checkpoint_path: Path | None = None
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.team_id not in {"red", "blue"}:
            raise ValueError("policy team_id must be 'red' or 'blue'")


@dataclass
class MatchEvent:
    step: int
    event_type: MatchEventType
    agent_id: str | None = None
    team_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.step < 0:
            raise ValueError("event step must be non-negative")
        if self.event_type == MatchEventType.ERROR:
            if "code" not in self.details or "message" not in self.details:
                raise ValueError("error events require code and message details")


@dataclass
class Match:
    match_id: str
    scenario_id: str
    seed: int
    teams: dict[str, Team]
    agents: dict[str, Agent]
    flags: dict[str, Flag]
    max_steps: int
    step_count: int = 0
    score: dict[str, int] = field(default_factory=lambda: {"red": 0, "blue": 0})
    status: MatchStatus = MatchStatus.NOT_STARTED
    winner: str | None = None
    terminal_reason: str | None = None
    events: list[MatchEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if set(self.teams) != {"red", "blue"}:
            raise ValueError("match must contain red and blue teams")
        if len(self.agents) != 6:
            raise ValueError("match must contain exactly six agents")
        if set(self.flags) != {"red", "blue"}:
            raise ValueError("match must contain red and blue flags")
        if self.step_count > self.max_steps:
            raise ValueError("step_count must not exceed max_steps")
        if self.status in {MatchStatus.TERMINATED, MatchStatus.TRUNCATED} and not self.terminal_reason:
            raise ValueError("terminal matches require terminal_reason")


@dataclass
class RunArtifact:
    run_id: str
    run_type: RunType
    created_at: str
    config_path: Path
    scenario_id: str
    seeds: tuple[int, ...]
    policy_ids: tuple[str, ...]
    metrics_path: Path
    events_path: Path | None = None
    checkpoint_paths: tuple[Path, ...] = ()
    summary: dict[str, Any] = field(default_factory=dict)
    status: RunStatus = RunStatus.RUNNING
    error: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.status == RunStatus.COMPLETED and not self.summary:
            raise ValueError("completed runs require summary metrics")
        if self.status in {RunStatus.FAILED, RunStatus.INTERRUPTED} and not self.error:
            raise ValueError("failed or interrupted runs require an error reason")
