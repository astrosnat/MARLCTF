from __future__ import annotations

from marlctf.env.mechanics import (
    create_initial_match,
    legal_action_mask,
    step_match,
)
from marlctf.models import FlagStatus, MatchEventType, MatchStatus


def test_initial_match_has_two_teams_six_agents_and_flags(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)

    assert set(match.teams) == {"red", "blue"}
    assert len(match.agents) == 6
    assert match.flags["red"].status == FlagStatus.HOME
    assert match.flags["blue"].position == smoke_scenario.flag_homes["blue"]


def test_movement_respects_bounds_and_walls(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    mask = legal_action_mask(match, "red_0", smoke_scenario)

    assert mask[3] == 1  # west from [1,2] is open
    assert mask[4] == 1  # east from [1,2] is open

    match.agents["red_0"].position = (3, 1)
    mask = legal_action_mask(match, "red_0", smoke_scenario)
    assert mask[4] == 0  # wall at [4,1]


def test_flag_pickup_and_score(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    match.agents["red_0"].position = (7, 3)

    result = step_match(match, {"red_0": 4}, smoke_scenario)
    assert match.flags["blue"].status == FlagStatus.CARRIED
    assert match.flags["blue"].carrier_agent_id == "red_0"
    assert any(event.event_type == MatchEventType.FLAG_PICKUP for event in result.events)

    match.agents["red_0"].position = (1, 3)
    result = step_match(match, {"red_0": 3}, smoke_scenario)
    assert match.score["red"] == 1
    assert match.status == MatchStatus.TERMINATED
    assert match.winner == "red"
    assert match.flags["blue"].status == FlagStatus.HOME
    assert any(event.event_type == MatchEventType.SCORE for event in result.events)


def test_tag_returns_carried_flag_and_respawns_carrier(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    carrier = match.agents["red_0"]
    carrier.position = (5, 3)
    carrier.has_flag = True
    defender = match.agents["blue_0"]
    defender.position = (5, 4)
    match.flags["blue"].status = FlagStatus.CARRIED
    match.flags["blue"].carrier_agent_id = "red_0"
    match.flags["blue"].position = None

    result = step_match(match, {"blue_0": 5}, smoke_scenario)

    assert carrier.position == carrier.spawn_position
    assert not carrier.has_flag
    assert match.flags["blue"].status == FlagStatus.HOME
    assert match.flags["blue"].carrier_agent_id is None
    assert any(event.event_type == MatchEventType.TAG for event in result.events)


def test_truncates_at_max_steps(smoke_scenario):
    match = create_initial_match(smoke_scenario, seed=42)
    match.step_count = smoke_scenario.max_steps - 1

    step_match(match, {}, smoke_scenario)

    assert match.status == MatchStatus.TRUNCATED
    assert match.terminal_reason == "max_steps"
