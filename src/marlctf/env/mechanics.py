"""CTF match mechanics."""

from __future__ import annotations

from dataclasses import dataclass

from marlctf.models import (
    Agent,
    Flag,
    FlagStatus,
    Match,
    MatchEvent,
    MatchEventType,
    MatchStatus,
    Scenario,
    Team,
)
from marlctf.seeding import make_run_id

ACTION_STAY = 0
ACTION_NORTH = 1
ACTION_SOUTH = 2
ACTION_WEST = 3
ACTION_EAST = 4
ACTION_TAG = 5

ACTION_DELTAS = {
    ACTION_NORTH: (0, -1),
    ACTION_SOUTH: (0, 1),
    ACTION_WEST: (-1, 0),
    ACTION_EAST: (1, 0),
}

AGENT_IDS = ("red_0", "red_1", "red_2", "blue_0", "blue_1", "blue_2")


@dataclass
class StepResult:
    events: list[MatchEvent]
    invalid_actions: dict[str, int]


def create_initial_match(scenario: Scenario, seed: int) -> Match:
    teams: dict[str, Team] = {}
    agents: dict[str, Agent] = {}
    for team_id in ("red", "blue"):
        agent_ids = tuple(f"{team_id}_{idx}" for idx in range(3))
        spawn_zone = scenario.spawn_zones[team_id]
        teams[team_id] = Team(
            team_id=team_id,
            agent_ids=agent_ids,  # type: ignore[arg-type]
            spawn_zone=spawn_zone,
            flag_home=scenario.flag_homes[team_id],
            policy_id="scripted",
        )
        for agent_id, spawn in zip(agent_ids, spawn_zone, strict=True):
            agents[agent_id] = Agent(
                agent_id=agent_id,
                team_id=team_id,
                position=spawn,
                spawn_position=spawn,
            )

    flags = {
        "red": Flag("red_flag", "red", scenario.flag_homes["red"]),
        "blue": Flag("blue_flag", "blue", scenario.flag_homes["blue"]),
    }
    return Match(
        match_id=make_run_id("match", scenario.scenario_id, [seed]),
        scenario_id=scenario.scenario_id,
        seed=seed,
        teams=teams,
        agents=agents,
        flags=flags,
        max_steps=scenario.max_steps,
    )


def legal_action_mask(match: Match, agent_id: str, scenario: Scenario) -> tuple[int, ...]:
    agent = match.agents[agent_id]
    if match.status in {MatchStatus.TERMINATED, MatchStatus.TRUNCATED} or not agent.alive:
        return (1, 0, 0, 0, 0, 0)

    mask = [1, 0, 0, 0, 0, 0]
    for action, delta in ACTION_DELTAS.items():
        target = _add(agent.position, delta)
        if _is_open(target, scenario):
            mask[action] = 1
    mask[ACTION_TAG] = int(_adjacent_opponents(match, agent_id) != [])
    return tuple(mask)


def step_match(match: Match, actions: dict[str, int], scenario: Scenario) -> StepResult:
    if match.status in {MatchStatus.TERMINATED, MatchStatus.TRUNCATED}:
        return StepResult(events=[], invalid_actions={})

    if match.status == MatchStatus.NOT_STARTED:
        match.status = MatchStatus.RUNNING

    events: list[MatchEvent] = []
    invalid_actions: dict[str, int] = {}
    normalized: dict[str, int] = {}
    for agent_id in AGENT_IDS:
        action = actions.get(agent_id, ACTION_STAY)
        mask = legal_action_mask(match, agent_id, scenario)
        if action < 0 or action >= len(mask) or mask[action] != 1:
            invalid_actions[agent_id] = action
            events.append(
                MatchEvent(
                    match.step_count,
                    MatchEventType.INVALID_ACTION,
                    agent_id=agent_id,
                    team_id=match.agents[agent_id].team_id,
                    details={"action": action, "handled_as": ACTION_STAY},
                )
            )
            action = ACTION_STAY
        normalized[agent_id] = action

    _apply_movement(match, normalized, scenario, events)
    _apply_tags(match, normalized, scenario, events)
    _apply_flag_pickups(match, events)
    _apply_scores(match, scenario, events)

    match.step_count += 1
    _apply_terminal_status(match, scenario, events)
    match.events.extend(events)
    return StepResult(events=events, invalid_actions=invalid_actions)


def _apply_movement(match: Match, actions: dict[str, int], scenario: Scenario, events: list[MatchEvent]) -> None:
    desired: dict[str, tuple[int, int]] = {}
    for agent_id, action in actions.items():
        if action in ACTION_DELTAS:
            target = _add(match.agents[agent_id].position, ACTION_DELTAS[action])
            desired[agent_id] = target if _is_open(target, scenario) else match.agents[agent_id].position
        else:
            desired[agent_id] = match.agents[agent_id].position

    occupied_before = {
        agent.position: agent_id
        for agent_id, agent in match.agents.items()
        if agent.alive
    }
    target_counts: dict[tuple[int, int], int] = {}
    for target in desired.values():
        target_counts[target] = target_counts.get(target, 0) + 1

    for agent_id, target in desired.items():
        agent = match.agents[agent_id]
        original = agent.position
        blocked_by_stationary = (
            target in occupied_before
            and occupied_before[target] != agent_id
            and desired[occupied_before[target]] == target
        )
        if target_counts[target] > 1 or blocked_by_stationary:
            target = original
        if target != original:
            agent.position = target
            events.append(
                MatchEvent(
                    match.step_count,
                    MatchEventType.MOVE,
                    agent_id=agent_id,
                    team_id=agent.team_id,
                    details={"from": original, "to": target},
                )
            )


def _apply_tags(match: Match, actions: dict[str, int], scenario: Scenario, events: list[MatchEvent]) -> None:
    for agent_id, action in actions.items():
        if action != ACTION_TAG:
            continue
        tagger = match.agents[agent_id]
        opponents = _adjacent_opponents(match, agent_id)
        if not opponents:
            continue
        target = sorted(opponents)[0]
        tagged = match.agents[target]
        was_carrier = tagged.has_flag
        if was_carrier:
            carried_flag = match.flags[_opponent_team(tagged.team_id)]
            _return_flag(carried_flag)
        tagged.has_flag = False
        tagged.position = tagged.spawn_position
        tagged.last_action = None
        events.append(
            MatchEvent(
                match.step_count,
                MatchEventType.TAG,
                agent_id=agent_id,
                team_id=tagger.team_id,
                details={"tagged_agent_id": target, "carrier": was_carrier},
            )
        )
        if was_carrier:
            events.append(
                MatchEvent(
                    match.step_count,
                    MatchEventType.FLAG_RETURN,
                    agent_id=target,
                    team_id=tagged.team_id,
                    details={"flag_team": _opponent_team(tagged.team_id)},
                )
            )


def _apply_flag_pickups(match: Match, events: list[MatchEvent]) -> None:
    for agent in match.agents.values():
        if agent.has_flag:
            continue
        opponent = _opponent_team(agent.team_id)
        flag = match.flags[opponent]
        if flag.status == FlagStatus.HOME and flag.position == agent.position:
            flag.status = FlagStatus.CARRIED
            flag.position = None
            flag.carrier_agent_id = agent.agent_id
            agent.has_flag = True
            events.append(
                MatchEvent(
                    match.step_count,
                    MatchEventType.FLAG_PICKUP,
                    agent_id=agent.agent_id,
                    team_id=agent.team_id,
                    details={"flag_team": opponent},
                )
            )


def _apply_scores(match: Match, scenario: Scenario, events: list[MatchEvent]) -> None:
    for agent in match.agents.values():
        if not agent.has_flag or agent.position != scenario.flag_homes[agent.team_id]:
            continue
        opponent = _opponent_team(agent.team_id)
        flag = match.flags[opponent]
        match.score[agent.team_id] += 1
        agent.has_flag = False
        _return_flag(flag)
        events.append(
            MatchEvent(
                match.step_count,
                MatchEventType.SCORE,
                agent_id=agent.agent_id,
                team_id=agent.team_id,
                details={"score": dict(match.score), "flag_team": opponent},
            )
        )


def _apply_terminal_status(match: Match, scenario: Scenario, events: list[MatchEvent]) -> None:
    for team_id, score in match.score.items():
        if score >= scenario.capture_target:
            match.status = MatchStatus.TERMINATED
            match.winner = team_id
            match.terminal_reason = "capture_target"
            events.append(
                MatchEvent(
                    match.step_count,
                    MatchEventType.TERMINAL,
                    team_id=team_id,
                    details={"reason": "capture_target", "winner": team_id},
                )
            )
            return
    if match.step_count >= scenario.max_steps:
        match.status = MatchStatus.TRUNCATED
        match.winner = "draw"
        match.terminal_reason = "max_steps"
        events.append(
            MatchEvent(
                match.step_count,
                MatchEventType.TERMINAL,
                details={"reason": "max_steps", "winner": "draw"},
            )
        )


def _return_flag(flag: Flag) -> None:
    flag.status = FlagStatus.HOME
    flag.position = flag.home_position
    flag.carrier_agent_id = None


def _adjacent_opponents(match: Match, agent_id: str) -> list[str]:
    agent = match.agents[agent_id]
    return [
        other_id
        for other_id, other in match.agents.items()
        if other.team_id != agent.team_id and other.alive and _manhattan(agent.position, other.position) == 1
    ]


def _is_open(coord: tuple[int, int], scenario: Scenario) -> bool:
    x, y = coord
    return 0 <= x < scenario.map_width and 0 <= y < scenario.map_height and coord not in scenario.walls


def _add(coord: tuple[int, int], delta: tuple[int, int]) -> tuple[int, int]:
    return coord[0] + delta[0], coord[1] + delta[1]


def _manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _opponent_team(team_id: str) -> str:
    return "blue" if team_id == "red" else "red"
