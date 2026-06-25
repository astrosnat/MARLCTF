"""Reward calculation for CTF events."""

from __future__ import annotations

from marlctf.models import MatchEvent, MatchEventType, MatchStatus, Scenario


def calculate_rewards(
    events: list[MatchEvent],
    scenario: Scenario,
    *,
    agent_ids: list[str] | tuple[str, ...],
    terminal_status: MatchStatus | None = None,
    winner: str | None = None,
) -> dict[str, float]:
    rewards = {agent_id: float(scenario.reward_config["step"]) for agent_id in agent_ids}

    for event in events:
        if event.event_type == MatchEventType.FLAG_PICKUP and event.agent_id:
            rewards[event.agent_id] += float(scenario.reward_config["flag_pickup"])
        elif event.event_type == MatchEventType.TAG and event.agent_id:
            rewards[event.agent_id] += float(scenario.reward_config["tag"])
            tagged = event.details.get("tagged_agent_id")
            if event.details.get("carrier") and tagged in rewards:
                rewards[tagged] += float(scenario.reward_config["tagged_while_carrying"])
        elif event.event_type == MatchEventType.SCORE and event.team_id:
            for agent_id in rewards:
                if agent_id.startswith(f"{event.team_id}_"):
                    rewards[agent_id] += float(scenario.reward_config["score"])

    if terminal_status == MatchStatus.TERMINATED and winner in {"red", "blue"}:
        for agent_id in rewards:
            if agent_id.startswith(f"{winner}_"):
                rewards[agent_id] += float(scenario.reward_config["terminal_win"])
            else:
                rewards[agent_id] += float(scenario.reward_config["terminal_loss"])
    return rewards
