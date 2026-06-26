"""Replay snapshot builders and validators."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

from marlctf.env.mechanics import AGENT_IDS
from marlctf.models import Match, MatchEvent, Scenario

REPLAY_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ReplayValidationResult:
    """Validation result for replay snapshots and streams."""

    ok: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


def build_replay_snapshot(
    match: Match,
    scenario: Scenario,
    *,
    run_id: str | None = None,
    run_type: str = "match",
    episode: int | None = None,
    step: int | None = None,
    events: Iterable[MatchEvent | dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable replay snapshot from match state."""

    snapshot_step = match.step_count if step is None else step
    step_events = list(events or [])
    return {
        "schema_version": REPLAY_SCHEMA_VERSION,
        "run_id": run_id or match.match_id,
        "run_type": run_type,
        "scenario_id": match.scenario_id,
        "seed": match.seed,
        "episode": episode,
        "step": snapshot_step,
        "map": {
            "width": scenario.map_width,
            "height": scenario.map_height,
            "walls": [[x, y] for x, y in sorted(scenario.walls)],
        },
        "agents": {
            agent_id: {
                "team": agent.team_id,
                "x": agent.position[0],
                "y": agent.position[1],
                "alive": agent.alive,
                "has_flag": agent.has_flag,
            }
            for agent_id, agent in sorted(match.agents.items())
        },
        "flags": {
            team_id: {
                "status": flag.status.value,
                "x": None if flag.position is None else flag.position[0],
                "y": None if flag.position is None else flag.position[1],
                "carrier": flag.carrier_agent_id,
            }
            for team_id, flag in sorted(match.flags.items())
        },
        "score": dict(match.score),
        "terminal": {
            "status": match.status.value,
            "winner": match.winner,
            "reason": match.terminal_reason,
        },
        "events": [_event_to_dict(event) for event in step_events],
    }


def validate_replay_snapshot(snapshot: dict[str, Any]) -> ReplayValidationResult:
    """Validate a single replay snapshot."""

    errors: list[str] = []
    required = (
        "schema_version",
        "run_id",
        "run_type",
        "scenario_id",
        "seed",
        "step",
        "map",
        "agents",
        "flags",
        "score",
        "terminal",
        "events",
    )
    for field_name in required:
        if field_name not in snapshot:
            errors.append(f"missing required field: {field_name}")

    if errors:
        return ReplayValidationResult(ok=False, errors=tuple(errors))

    if snapshot["schema_version"] != REPLAY_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {snapshot['schema_version']}")

    if not isinstance(snapshot["step"], int) or snapshot["step"] < 0:
        errors.append("step must be a non-negative integer")

    map_data = snapshot.get("map", {})
    width = map_data.get("width")
    height = map_data.get("height")
    if not isinstance(width, int) or width <= 0:
        errors.append("map.width must be a positive integer")
    if not isinstance(height, int) or height <= 0:
        errors.append("map.height must be a positive integer")

    agents = snapshot.get("agents", {})
    if set(agents) != set(AGENT_IDS):
        errors.append("agents must contain exactly the default six 3v3 agent ids")
    for agent_id, agent in agents.items():
        _validate_coordinate(errors, f"agents.{agent_id}", agent.get("x"), agent.get("y"), width, height)
        if agent.get("team") not in {"red", "blue"}:
            errors.append(f"agents.{agent_id}.team must be red or blue")

    flags = snapshot.get("flags", {})
    if set(flags) != {"red", "blue"}:
        errors.append("flags must contain red and blue")
    for team_id, flag in flags.items():
        carrier = flag.get("carrier")
        x_value = flag.get("x")
        y_value = flag.get("y")
        if carrier is None:
            _validate_coordinate(errors, f"flags.{team_id}", x_value, y_value, width, height)
        else:
            if carrier not in agents:
                errors.append(f"flags.{team_id}.carrier must reference a known agent")
            if x_value is not None or y_value is not None:
                errors.append(f"flags.{team_id} carried flags must have null coordinates")

    score = snapshot.get("score", {})
    if set(score) != {"red", "blue"}:
        errors.append("score must contain red and blue")

    terminal = snapshot.get("terminal", {})
    if "status" not in terminal:
        errors.append("terminal.status is required")

    events = snapshot.get("events")
    if not isinstance(events, list):
        errors.append("events must be a list")
    else:
        for idx, event in enumerate(events):
            for event_field in ("step", "event_type", "agent_id", "team_id", "details"):
                if event_field not in event:
                    errors.append(f"events[{idx}] missing {event_field}")

    return ReplayValidationResult(ok=not errors, errors=tuple(errors))


def validate_replay_sequence(snapshots: Iterable[dict[str, Any]]) -> ReplayValidationResult:
    """Validate an ordered replay snapshot sequence."""

    rows = list(snapshots)
    errors: list[str] = []
    if not rows:
        return ReplayValidationResult(ok=False, errors=("replay artifact must contain at least one snapshot",))
    if rows[0].get("step") != 0:
        errors.append("snapshot steps must start at 0")

    previous_step: int | None = None
    for idx, snapshot in enumerate(rows):
        result = validate_replay_snapshot(snapshot)
        errors.extend(f"snapshots[{idx}]: {error}" for error in result.errors)
        step = snapshot.get("step")
        if isinstance(step, int):
            if previous_step is not None and step < previous_step:
                errors.append("snapshot steps must be ordered")
            previous_step = step

    return ReplayValidationResult(ok=not errors, errors=tuple(errors))


def _validate_coordinate(
    errors: list[str],
    label: str,
    x_value: Any,
    y_value: Any,
    width: Any,
    height: Any,
) -> None:
    if not isinstance(x_value, int) or not isinstance(y_value, int):
        errors.append(f"{label} coordinates must be integers")
        return
    if isinstance(width, int) and isinstance(height, int):
        if x_value < 0 or y_value < 0 or x_value >= width or y_value >= height:
            errors.append(f"{label} coordinates out of bounds")


def _event_to_dict(event: MatchEvent | dict[str, Any]) -> dict[str, Any]:
    if isinstance(event, dict):
        return _jsonable(event)
    return _jsonable(asdict(event))


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_jsonable(item) for item in value]
    return value

