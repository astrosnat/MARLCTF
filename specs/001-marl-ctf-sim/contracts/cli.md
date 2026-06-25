# CLI Contract: Toy MARL CTF Simulation

## Purpose

Define the user-facing commands used by quickstart, smoke tests, and downstream
task generation.

## Command: `marlctf match`

Runs one 3v3 CTF match.

Required options:
- `--config <path>`: match configuration file.

Optional options:
- `--seed <int>`: override config seed.
- `--policy-red <policy_id>`: red team policy.
- `--policy-blue <policy_id>`: blue team policy.
- `--artifact-dir <path>`: output directory.
- `--render <none|ansi|human>`: rendering mode.

Exit codes:
- `0`: completed match.
- `1`: config or contract validation failure.
- `2`: runtime failure or interrupted run.

Required artifacts:
- `run.json`: run metadata and summary.
- `metrics.jsonl`: step or episode metrics.
- `events.jsonl`: rule-relevant events.

## Command: `marlctf train`

Runs a bounded local training smoke run.

Required options:
- `--config <path>`: training configuration file.

Optional options:
- `--seed <int>`: override training seed.
- `--artifact-dir <path>`: output directory.
- `--checkpoint-every <episodes>`: checkpoint cadence.

Exit codes:
- `0`: completed training run.
- `1`: config or contract validation failure.
- `2`: runtime failure or interrupted run.

Required artifacts:
- `run.json`: run metadata and summary.
- `metrics.jsonl`: episode metrics.
- optional `checkpoints/`: learned policy snapshots.

## Command: `marlctf evaluate`

Compares policy configurations over a fixed seed set.

Required options:
- `--config <path>`: evaluation configuration file.

Optional options:
- `--artifact-dir <path>`: output directory.
- `--candidate <policy_id>`: candidate policy override.
- `--baseline <policy_id>`: baseline policy override.

Exit codes:
- `0`: completed evaluation and wrote summary.
- `1`: config or contract validation failure.
- `2`: runtime failure or interrupted run.

Required artifacts:
- `run.json`: run metadata and aggregate summary.
- `metrics.jsonl`: per-seed metrics.
- `comparison.json`: baseline versus candidate comparison.

## Config Contract

All commands MUST accept structured config with:
- `scenario_id`
- `seed` or `seeds`
- `max_steps`
- `reward_config`
- `policy_config`
- `artifact_dir`
- command-specific smoke limits

Config validation MUST fail before a run starts when required fields are missing
or inconsistent with the 3v3 scope.
