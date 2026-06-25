"""PettingZoo-style Parallel environment for toy 3v3 CTF."""

from __future__ import annotations

from typing import Any

import numpy as np

from marlctf.config import scenario_from_config
from marlctf.env.mechanics import AGENT_IDS, StepResult, create_initial_match, step_match
from marlctf.env.observations import build_action_mask, build_global_state, build_observation
from marlctf.env.rewards import calculate_rewards
from marlctf.env.spaces import make_box, make_discrete
from marlctf.models import Match, MatchStatus, Scenario
from marlctf.seeding import seed_everything

try:
    from pettingzoo import ParallelEnv
except ImportError:
    ParallelEnv = object  # type: ignore[misc, assignment]


class CTFParallelEnv(ParallelEnv):  # type: ignore[misc]
    metadata = {"name": "marlctf_3v3_v0", "render_modes": ["none", "ansi", "human"]}

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = dict(config)
        self.scenario: Scenario = scenario_from_config(self.config)
        self.possible_agents = list(AGENT_IDS)
        self.agents = list(self.possible_agents)
        self.match: Match | None = None
        self.last_step: StepResult = StepResult(events=[], invalid_actions={})
        self._observation_space = make_box(low=-1.0, high=1.0, shape=(29,), dtype=np.float32)
        self._action_space = make_discrete(6)

    def reset(self, seed: int | None = None, options: dict[str, Any] | None = None):
        del options
        actual_seed = seed_everything(seed if seed is not None else self.config.get("seed"))
        self.match = create_initial_match(self.scenario, actual_seed)
        self.match.status = MatchStatus.RUNNING
        self.agents = list(self.possible_agents)
        self.last_step = StepResult(events=[], invalid_actions={})
        observations = self._observations()
        infos = self._infos()
        return observations, infos

    def step(self, actions: dict[str, int]):
        if self.match is None:
            raise RuntimeError("environment must be reset before step")

        active_agents = list(self.possible_agents)
        self.last_step = step_match(self.match, actions, self.scenario)
        terminal_status = self.match.status if self.match.status == MatchStatus.TERMINATED else None
        rewards = calculate_rewards(
            self.last_step.events,
            self.scenario,
            agent_ids=active_agents,
            terminal_status=terminal_status,
            winner=self.match.winner,
        )
        observations = self._observations()
        terminations = {
            agent: self.match.status == MatchStatus.TERMINATED
            for agent in active_agents
        }
        truncations = {
            agent: self.match.status == MatchStatus.TRUNCATED
            for agent in active_agents
        }
        infos = self._infos()
        if self.match.status in {MatchStatus.TERMINATED, MatchStatus.TRUNCATED}:
            self.agents = []
        return observations, rewards, terminations, truncations, infos

    def state(self) -> np.ndarray:
        if self.match is None:
            raise RuntimeError("environment must be reset before state")
        return build_global_state(self.match, self.scenario)

    def observation_space(self, agent: str):
        self._validate_agent(agent)
        return self._observation_space

    def action_space(self, agent: str):
        self._validate_agent(agent)
        return self._action_space

    def render(self) -> str:
        if self.match is None:
            return ""
        rows = [["." for _ in range(self.scenario.map_width)] for _ in range(self.scenario.map_height)]
        for x, y in self.scenario.walls:
            rows[y][x] = "#"
        for team_id, flag in self.match.flags.items():
            if flag.position is not None:
                x, y = flag.position
                rows[y][x] = "R" if team_id == "red" else "B"
        for agent_id, agent in self.match.agents.items():
            x, y = agent.position
            rows[y][x] = agent_id[0].lower()
        return "\n".join("".join(row) for row in rows)

    def close(self) -> None:
        return None

    def _observations(self) -> dict[str, np.ndarray]:
        assert self.match is not None
        return {
            agent: build_observation(self.match, agent, self.scenario)
            for agent in self.possible_agents
        }

    def _infos(self) -> dict[str, dict[str, Any]]:
        assert self.match is not None
        events = [
            {
                "step": event.step,
                "event_type": event.event_type.value,
                "agent_id": event.agent_id,
                "team_id": event.team_id,
                "details": event.details,
            }
            for event in self.last_step.events
        ]
        return {
            agent: {
                "action_mask": build_action_mask(self.match, agent, self.scenario),
                "events": events,
                "invalid_action": self.last_step.invalid_actions.get(agent),
                "team_score": dict(self.match.score),
                "carrying_flag": self.match.agents[agent].has_flag,
            }
            for agent in self.possible_agents
        }

    def _validate_agent(self, agent: str) -> None:
        if agent not in self.possible_agents:
            raise KeyError(f"unknown agent: {agent}")
