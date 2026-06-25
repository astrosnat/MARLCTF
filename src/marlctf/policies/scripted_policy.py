"""Deterministic scripted baseline policy."""

from __future__ import annotations

from marlctf.env.mechanics import ACTION_EAST, ACTION_NORTH, ACTION_SOUTH, ACTION_TAG, ACTION_WEST, ACTION_STAY
from marlctf.models import Match


class ScriptedPolicy:
    """Moves agents toward the opponent flag, then home; tags when possible."""

    def act_from_match(self, match: Match, agent_id: str, action_mask) -> int:
        mask = [int(value) for value in action_mask]
        if mask[ACTION_TAG]:
            return ACTION_TAG

        agent = match.agents[agent_id]
        if agent.has_flag:
            target = match.flags[agent.team_id].home_position
        else:
            target = match.flags["blue" if agent.team_id == "red" else "red"].home_position
        action = _move_toward(agent.position, target, mask)
        return action

    def act(self, agent_id: str, observation, info: dict) -> int:
        del agent_id, observation
        mask = [int(value) for value in info.get("action_mask", [1, 0, 0, 0, 0, 0])]
        return ACTION_TAG if len(mask) > ACTION_TAG and mask[ACTION_TAG] else ACTION_STAY


def _move_toward(position: tuple[int, int], target: tuple[int, int], mask: list[int]) -> int:
    x, y = position
    tx, ty = target
    candidates: list[int] = []
    if tx > x:
        candidates.append(ACTION_EAST)
    if tx < x:
        candidates.append(ACTION_WEST)
    if ty > y:
        candidates.append(ACTION_SOUTH)
    if ty < y:
        candidates.append(ACTION_NORTH)
    for action in candidates:
        if action < len(mask) and mask[action]:
            return action
    for action in (ACTION_EAST, ACTION_WEST, ACTION_SOUTH, ACTION_NORTH):
        if action < len(mask) and mask[action]:
            return action
    return ACTION_STAY
