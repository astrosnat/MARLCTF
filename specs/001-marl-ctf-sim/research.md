# Research: Toy MARL CTF Simulation

## Decision: Implement a custom PettingZoo Parallel environment

**Rationale**: PettingZoo is designed as a standard API for multi-agent
reinforcement learning, and its Parallel API supports simultaneous action
submission. A 3v3 CTF match has simultaneous team actions each step, so a custom
Parallel environment matches the domain better than a turn-based API. The
environment will still be small enough to expose AEC conversion later if needed.

**Alternatives considered**:
- AEC-only environment: rejected because CTF movement and conflict resolution are
  simultaneous by design.
- Reusing PettingZoo KAZ directly: rejected because KAZ models Knights,
  Archers, and Zombies rather than two opposing CTF teams.

Source notes:
- PettingZoo documents Parallel environments for simultaneous actions:
  https://pettingzoo.farama.org/api/parallel/
- PettingZoo custom environment guidance covers custom logic and action masking:
  https://pettingzoo.farama.org/content/environment_creation/

## Decision: Use KAZ as a reference pattern, not the core game

**Rationale**: KAZ is useful because it is an official PettingZoo Butterfly
environment with discrete actions, vector observations, parallel usage examples,
and configurable agent counts. It does not implement flags, two adversarial
teams, tagging between teams, or a 3v3 CTF objective, so the CTF environment
must be custom.

**Alternatives considered**:
- Fork KAZ and mutate mechanics: rejected because CTF rules would replace most
  game semantics while preserving only API shape.
- Use Atari Flag Capture: rejected because it is not a clean custom 3v3 MARL
  environment and is less suitable for controlled local smoke training.

Source notes:
- KAZ supports Parallel API, discrete actions, and vectorized observation mode:
  https://pettingzoo.farama.org/environments/butterfly/knights_archers_zombies/

## Decision: Start with vector observations and discrete actions

**Rationale**: Vector observations are smaller and cheaper than image inputs,
which supports consumer-grade hardware and faster deterministic tests. Discrete
actions fit VDN/QMIX-style value decomposition methods and simplify invalid
action handling.

**Alternatives considered**:
- Image observations: rejected for MVP because they increase compute and make a
  30-minute local training smoke target harder to satisfy.
- Continuous actions: rejected because QMIX/VDN are value-based discrete-action
  methods and the CTF mechanics do not require continuous control.

Source notes:
- KAZ documents both vectorized and image-based observations and discrete action
  values: https://pettingzoo.farama.org/environments/butterfly/knights_archers_zombies/

## Decision: Use VDN for the first training smoke run

**Rationale**: VDN factorizes team value as an additive sum of per-agent values.
It is simpler than QMIX and is enough to validate that the custom environment,
shared team reward, replay, and local training loop work on consumer hardware.
The environment will expose global state so a QMIX mixer can be added later
without changing the environment contract.

**Alternatives considered**:
- QMIX first: deferred because it adds a state-conditioned monotonic mixing
  network and hypernetwork, increasing code and tuning complexity.
- Independent Q-learning only: rejected because the user asked for QMIX or VDN
  and because team-level value decomposition better matches cooperative team
  learning.

Source notes:
- QMIX/VDN are value-decomposition methods for centralized training with
  decentralized execution. QMIX uses discrete actions and global state during
  training: https://di-engine-docs.readthedocs.io/en/latest/12_policies/qmix.html
- PettingZoo's `state()` is intended for global views used by centralized
  training methods like QMIX:
  https://pettingzoo.farama.org/_modules/pettingzoo/utils/env/

## Decision: Store reproducibility artifacts as local JSONL/JSON files

**Rationale**: Local files are simple, inspectable, versionable, and adequate for
toy experiments. JSON metadata and JSONL event/metric streams can be validated in
tests and read without a database.

**Alternatives considered**:
- SQLite: deferred because the first scope does not need querying beyond one run.
- TensorBoard-only logging: rejected as the sole artifact because structured
  JSON is easier to test and inspect in automated checks.

## Decision: Consumer-grade defaults are CPU-capable smoke defaults

**Rationale**: The success criteria prioritize a local smoke match, smoke
training run, and smoke evaluation over high performance. Defaults will use
small maps, limited steps, few seeds, compact networks, and optional checkpoint
output.

**Alternatives considered**:
- GPU-required training: rejected because it conflicts with consumer-grade
  hardware constraints.
- Large-scale parallel rollout: deferred because it adds orchestration
  complexity and is not necessary for the first feature.
