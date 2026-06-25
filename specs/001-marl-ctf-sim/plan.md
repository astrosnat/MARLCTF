# Implementation Plan: Toy MARL CTF Simulation

**Branch**: `001-marl-ctf-sim` | **Date**: 2026-06-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-marl-ctf-sim/spec.md`

## Summary

Build a toy 3v3 capture-the-flag multi-agent reinforcement learning simulation
that runs locally on consumer-grade hardware. The implementation will expose a
custom PettingZoo Parallel environment with KAZ-inspired vector observations,
discrete actions, deterministic seeding, structured run artifacts, random and
scripted baselines, a VDN smoke trainer, and an evaluation flow that can compare
baseline and learned team policies.

KAZ is used as the PettingZoo reference pattern, not as the core environment,
because PettingZoo KAZ is Knights-Archers-Zombies and does not model opposing
3v3 teams or flags. The custom environment will still preserve compatibility
with QMIX-style centralized training by exposing a global state contract.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: PettingZoo, Gymnasium, NumPy, PyTorch, PyYAML or TOML config parsing, pytest  
**Storage**: Local filesystem artifacts for configs, metrics, logs, and optional checkpoints  
**Testing**: pytest plus PettingZoo environment API tests and deterministic smoke tests  
**Target Platform**: Consumer-grade laptop/desktop, Windows first with cross-platform Python paths  
**Project Type**: Single Python package with CLI entry points and reusable environment/training modules  
**Performance Goals**: Complete one default smoke match in under 2 minutes; complete 100 seeded rule-validity matches with zero failures; complete default training smoke run in under 30 minutes  
**Constraints**: Exactly 3v3 for initial scope; discrete action spaces; deterministic reset when seed is supplied; CPU-capable defaults; no production-scale distributed training in this feature  
**Scale/Scope**: One custom toy CTF scenario, six agents, random/scripted baselines, VDN smoke trainer, QMIX-compatible global state, evaluation over at least 10 seeds

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Reproducibility**: PASS. Plan requires seeded scenarios, local config files,
  run metadata, deterministic smoke checks, and artifact output for matches,
  training, and evaluation.
- **Agent-Environment Contracts**: PASS. Contracts define observation/action
  spaces, rewards, global state, lifecycle events, run artifacts, and CLI inputs.
- **Test Strategy**: PASS. Planning includes PettingZoo API tests, mechanics
  tests, contract tests, deterministic regression tests, smoke training tests,
  and evaluation artifact tests.
- **Training Evidence**: PASS. Learning evidence compares VDN candidate policy
  against random/scripted baselines using win rate, capture count, average
  return, episode length, runtime, and rule-validity failures over fixed seeds.
- **Simplicity**: PASS. The first trainer uses VDN for lower implementation and
  compute cost. QMIX is deferred to a compatible interface rather than a second
  full trainer in the initial implementation.

Post-design re-check: PASS. The data model, CLI contracts, environment contract,
and quickstart preserve the same reproducibility, testing, evidence, and
simplicity constraints.

## Project Structure

### Documentation (this feature)

```text
specs/001-marl-ctf-sim/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- cli.md
|   `-- environment.md
`-- checklists/
    `-- requirements.md
```

### Source Code (repository root)

```text
pyproject.toml

src/
`-- marlctf/
    |-- __init__.py
    |-- cli.py
    |-- config.py
    |-- env/
    |   |-- __init__.py
    |   |-- ctf_parallel_env.py
    |   |-- mechanics.py
    |   |-- observations.py
    |   `-- rewards.py
    |-- policies/
    |   |-- __init__.py
    |   |-- random_policy.py
    |   `-- scripted_policy.py
    |-- training/
    |   |-- __init__.py
    |   |-- replay_buffer.py
    |   |-- vdn.py
    |   `-- runner.py
    |-- evaluation/
    |   |-- __init__.py
    |   |-- evaluator.py
    |   `-- metrics.py
    `-- artifacts.py

tests/
|-- contract/
|   |-- test_cli_contract.py
|   `-- test_environment_contract.py
|-- integration/
|   |-- test_seeded_match.py
|   |-- test_training_smoke.py
|   `-- test_evaluation_smoke.py
`-- unit/
    |-- test_mechanics.py
    |-- test_observations.py
    |-- test_rewards.py
    `-- test_artifacts.py

configs/
|-- smoke_match.yml
|-- smoke_train.yml
`-- smoke_eval.yml

artifacts/
`-- .gitkeep
```

**Structure Decision**: Use a single Python package because the feature is a
local simulation library plus CLI, not a web or mobile application. Environment
mechanics, policies, training, evaluation, and artifacts are separated so tests
can target each constitution-governed contract without adding service layers.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Custom PettingZoo environment instead of directly using KAZ | The feature requires opposing 3v3 CTF teams, flags, tagging, scoring, and deterministic CTF-specific artifacts | KAZ is Knights-Archers-Zombies with cooperative PvE dynamics and four default agents, so it cannot satisfy the 3v3 CTF match requirements |
| VDN trainer plus QMIX-compatible global state | The user requested QMIX or VDN, and the constitution requires algorithm settings to be reproducible | Implementing both full QMIX and VDN in the first pass increases complexity; VDN is the MVP trainer while the global state contract preserves a path to QMIX |
