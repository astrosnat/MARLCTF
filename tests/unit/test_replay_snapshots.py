from __future__ import annotations

from marlctf.env.mechanics import AGENT_IDS, create_initial_match
from marlctf.models import FlagStatus, MatchEvent, MatchEventType, MatchStatus
from marlctf.replay import build_replay_snapshot, validate_replay_sequence, validate_replay_snapshot


def test_replay_snapshot_contains_schema_positions_flags_and_terminal(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    match.status = MatchStatus.RUNNING
    event = MatchEvent(0, MatchEventType.MOVE, agent_id="red_0", team_id="red", details={"to": (1, 2)})

    snapshot = build_replay_snapshot(match, smoke_scenario, run_id="run-1", events=[event])

    assert snapshot["schema_version"] == "1.0"
    assert snapshot["run_id"] == "run-1"
    assert snapshot["run_type"] == "match"
    assert snapshot["scenario_id"] == smoke_scenario.scenario_id
    assert snapshot["seed"] == 42
    assert snapshot["step"] == 0
    assert snapshot["map"]["width"] == smoke_scenario.map_width
    assert set(snapshot["agents"]) == set(AGENT_IDS)
    assert snapshot["agents"]["red_0"]["team"] == "red"
    assert snapshot["agents"]["red_0"]["x"] == match.agents["red_0"].position[0]
    assert snapshot["flags"]["red"]["status"] == "home"
    assert snapshot["flags"]["red"]["carrier"] is None
    assert snapshot["score"] == {"red": 0, "blue": 0}
    assert snapshot["terminal"] == {"status": "running", "winner": None, "reason": None}
    assert snapshot["events"][0]["event_type"] == "move"

    assert validate_replay_snapshot(snapshot).ok


def test_replay_snapshot_supports_carried_flag_with_null_coordinates(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    match.agents["red_0"].has_flag = True
    match.flags["blue"].status = FlagStatus.CARRIED
    match.flags["blue"].position = None
    match.flags["blue"].carrier_agent_id = "red_0"

    snapshot = build_replay_snapshot(match, smoke_scenario)

    assert snapshot["flags"]["blue"] == {
        "status": "carried",
        "x": None,
        "y": None,
        "carrier": "red_0",
    }
    assert validate_replay_snapshot(snapshot).ok


def test_replay_snapshot_validator_rejects_out_of_bounds_agent(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    snapshot = build_replay_snapshot(match, smoke_scenario)
    snapshot["agents"]["red_0"]["x"] = smoke_scenario.map_width

    result = validate_replay_snapshot(snapshot)

    assert not result.ok
    assert any("out of bounds" in error for error in result.errors)


def test_replay_sequence_validator_requires_zero_start_and_ordered_steps(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    first = build_replay_snapshot(match, smoke_scenario, step=1)
    second = build_replay_snapshot(match, smoke_scenario, step=0)

    result = validate_replay_sequence([first, second])

    assert not result.ok
    assert "snapshot steps must start at 0" in result.errors
    assert "snapshot steps must be ordered" in result.errors
