# Quickstart: Toy MARL CTF Simulation

This quickstart verifies the planned user path before implementation tasks are
generated.

## Prerequisites

- Python 3.11 or newer.
- A local virtual environment.
- Consumer-grade laptop or desktop hardware.

## Install

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

## Run Contract and Mechanics Tests

```powershell
pytest tests/contract tests/unit
```

Expected result:
- PettingZoo environment contract tests pass.
- Mechanics, reward, observation, and artifact tests pass.

## Run One Seeded Match

```powershell
marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/smoke-match
```

Expected result:
- A 3v3 match reaches a terminal or truncated outcome in under 2 minutes.
- `artifacts/smoke-match/run.json` includes scenario, seed, policies, final
  score, winner, terminal reason, and runtime.
- `events.jsonl` records movement, tags, flag events, invalid actions, scores,
  and terminal event.

## Verify Determinism

```powershell
marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/repro-a
marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/repro-b
```

Expected result:
- Initial state and deterministic baseline-policy outcome match across both
  runs.

## Run Local Training Smoke

```powershell
marlctf train --config configs/smoke_train.yml --seed 7 --artifact-dir artifacts/smoke-train
```

Expected result:
- Training completes within 30 minutes using default smoke limits.
- `run.json` records algorithm, seed, scenario, reward config, episode count,
  runtime, and checkpoint metadata.
- `metrics.jsonl` includes episode return, win/loss, capture count, and episode
  length.

## Run Evaluation

```powershell
marlctf evaluate --config configs/smoke_eval.yml --artifact-dir artifacts/smoke-eval
```

Expected result:
- Evaluation compares baseline and candidate policy configurations across at
  least 10 seeds.
- `comparison.json` reports win rate, capture count, average return, episode
  length, rule-validity failures, and whether the acceptance threshold passed.

## Troubleshooting Checks

- If a run exceeds the smoke time budget, reduce episode count or max steps in
  the smoke config.
- If determinism checks fail, inspect `run.json` for seed, scenario, policy, and
  reward-config differences.
- If contract tests fail, fix the environment contract before training changes.
