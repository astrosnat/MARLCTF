# Tasks: Toy MARL CTF Simulation

**Input**: Design documents from `/specs/001-marl-ctf-sim/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by the MARLCTF constitution and this feature's contracts for
simulation mechanics, agent-environment contracts, training/evaluation pipelines,
determinism, and reproducibility artifacts.

**Organization**: Tasks are grouped by user story so each story can be implemented
and tested independently after the shared foundation is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not
  depend on incomplete tasks.
- **[Story]**: User story label for story phases only.
- Every task includes an exact file path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the Python package skeleton, dependency metadata, smoke
configuration files, and test directories used by all stories.

- [X] T001 Create package, test, config, and artifact directories in `src/marlctf/`, `tests/`, `configs/`, and `artifacts/`
- [X] T002 Create Python project metadata with runtime and dev dependencies in `pyproject.toml`
- [X] T003 [P] Create package exports and version metadata in `src/marlctf/__init__.py`
- [X] T004 [P] Create empty module initializers in `src/marlctf/env/__init__.py`, `src/marlctf/policies/__init__.py`, `src/marlctf/training/__init__.py`, and `src/marlctf/evaluation/__init__.py`
- [X] T005 [P] Add artifact directory placeholder in `artifacts/.gitkeep`
- [X] T006 [P] Create default smoke match configuration in `configs/smoke_match.yml`
- [X] T007 [P] Create default smoke training configuration in `configs/smoke_train.yml`
- [X] T008 [P] Create default smoke evaluation configuration in `configs/smoke_eval.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared models, config loading, artifact writing, and core
contract fixtures that every user story depends on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T009 Define shared dataclasses and enums for Match, Team, Agent, Flag, Scenario, Observation, GlobalState, PolicyConfig, RunArtifact, and MatchEvent in `src/marlctf/models.py`
- [X] T010 Implement config loading, defaults, and validation for smoke YAML files in `src/marlctf/config.py`
- [X] T011 Implement deterministic seed utilities and run id creation in `src/marlctf/seeding.py`
- [X] T012 Implement JSON/JSONL run artifact writer and interrupted-run handling in `src/marlctf/artifacts.py`
- [X] T013 [P] Create reusable scenario and action fixtures for contract tests in `tests/conftest.py`
- [X] T014 [P] Add config validation unit tests for all smoke config files in `tests/unit/test_config.py`
- [X] T015 [P] Add artifact writer unit tests for `run.json`, `metrics.jsonl`, and `events.jsonl` in `tests/unit/test_artifacts.py`

**Checkpoint**: Shared data, config, seed, and artifact infrastructure exists and
can be tested without the environment implementation.

---

## Phase 3: User Story 1 - Run a 3v3 CTF Match (Priority: P1) MVP

**Goal**: Run a complete deterministic 3v3 capture-the-flag match with random or
scripted policies and inspectable artifacts.

**Independent Test**: Start a match with six agents and a fixed scenario, run it
until termination or truncation, and verify state transitions, rewards, score,
events, and final artifacts follow the documented rules.

### Tests for User Story 1 (write first)

- [X] T016 [P] [US1] Add PettingZoo Parallel API, reset, space stability, action mask, and global state contract tests in `tests/contract/test_environment_contract.py`
- [X] T017 [P] [US1] Add mechanics unit tests for movement bounds, blocked cells, simultaneous collisions, flag pickup, flag return, scoring, tagging, respawn, and truncation in `tests/unit/test_mechanics.py`
- [X] T018 [P] [US1] Add observation and global-state shape tests for hidden entities, score features, action masks, and fixed scenario shapes in `tests/unit/test_observations.py`
- [X] T019 [P] [US1] Add reward tests for step penalty, flag pickup, tag, score, carrier tagged, terminal win, and terminal loss in `tests/unit/test_rewards.py`
- [X] T020 [P] [US1] Add deterministic seeded match integration test for two identical scripted-policy runs in `tests/integration/test_seeded_match.py`
- [X] T021 [P] [US1] Add CLI contract tests for `marlctf match` options, exit codes, and required artifacts in `tests/contract/test_cli_contract.py`

### Implementation for User Story 1

- [X] T022 [P] [US1] Implement CTF movement, collision resolution, tag resolution, flag state transitions, scoring, truncation, and terminal rules in `src/marlctf/env/mechanics.py`
- [X] T023 [P] [US1] Implement fixed-shape local observations, action masks, and QMIX-compatible global state conversion in `src/marlctf/env/observations.py`
- [X] T024 [P] [US1] Implement configurable reward calculation for match events and terminal outcomes in `src/marlctf/env/rewards.py`
- [X] T025 [US1] Implement the PettingZoo Parallel environment `marlctf_3v3_v0` in `src/marlctf/env/ctf_parallel_env.py`
- [X] T026 [P] [US1] Implement random baseline team policy in `src/marlctf/policies/random_policy.py`
- [X] T027 [P] [US1] Implement scripted baseline team policy for deterministic smoke matches in `src/marlctf/policies/scripted_policy.py`
- [X] T028 [US1] Implement match runner that connects environment, policies, seeds, and artifact output in `src/marlctf/runner.py`
- [X] T029 [US1] Implement `marlctf match` CLI command in `src/marlctf/cli.py`
- [X] T030 [US1] Wire package console entry point for `marlctf` in `pyproject.toml`

**Checkpoint**: `marlctf match --config configs/smoke_match.yml --seed 42
--artifact-dir artifacts/smoke-match` completes and writes valid artifacts.

---

## Phase 4: User Story 2 - Train Cooperative Agents Locally (Priority: P2)

**Goal**: Run a bounded local VDN training smoke run against the 3v3 environment
and produce reproducible training metrics and optional checkpoints.

**Independent Test**: Run the smoke training command with a fixed seed and verify
completion within the configured limits, metrics output, run metadata, and
checkpoint metadata.

### Tests for User Story 2 (write first)

- [X] T031 [P] [US2] Add replay buffer unit tests for transition shape, episode boundary handling, sampling, and seed determinism in `tests/unit/test_replay_buffer.py`
- [X] T032 [P] [US2] Add VDN model unit tests for per-agent Q output shapes, team value sum, masked action selection, and checkpoint metadata in `tests/unit/test_vdn.py`
- [X] T033 [P] [US2] Add training runner integration smoke test for metrics, runtime budget, and artifact output in `tests/integration/test_training_smoke.py`
- [X] T034 [P] [US2] Add CLI contract tests for `marlctf train` options, exit codes, and required training artifacts in `tests/contract/test_cli_train.py`

### Implementation for User Story 2

- [X] T035 [P] [US2] Implement episode replay buffer and transition schema in `src/marlctf/training/replay_buffer.py`
- [X] T036 [P] [US2] Implement compact PyTorch VDN agent network, team-value summation, masked action selection, and checkpoint save/load in `src/marlctf/training/vdn.py`
- [X] T037 [US2] Implement bounded training loop with exploration schedule, target updates, metric logging, and interrupted-run handling in `src/marlctf/training/runner.py`
- [X] T038 [US2] Add VDN policy loading and inference adapter for matches in `src/marlctf/policies/vdn_policy.py`
- [X] T039 [US2] Implement `marlctf train` CLI command and config validation in `src/marlctf/cli.py`
- [X] T040 [US2] Ensure training run metadata records algorithm, seed, scenario, reward config, smoke limits, runtime, metrics path, and checkpoint paths in `src/marlctf/artifacts.py`

**Checkpoint**: `marlctf train --config configs/smoke_train.yml --seed 7
--artifact-dir artifacts/smoke-train` completes within the smoke budget and
writes training metrics.

---

## Phase 5: User Story 3 - Evaluate and Compare Team Policies (Priority: P3)

**Goal**: Compare random, scripted, and learned policies over fixed seeds and
report aggregate evidence that indicates whether the candidate policy passes the
configured threshold.

**Independent Test**: Run an evaluation batch across at least 10 seeds and verify
aggregate win rate, capture count, average return, episode length, rule-validity
failures, and pass/fail threshold output.

### Tests for User Story 3 (write first)

- [ ] T041 [P] [US3] Add evaluation metrics unit tests for win rate, capture count, average return, episode length, rule-validity failures, and threshold pass/fail in `tests/unit/test_evaluation_metrics.py`
- [ ] T042 [P] [US3] Add evaluation runner integration smoke test for fixed seed sets and `comparison.json` output in `tests/integration/test_evaluation_smoke.py`
- [ ] T043 [P] [US3] Add CLI contract tests for `marlctf evaluate` options, exit codes, and required evaluation artifacts in `tests/contract/test_cli_evaluate.py`

### Implementation for User Story 3

- [ ] T044 [P] [US3] Implement aggregate evaluation metric calculations in `src/marlctf/evaluation/metrics.py`
- [ ] T045 [US3] Implement evaluation runner for baseline-versus-candidate policy batches over fixed seeds in `src/marlctf/evaluation/evaluator.py`
- [ ] T046 [US3] Implement `marlctf evaluate` CLI command and comparison artifact writing in `src/marlctf/cli.py`
- [ ] T047 [US3] Ensure evaluation artifacts include per-seed metrics, aggregate summary, `comparison.json`, and acceptance threshold result in `src/marlctf/artifacts.py`

**Checkpoint**: `marlctf evaluate --config configs/smoke_eval.yml
--artifact-dir artifacts/smoke-eval` writes `comparison.json` and aggregate
metrics for at least 10 seeds.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete quickstart, harden documentation, and run the
full reproducibility evidence required by the constitution.

- [ ] T048 [P] Update README with install, match, train, evaluate, and artifact inspection commands in `README.md`
- [ ] T049 [P] Document default scenario rules, action ids, rewards, observation features, and state features in `docs/scenario.md`
- [ ] T050 [P] Add generated artifact examples or schemas for `run.json`, `metrics.jsonl`, `events.jsonl`, and `comparison.json` in `docs/artifacts.md`
- [ ] T051 Run 100 seeded rule-validity smoke matches and record the result in `artifacts/validation/rule_validity_summary.json`
- [ ] T052 Run quickstart commands end-to-end and record the outcome in `artifacts/validation/quickstart_summary.json`
- [ ] T053 Run the full pytest suite and record the final test result in `artifacts/validation/test_summary.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational. This is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and uses US1 environment and match runner.
- **User Story 3 (Phase 5)**: Depends on Foundational and uses US1 environment plus US2 learned-policy adapter when evaluating trained candidates.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 - Run a 3v3 CTF Match**: Required first for a playable environment and artifacts.
- **US2 - Train Cooperative Agents Locally**: Requires US1 environment, observations, rewards, policies, and artifacts.
- **US3 - Evaluate and Compare Team Policies**: Can evaluate random/scripted policies after US1; full candidate evaluation depends on US2 policy adapter.

### Within Each User Story

- Write required tests first and confirm they fail before implementation.
- Implement models and low-level mechanics before runners and CLI wiring.
- Complete each story checkpoint before starting the next story.
- Keep config, seed, and artifact changes synchronized with tests.

---

## Parallel Opportunities

- Setup tasks T003-T008 can run in parallel after T001-T002.
- Foundational tests T013-T015 can run in parallel after T009-T012 interfaces are drafted.
- US1 tests T016-T021 can be written in parallel.
- US1 modules T022-T024 and policies T026-T027 can be implemented in parallel before T025/T028/T029.
- US2 tests T031-T034 can be written in parallel.
- US2 implementation T035-T036 can run in parallel before T037-T040.
- US3 tests T041-T043 can be written in parallel.
- US3 metrics T044 can run before T045-T047.
- Polish docs T048-T050 can run in parallel before validation runs T051-T053.

---

## Parallel Example: User Story 1

```text
Task: "T016 [P] [US1] Add PettingZoo Parallel API, reset, space stability, action mask, and global state contract tests in tests/contract/test_environment_contract.py"
Task: "T017 [P] [US1] Add mechanics unit tests for movement bounds, blocked cells, simultaneous collisions, flag pickup, flag return, scoring, tagging, respawn, and truncation in tests/unit/test_mechanics.py"
Task: "T018 [P] [US1] Add observation and global-state shape tests for hidden entities, score features, action masks, and fixed scenario shapes in tests/unit/test_observations.py"
Task: "T019 [P] [US1] Add reward tests for step penalty, flag pickup, tag, score, carrier tagged, terminal win, and terminal loss in tests/unit/test_rewards.py"
```

## Parallel Example: User Story 2

```text
Task: "T031 [P] [US2] Add replay buffer unit tests for transition shape, episode boundary handling, sampling, and seed determinism in tests/unit/test_replay_buffer.py"
Task: "T032 [P] [US2] Add VDN model unit tests for per-agent Q output shapes, team value sum, masked action selection, and checkpoint metadata in tests/unit/test_vdn.py"
Task: "T033 [P] [US2] Add training runner integration smoke test for metrics, runtime budget, and artifact output in tests/integration/test_training_smoke.py"
```

## Parallel Example: User Story 3

```text
Task: "T041 [P] [US3] Add evaluation metrics unit tests for win rate, capture count, average return, episode length, rule-validity failures, and threshold pass/fail in tests/unit/test_evaluation_metrics.py"
Task: "T042 [P] [US3] Add evaluation runner integration smoke test for fixed seed sets and comparison.json output in tests/integration/test_evaluation_smoke.py"
Task: "T043 [P] [US3] Add CLI contract tests for marlctf evaluate options, exit codes, and required evaluation artifacts in tests/contract/test_cli_evaluate.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 tests and implementation.
3. Validate `marlctf match` with `configs/smoke_match.yml`.
4. Stop and inspect match artifacts before training work.

### Incremental Delivery

1. Deliver US1 as a valid deterministic 3v3 CTF match.
2. Add US2 as a bounded local VDN training smoke run.
3. Add US3 as baseline-versus-candidate evaluation evidence.
4. Complete Phase 6 validation and documentation.

### Format Validation

- All executable tasks use `- [ ] T###` checklist format.
- All user-story phase tasks include `[US1]`, `[US2]`, or `[US3]`.
- Setup, foundational, and polish tasks omit user-story labels.
- Each task names at least one concrete file path.
