"""Bounded local training loop for VDN smoke runs."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from marlctf.artifacts import RunArtifactWriter
from marlctf.config import load_config
from marlctf.env.ctf_parallel_env import CTFParallelEnv
from marlctf.policies.scripted_policy import ScriptedPolicy
from marlctf.seeding import make_run_id, seed_everything
from marlctf.training.replay_buffer import EpisodeReplayBuffer, Transition
from marlctf.training.vdn import VDNPolicy


def run_training(
    config_path: str | Path,
    *,
    seed: int | None = None,
    artifact_dir: str | Path | None = None,
    episodes: int | None = None,
) -> dict[str, Any]:
    config = load_config(config_path)
    if seed is not None:
        config["seed"] = seed
    if artifact_dir is not None:
        config["artifact_dir"] = Path(artifact_dir).as_posix()
    if episodes is not None:
        config["training"]["episodes"] = episodes

    seed_everything(config["seed"])
    env = CTFParallelEnv(config)
    observations, infos = env.reset(seed=config["seed"])
    obs_dim = int(next(iter(observations.values())).shape[0])
    action_dim = int(env.action_space(env.possible_agents[0]).n)
    hidden_dim = int(config["training"].get("hidden_dim", 32))
    policy = VDNPolicy(obs_dim=obs_dim, action_dim=action_dim, hidden_dim=hidden_dim, seed=config["seed"])
    target_policy = VDNPolicy(obs_dim=obs_dim, action_dim=action_dim, hidden_dim=hidden_dim, seed=config["seed"])
    target_policy.network.load_state_dict(policy.network.state_dict())
    target_policy.network.eval()
    optimizer = torch.optim.Adam(policy.network.parameters(), lr=float(config["training"]["learning_rate"]))
    loss_fn = nn.MSELoss()
    buffer = EpisodeReplayBuffer(int(config["training"]["replay_capacity"]), seed=config["seed"])
    scripted = ScriptedPolicy()
    rng = np.random.default_rng(int(config["seed"]))

    run_id = make_run_id("train", config["scenario_id"], [config["seed"]])
    checkpoint_dir = Path(config["artifact_dir"]) / "checkpoints"
    latest_checkpoint = checkpoint_dir / "latest.pt"
    writer = RunArtifactWriter(
        config["artifact_dir"],
        {
            "run_id": run_id,
            "run_type": "train",
            "algorithm": "vdn",
            "config_path": Path(config_path).as_posix(),
            "scenario_id": config["scenario_id"],
            "seeds": [config["seed"]],
            "policy_ids": ["red:vdn", "blue:scripted"],
            "reward_config": dict(config["reward_config"]),
            "smoke_limits": {
                "episodes": config["training"]["episodes"],
                "max_steps": config["max_steps"],
                "max_runtime_minutes": config["training"].get("max_runtime_minutes"),
            },
            "checkpoint_paths": [],
        },
    )

    start = time.perf_counter()
    checkpoint_paths: list[str] = []
    try:
        for episode in range(1, int(config["training"]["episodes"]) + 1):
            observations, infos = env.reset(seed=int(config["seed"]) + episode)
            buffer.start_episode()
            episode_return = 0.0
            capture_count = 0
            episode_length = 0
            epsilon = _epsilon_for_episode(
                episode,
                int(config["training"]["episodes"]),
                float(config["training"].get("epsilon_start", 0.0)),
                float(config["training"].get("epsilon_end", 0.0)),
            )

            while env.agents:
                assert env.match is not None
                actions: dict[str, int] = {}
                for agent_id in env.possible_agents:
                    team_id = env.match.agents[agent_id].team_id
                    if team_id == "red":
                        actions[agent_id] = _epsilon_action(
                            policy,
                            agent_id,
                            observations[agent_id],
                            infos[agent_id],
                            epsilon,
                            rng,
                        )
                    else:
                        actions[agent_id] = scripted.act_from_match(env.match, agent_id, infos[agent_id]["action_mask"])

                next_observations, rewards, terminations, truncations, next_infos = env.step(actions)
                dones = {
                    agent_id: bool(terminations[agent_id] or truncations[agent_id])
                    for agent_id in env.possible_agents
                }
                buffer.append(
                    Transition(
                        observations=observations,
                        actions=actions,
                        rewards=rewards,
                        next_observations=next_observations,
                        dones=dones,
                        infos=infos,
                        next_infos=next_infos,
                    )
                )
                episode_return += sum(rewards[agent] for agent in rewards if agent.startswith("red_"))
                capture_count = sum(env.match.score.values())
                episode_length = env.match.step_count
                observations, infos = next_observations, next_infos

            buffer.end_episode()
            _train_one_batch(
                policy,
                target_policy,
                optimizer,
                loss_fn,
                buffer,
                int(config["training"]["batch_size"]),
                float(config["training"].get("gamma", 0.0)),
            )
            if episode % int(config["training"].get("target_update_interval", 1)) == 0:
                target_policy.network.load_state_dict(policy.network.state_dict())
            assert env.match is not None
            metric = {
                "episode": episode,
                "episode_return": episode_return,
                "epsilon": round(epsilon, 6),
                "winner": env.match.winner or "draw",
                "win": env.match.winner == "red",
                "capture_count": capture_count,
                "episode_length": episode_length,
                "buffer_size": len(buffer),
            }
            writer.append_metric(metric)

        checkpoint_paths.append(
            policy.save_checkpoint(
                latest_checkpoint,
                metadata={
                    "episode": int(config["training"]["episodes"]),
                    "algorithm": "vdn",
                    "scenario_id": config["scenario_id"],
                    "seed": config["seed"],
                    "runtime_seconds": round(time.perf_counter() - start, 4),
                },
            ).as_posix()
        )
        writer.set_checkpoint_paths(checkpoint_paths)
        summary = {
            "episodes": int(config["training"]["episodes"]),
            "runtime_seconds": round(time.perf_counter() - start, 4),
            "checkpoint_paths": checkpoint_paths,
            "final_buffer_size": len(buffer),
        }
        writer.complete(summary)
        return writer.metadata
    except KeyboardInterrupt:
        return writer.interrupted("keyboard interrupt")
    except Exception as exc:
        writer.fail(type(exc).__name__, str(exc))
        raise


def _train_one_batch(
    policy: VDNPolicy,
    target_policy: VDNPolicy,
    optimizer: torch.optim.Optimizer,
    loss_fn: nn.Module,
    buffer: EpisodeReplayBuffer,
    batch_size: int,
    gamma: float,
) -> None:
    sample = buffer.sample(batch_size)
    if not sample:
        return
    red_agents = ("red_0", "red_1", "red_2")
    obs = np.asarray(
        [[transition.observations[agent] for agent in red_agents] for transition in sample],
        dtype=np.float32,
    )
    actions = np.asarray(
        [[transition.actions[agent] for agent in red_agents] for transition in sample],
        dtype=np.int64,
    )
    rewards = np.asarray(
        [sum(transition.rewards[agent] for agent in red_agents) for transition in sample],
        dtype=np.float32,
    )
    next_obs = np.asarray(
        [[transition.next_observations[agent] for agent in red_agents] for transition in sample],
        dtype=np.float32,
    )
    not_done = np.asarray(
        [not all(transition.dones[agent] for agent in red_agents) for transition in sample],
        dtype=np.float32,
    )
    q_values = policy.network(torch.as_tensor(obs, dtype=torch.float32))
    selected = q_values.gather(-1, torch.as_tensor(actions).unsqueeze(-1)).squeeze(-1).sum(dim=-1)
    with torch.no_grad():
        next_q_values = target_policy.network(torch.as_tensor(next_obs, dtype=torch.float32))
        next_team_value = next_q_values.max(dim=-1).values.sum(dim=-1)
        target = torch.as_tensor(rewards, dtype=torch.float32) + (
            float(gamma) * torch.as_tensor(not_done, dtype=torch.float32) * next_team_value
        )
    loss = loss_fn(selected, target)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()


def _epsilon_for_episode(episode: int, total_episodes: int, start: float, end: float) -> float:
    if total_episodes <= 1:
        return end
    fraction = (episode - 1) / (total_episodes - 1)
    return start + fraction * (end - start)


def _epsilon_action(
    policy: VDNPolicy,
    agent_id: str,
    observation: np.ndarray,
    info: dict[str, Any],
    epsilon: float,
    rng: np.random.Generator,
) -> int:
    if rng.random() >= epsilon:
        return policy.act(agent_id, observation, info)
    mask = np.asarray(info["action_mask"])
    valid_actions = np.flatnonzero(mask > 0)
    return int(rng.choice(valid_actions))
