"""Run loops for MARLCTF commands."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from marlctf.artifacts import RunArtifactWriter
from marlctf.config import load_config
from marlctf.env.ctf_parallel_env import CTFParallelEnv
from marlctf.models import MatchStatus
from marlctf.policies.random_policy import RandomPolicy
from marlctf.policies.scripted_policy import ScriptedPolicy
from marlctf.policies.vdn_policy import VDNPolicy
from marlctf.seeding import make_run_id


def run_match(
    config_path: str | Path,
    *,
    seed: int | None = None,
    artifact_dir: str | Path | None = None,
    policy_red: str | None = None,
    policy_blue: str | None = None,
    render: str = "none",
) -> dict[str, Any]:
    config = load_config(config_path)
    if seed is not None:
        config["seed"] = seed
    if artifact_dir is not None:
        config["artifact_dir"] = Path(artifact_dir).as_posix()
    if policy_red is not None:
        config["policy_config"]["red"]["type"] = policy_red
    if policy_blue is not None:
        config["policy_config"]["blue"]["type"] = policy_blue

    env = CTFParallelEnv(config)
    observations, infos = env.reset(seed=config["seed"])
    policies = _build_policies(config)
    run_id = make_run_id("match", config["scenario_id"], [config["seed"]])
    writer = RunArtifactWriter(
        config["artifact_dir"],
        {
            "run_id": run_id,
            "run_type": "match",
            "config_path": Path(config_path).as_posix(),
            "scenario_id": config["scenario_id"],
            "seeds": [config["seed"]],
            "policy_ids": [
                f"red:{config['policy_config']['red']['type']}",
                f"blue:{config['policy_config']['blue']['type']}",
            ],
            "render": render,
        },
    )

    try:
        while env.agents:
            actions: dict[str, int] = {}
            assert env.match is not None
            for agent_id in env.possible_agents:
                team_id = env.match.agents[agent_id].team_id
                policy = policies[team_id]
                if isinstance(policy, ScriptedPolicy):
                    actions[agent_id] = policy.act_from_match(env.match, agent_id, infos[agent_id]["action_mask"])
                else:
                    actions[agent_id] = policy.act(agent_id, observations[agent_id], infos[agent_id])
            observations, rewards, terminations, truncations, infos = env.step(actions)
            for event in infos[env.possible_agents[0]]["events"]:
                writer.append_event(event)
            writer.append_metric(
                {
                    "step": env.match.step_count,
                    "score": dict(env.match.score),
                    "rewards": rewards,
                    "terminated": all(terminations.values()),
                    "truncated": all(truncations.values()),
                }
            )
        assert env.match is not None
        summary = {
            "winner": env.match.winner or "draw",
            "score": dict(env.match.score),
            "steps": env.match.step_count,
            "terminal_reason": env.match.terminal_reason or "unknown",
            "status": env.match.status.value,
            "capture_count": sum(env.match.score.values()),
            "rule_validity_failures": 0,
        }
        if env.match.status not in {MatchStatus.TERMINATED, MatchStatus.TRUNCATED}:
            summary["status"] = "incomplete"
        writer.complete(summary)
        return writer.metadata
    except KeyboardInterrupt:
        return writer.interrupted("keyboard interrupt")
    except Exception as exc:
        writer.fail(type(exc).__name__, str(exc))
        raise


def _build_policies(config: dict[str, Any]) -> dict[str, object]:
    policies: dict[str, object] = {}
    for team_id in ("red", "blue"):
        policy = config["policy_config"][team_id]
        policy_type = policy["type"]
        if policy_type == "random":
            policies[team_id] = RandomPolicy(seed=policy.get("seed"))
        elif policy_type == "scripted":
            policies[team_id] = ScriptedPolicy()
        elif policy_type == "vdn":
            policies[team_id] = VDNPolicy(
                checkpoint_path=policy.get("checkpoint_path"),
                seed=policy.get("seed"),
            )
        else:
            raise ValueError(f"policy type is not available for match runs yet: {policy_type}")
    return policies
