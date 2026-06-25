from __future__ import annotations

from marlctf.env.rewards import calculate_rewards
from marlctf.models import MatchEvent, MatchEventType, MatchStatus


def test_step_penalty_applies_to_all_agents(smoke_scenario):
    rewards = calculate_rewards([], smoke_scenario, agent_ids=["red_0", "blue_0"])

    assert rewards == {"red_0": -0.01, "blue_0": -0.01}


def test_event_rewards_apply_to_actor_and_team(smoke_scenario):
    events = [
        MatchEvent(0, MatchEventType.FLAG_PICKUP, agent_id="red_0", team_id="red"),
        MatchEvent(0, MatchEventType.TAG, agent_id="blue_0", team_id="blue"),
        MatchEvent(0, MatchEventType.SCORE, agent_id="red_0", team_id="red"),
    ]

    rewards = calculate_rewards(events, smoke_scenario, agent_ids=["red_0", "red_1", "blue_0"])

    assert rewards["red_0"] > rewards["red_1"] > 0
    assert rewards["blue_0"] > 0


def test_carrier_tagged_penalty(smoke_scenario):
    events = [
        MatchEvent(
            0,
            MatchEventType.TAG,
            agent_id="blue_0",
            team_id="blue",
            details={"tagged_agent_id": "red_0", "carrier": True},
        )
    ]

    rewards = calculate_rewards(events, smoke_scenario, agent_ids=["red_0", "blue_0"])

    assert rewards["red_0"] < 0
    assert rewards["blue_0"] > 0


def test_terminal_rewards_apply_by_team(smoke_scenario):
    rewards = calculate_rewards(
        [],
        smoke_scenario,
        agent_ids=["red_0", "blue_0"],
        terminal_status=MatchStatus.TERMINATED,
        winner="red",
    )

    assert rewards["red_0"] > 0
    assert rewards["blue_0"] < 0
