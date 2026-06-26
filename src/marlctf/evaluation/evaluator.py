"""Evaluation runner for fixed-seed policy comparisons."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from marlctf.artifacts import RunArtifactWriter
from marlctf.config import load_config, validate_config
from marlctf.env.ctf_parallel_env import CTFParallelEnv
from marlctf.evaluation.metrics import build_comparison
from marlctf.models import MatchStatus
from marlctf.policies.random_policy import RandomPolicy
from marlctf.policies.scripted_policy import ScriptedPolicy
from marlctf.policies.vdn_policy import VDNPolicy
from marlctf.seeding import make_run_id


def run_evaluation(
    config_path: str | Path,
    *,
    artifact_dir: str | Path | None = None,
    candidate: str | None = None,
    baseline: str | None = None,
) -> dict[str, Any]:
    config = load_config(config_path)
    if artifact_dir is not None:
        config["artifact_dir"] = Path(artifact_dir).as_posix()
    if candidate is not None:
        _override_policy(config, "candidate", candidate)
    if baseline is not None:
        _override_policy(config, "baseline", baseline)
    validate_config(config)

    seeds = [int(seed) for seed in config["seeds"]]
    candidate_team = str(config["candidate"].get("team", "red"))
    baseline_team = str(config["baseline"].get("team", "blue"))
    policy_ids = [
        f"{candidate_team}:{config['policy_config'][candidate_team]['type']}",
        f"{baseline_team}:{config['policy_config'][baseline_team]['type']}",
    ]
    writer = RunArtifactWriter(
        config["artifact_dir"],
        {
            "run_id": make_run_id("evaluate", config["scenario_id"], seeds),
            "run_type": "evaluate",
            "config_path": Path(config_path).as_posix(),
            "scenario_id": config["scenario_id"],
            "seeds": seeds,
            "policy_ids": policy_ids,
            "candidate": config["candidate"],
            "baseline": config["baseline"],
            "reward_config": dict(config["reward_config"]),
            "smoke_limits": {"seed_count": len(seeds), "max_steps": config["max_steps"]},
        },
    )

    results: list[dict[str, Any]] = []
    try:
        for seed in seeds:
            result = _run_seed(config, seed)
            results.append(result)
            writer.append_metric(result)

        comparison = build_comparison(
            results,
            candidate_team=candidate_team,
            baseline_team=baseline_team,
            acceptance=dict(config["metrics"]["acceptance"]),
        )
        comparison_path = writer.write_json_artifact("comparison.json", comparison)
        summary = {
            "seed_count": len(seeds),
            "candidate": comparison["candidate"],
            "baseline": comparison["baseline"],
            "acceptance": comparison["acceptance"],
            "comparison_path": comparison_path.as_posix(),
        }
        writer.complete(summary)
        return writer.metadata
    except KeyboardInterrupt:
        return writer.interrupted("keyboard interrupt")
    except Exception as exc:
        writer.fail(type(exc).__name__, str(exc))
        raise


def _run_seed(config: dict[str, Any], seed: int) -> dict[str, Any]:
    env = CTFParallelEnv(config)
    observations, infos = env.reset(seed=seed)
    policies = _build_policies(config, seed)
    returns = {"red": 0.0, "blue": 0.0}
    rule_failures = 0

    while env.agents:
        assert env.match is not None
        actions: dict[str, int] = {}
        for agent_id in env.possible_agents:
            team_id = env.match.agents[agent_id].team_id
            policy = policies[team_id]
            if isinstance(policy, ScriptedPolicy):
                actions[agent_id] = policy.act_from_match(env.match, agent_id, infos[agent_id]["action_mask"])
            else:
                actions[agent_id] = policy.act(agent_id, observations[agent_id], infos[agent_id])

        observations, rewards, terminations, truncations, infos = env.step(actions)
        del terminations, truncations
        for agent_id, reward in rewards.items():
            team_id = agent_id.split("_", maxsplit=1)[0]
            returns[team_id] += float(reward)
        rule_failures += sum(1 for info in infos.values() if info.get("invalid_action") is not None)

    assert env.match is not None
    status = env.match.status.value
    if env.match.status not in {MatchStatus.TERMINATED, MatchStatus.TRUNCATED}:
        status = "incomplete"
    return {
        "seed": seed,
        "winner": env.match.winner or "draw",
        "score": dict(env.match.score),
        "returns": {team_id: round(value, 6) for team_id, value in returns.items()},
        "episode_length": env.match.step_count,
        "terminal_reason": env.match.terminal_reason or "unknown",
        "status": status,
        "rule_validity_failures": rule_failures,
    }


def _build_policies(config: dict[str, Any], seed: int) -> dict[str, object]:
    policies: dict[str, object] = {}
    for offset, team_id in enumerate(("red", "blue")):
        policy = config["policy_config"][team_id]
        policy_type = policy["type"]
        policy_seed = int(policy.get("seed", seed + offset))
        if policy_type == "random":
            policies[team_id] = RandomPolicy(seed=policy_seed)
        elif policy_type == "scripted":
            policies[team_id] = ScriptedPolicy()
        elif policy_type == "vdn":
            policies[team_id] = VDNPolicy(checkpoint_path=policy.get("checkpoint_path"), seed=policy_seed)
        else:
            raise ValueError(f"unsupported evaluation policy type: {policy_type}")
    return policies


def _override_policy(config: dict[str, Any], section: str, policy_type: str) -> None:
    team_id = str(config[section].get("team", "red" if section == "candidate" else "blue"))
    config[section]["policy"] = {"type": policy_type}
    config["policy_config"][team_id]["type"] = policy_type
    if policy_type != "vdn":
        config["policy_config"][team_id].pop("checkpoint_path", None)
