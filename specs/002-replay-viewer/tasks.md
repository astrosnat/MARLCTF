# Tasks: Replay Viewer

**Input**: Design documents from `/specs/002-replay-viewer/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by the MARLCTF constitution because this feature changes
run artifacts, CLI behavior, visualization contracts, and training artifact
options. Tests must be written before or with implementation for each story.

**Organization**: Tasks are grouped by user story so each story can be
implemented and tested independently after shared replay/viewer foundations are
complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: User story label for story phases only.
- Every task includes an exact file path.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directories and package/static-asset scaffolding for replay
artifacts and the local viewer.

- [X] T001 Create replay/viewer package directories in `src/marlctf/viewer/`, `src/marlctf/viewer/static/`, and `tests/viewer/`
- [X] T002 [P] Create viewer package initializer in `src/marlctf/viewer/__init__.py`
- [X] T003 [P] Create placeholder static viewer files in `src/marlctf/viewer/static/index.html`, `src/marlctf/viewer/static/app.js`, and `src/marlctf/viewer/static/styles.css`
- [X] T004 [P] Ensure viewer static assets are packaged in `pyproject.toml`
- [X] T005 [P] Create sample viewer manifest placeholder in `src/marlctf/viewer/static/sample-manifest.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared replay snapshot, artifact, and viewer-data parsing
primitives that every story depends on.

**CRITICAL**: No user story work can begin until this phase is complete.

### Foundational Tests

- [ ] T006 [P] Add replay snapshot unit tests for schema fields, agent/flag coordinates, terminal fields, and ordered steps in `tests/unit/test_replay_snapshots.py`
- [ ] T007 [P] Add replay JSONL artifact unit tests for append/read behavior and metadata path handling in `tests/unit/test_replay_artifacts.py`
- [ ] T008 [P] Add viewer data parsing unit tests for run directories, replay files, metrics files, comparison files, and missing optional artifacts in `tests/unit/test_viewer_data_parsing.py`

### Foundational Implementation

- [ ] T009 Implement replay snapshot builders and validators in `src/marlctf/replay.py`
- [ ] T010 Extend artifact writer with replay JSONL and generic viewer artifact helpers in `src/marlctf/artifacts.py`
- [ ] T011 Implement viewer artifact discovery and JSON/JSONL parsing helpers in `src/marlctf/viewer/data.py`
- [ ] T012 Implement shared viewer error types and validation result objects in `src/marlctf/viewer/data.py`
- [ ] T013 Update artifact documentation with replay artifact schema references in `docs/artifacts.md`

**Checkpoint**: Replay snapshots can be built, validated, written, and discovered without the UI or run-loop integration.

---

## Phase 3: User Story 1 - Inspect A Completed Match Replay (Priority: P1) MVP

**Goal**: Run a smoke match, produce `replay.jsonl`, and inspect the replay in a local viewer with grid, agents, flags, score, steps, and events.

**Independent Test**: Run one deterministic match, open the produced replay in the viewer, and verify the board, agents, flags, score, step counter, terminal outcome, and event list match artifacts.

### Tests for User Story 1

- [ ] T014 [P] [US1] Add replay artifact contract tests for required snapshot fields and final snapshot consistency in `tests/contract/test_replay_artifact_contract.py`
- [ ] T015 [P] [US1] Add CLI contract tests for `marlctf match` replay metadata and `marlctf viewer --artifact` behavior in `tests/contract/test_cli_viewer.py`
- [ ] T016 [P] [US1] Add match replay integration smoke test for initial snapshot, per-step snapshots, terminal snapshot, and artifact size in `tests/integration/test_match_replay_smoke.py`
- [ ] T017 [P] [US1] Add viewer replay parser/renderer contract tests for controls, grid labels, agents, flags, score, step text, and events in `tests/contract/test_viewer_contract.py`

### Implementation for User Story 1

- [ ] T018 [US1] Write initial and post-step match replay snapshots from the match runner in `src/marlctf/runner.py`
- [ ] T019 [US1] Persist match replay metadata fields `replay_available` and `replay_paths` in `src/marlctf/artifacts.py`
- [ ] T020 [US1] Implement viewer CLI command options `--artifact`, `--host`, `--port`, and `--no-open` in `src/marlctf/cli.py`
- [ ] T021 [P] [US1] Implement replay board drawing and state rendering in `src/marlctf/viewer/static/app.js`
- [ ] T022 [P] [US1] Implement viewer replay controls, speed selection, step scrubber, and event list updates in `src/marlctf/viewer/static/app.js`
- [ ] T023 [P] [US1] Implement accessible replay layout and visual styling in `src/marlctf/viewer/static/index.html` and `src/marlctf/viewer/static/styles.css`
- [ ] T024 [US1] Add viewer smoke harness or static rendering validation in `tests/integration/test_viewer_smoke.py`
- [ ] T025 [US1] Document match replay usage and viewer launch commands in `docs/viewer.md`

**Checkpoint**: `marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/viewer-match` writes `replay.jsonl`, and `marlctf viewer --artifact artifacts/viewer-match` can inspect it.

---

## Phase 4: User Story 2 - Understand Training Progress With Charts (Priority: P2)

**Goal**: Open a training run and display compact charts for available episode metric series from `metrics.jsonl`.

**Independent Test**: Run a bounded training smoke run, open its artifact directory, and verify training charts and summary text match the recorded metrics.

### Tests for User Story 2

- [ ] T026 [P] [US2] Add training metrics parser tests for returns, winners, captures, episode length, epsilon, buffer size, and missing optional fields in `tests/unit/test_viewer_data_parsing.py`
- [ ] T027 [P] [US2] Add viewer contract tests for training chart series availability and unavailable-series messaging in `tests/contract/test_viewer_contract.py`
- [ ] T028 [P] [US2] Add training chart integration smoke test using a 3-episode smoke training run in `tests/integration/test_viewer_smoke.py`

### Implementation for User Story 2

- [ ] T029 [US2] Implement training metric series extraction in `src/marlctf/viewer/data.py`
- [ ] T030 [P] [US2] Implement chart drawing utilities for line, bar, and point series in `src/marlctf/viewer/static/app.js`
- [ ] T031 [US2] Implement training charts view, series toggles, summary context, and missing-series states in `src/marlctf/viewer/static/app.js`
- [ ] T032 [P] [US2] Add training chart markup and styles in `src/marlctf/viewer/static/index.html` and `src/marlctf/viewer/static/styles.css`
- [ ] T033 [US2] Update viewer documentation for training metrics charts in `docs/viewer.md`

**Checkpoint**: `marlctf viewer --artifact artifacts/viewer-train` displays available training metric series from `metrics.jsonl` without requiring replay snapshots.

---

## Phase 5: User Story 3 - Compare Evaluation Evidence Visually (Priority: P3)

**Goal**: Open an evaluation run and display candidate-vs-baseline aggregate metrics, per-seed results, and acceptance pass/fail status.

**Independent Test**: Run a smoke evaluation, open its artifact directory, and verify candidate metrics, baseline metrics, per-seed rows, thresholds, and pass/fail status match `comparison.json` and `metrics.jsonl`.

### Tests for User Story 3

- [ ] T034 [P] [US3] Add evaluation comparison parser tests for candidate, baseline, acceptance, and per-seed result fields in `tests/unit/test_viewer_data_parsing.py`
- [ ] T035 [P] [US3] Add viewer contract tests for evaluation summary cards, per-seed table, and pass/fail status in `tests/contract/test_viewer_contract.py`
- [ ] T036 [P] [US3] Add evaluation viewer smoke test using `configs/smoke_eval.yml` artifacts in `tests/integration/test_viewer_smoke.py`

### Implementation for User Story 3

- [ ] T037 [US3] Implement evaluation comparison extraction and validation in `src/marlctf/viewer/data.py`
- [ ] T038 [US3] Implement evaluation comparison view, threshold status, and per-seed result selection in `src/marlctf/viewer/static/app.js`
- [ ] T039 [P] [US3] Add evaluation comparison markup and styles in `src/marlctf/viewer/static/index.html` and `src/marlctf/viewer/static/styles.css`
- [ ] T040 [US3] Update viewer documentation for evaluation comparison artifacts in `docs/viewer.md`

**Checkpoint**: `marlctf viewer --artifact artifacts/viewer-eval` shows candidate-vs-baseline metrics, per-seed evidence, and acceptance status.

---

## Phase 6: User Story 4 - Sample Training Episode Replays Later (Priority: P4)

**Goal**: Enable bounded optional training episode replay sampling without changing default training behavior.

**Independent Test**: Run training once with sampling disabled and once with sampling enabled; verify disabled mode preserves current artifacts and enabled mode writes no more than the configured sampled replay files plus metadata.

### Tests for User Story 4

- [ ] T041 [P] [US4] Add config validation tests for disabled and bounded training replay sampling settings in `tests/unit/test_config.py`
- [ ] T042 [P] [US4] Add training replay sampling integration tests for disabled default behavior and enabled bounded sample output in `tests/integration/test_training_replay_sampling.py`
- [ ] T043 [P] [US4] Add sampled replay viewer selection tests for multiple episode replay artifacts in `tests/contract/test_viewer_contract.py`
- [ ] T044 [P] [US4] Add CLI contract test for training sampled replay metadata in `tests/contract/test_cli_viewer.py`

### Implementation for User Story 4

- [ ] T045 [US4] Add training replay sampling config defaults and validation in `src/marlctf/config.py`
- [ ] T046 [US4] Write sampled training episode replay snapshots and sampled metadata in `src/marlctf/training/runner.py`
- [ ] T047 [US4] Add bounded sampled replay metadata helpers in `src/marlctf/artifacts.py`
- [ ] T048 [US4] Implement sampled episode replay discovery and selection in `src/marlctf/viewer/data.py`
- [ ] T049 [US4] Implement sampled replay episode selector in `src/marlctf/viewer/static/app.js`
- [ ] T050 [P] [US4] Add sampled replay settings to `configs/smoke_train.yml`
- [ ] T051 [US4] Document optional training replay sampling in `docs/viewer.md` and `docs/artifacts.md`

**Checkpoint**: Training replay sampling is opt-in, bounded, visible in `run.json`, and selectable in the viewer when present.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate quickstart, harden docs, and ensure viewer/replay behavior remains compatible with existing MARLCTF artifacts.

- [ ] T052 [P] Update README viewer section with replay, training chart, and evaluation viewer commands in `README.md`
- [ ] T053 [P] Update artifact schemas for replay and sampled training replays in `docs/artifacts.md`
- [ ] T054 [P] Add replay/viewer troubleshooting notes for local file loading, missing artifacts, and unsupported schema versions in `docs/viewer.md`
- [ ] T055 Run replay viewer quickstart end-to-end and record results in `artifacts/validation/replay_viewer_summary.json`
- [ ] T056 Run contract and integration tests for replay/viewer feature and record results in `artifacts/validation/replay_viewer_test_summary.json`
- [ ] T057 Verify default smoke match replay artifact remains below 1 MB and record result in `artifacts/validation/replay_size_summary.json`
- [ ] T058 Run full pytest suite and record final result in `artifacts/validation/test_summary.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational; can use viewer shell from US1 if implemented first, but metric parsing remains independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational; can use viewer shell from US1 if implemented first, but comparison parsing remains independently testable.
- **User Story 4 (Phase 6)**: Depends on Foundational and uses replay writing from US1 plus training runner from the existing MARLCTF feature.
- **Polish (Phase 7)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 - Inspect A Completed Match Replay**: Required first for visual replay MVP and replay artifact contract.
- **US2 - Understand Training Progress With Charts**: Can be implemented after Foundational using existing training metrics; full viewer integration benefits from US1 viewer shell.
- **US3 - Compare Evaluation Evidence Visually**: Can be implemented after Foundational using existing evaluation metrics and comparison artifacts; full viewer integration benefits from US1 viewer shell.
- **US4 - Sample Training Episode Replays Later**: Depends on replay snapshot infrastructure and is intentionally last because it changes training artifact behavior.

### Within Each User Story

- Write required tests first and confirm they fail before implementation.
- Parser/schema tests before viewer rendering tasks.
- Artifact writer tasks before run-loop integration.
- Viewer data parsing before static UI rendering.
- Documentation updates after behavior and artifact paths are stable.

---

## Parallel Opportunities

- Setup tasks T002-T005 can run in parallel after T001.
- Foundational tests T006-T008 can run in parallel.
- Foundational implementation T009 and T011 can start in parallel, then T010/T012 integrate shared behavior.
- US1 tests T014-T017 can run in parallel.
- US1 static viewer tasks T021-T023 can run in parallel after replay data contract is stable.
- US2 tests T026-T028 can run in parallel.
- US2 chart utility/style tasks T030 and T032 can run in parallel after T029 interface is clear.
- US3 tests T034-T036 can run in parallel.
- US3 UI/style tasks T038 and T039 can run in parallel after T037 interface is clear.
- US4 tests T041-T044 can run in parallel.
- Polish docs T052-T054 can run in parallel before validation tasks T055-T058.

---

## Parallel Example: User Story 1

```text
Task: "T014 [P] [US1] Add replay artifact contract tests for required snapshot fields and final snapshot consistency in tests/contract/test_replay_artifact_contract.py"
Task: "T015 [P] [US1] Add CLI contract tests for marlctf match replay metadata and marlctf viewer --artifact behavior in tests/contract/test_cli_viewer.py"
Task: "T016 [P] [US1] Add match replay integration smoke test for initial snapshot, per-step snapshots, terminal snapshot, and artifact size in tests/integration/test_match_replay_smoke.py"
Task: "T017 [P] [US1] Add viewer replay parser/renderer contract tests for controls, grid labels, agents, flags, score, step text, and events in tests/contract/test_viewer_contract.py"
```

## Parallel Example: User Story 2

```text
Task: "T026 [P] [US2] Add training metrics parser tests for returns, winners, captures, episode length, epsilon, buffer size, and missing optional fields in tests/unit/test_viewer_data_parsing.py"
Task: "T027 [P] [US2] Add viewer contract tests for training chart series availability and unavailable-series messaging in tests/contract/test_viewer_contract.py"
Task: "T028 [P] [US2] Add training chart integration smoke test using a 3-episode smoke training run in tests/integration/test_viewer_smoke.py"
```

## Parallel Example: User Story 3

```text
Task: "T034 [P] [US3] Add evaluation comparison parser tests for candidate, baseline, acceptance, and per-seed result fields in tests/unit/test_viewer_data_parsing.py"
Task: "T035 [P] [US3] Add viewer contract tests for evaluation summary cards, per-seed table, and pass/fail status in tests/contract/test_viewer_contract.py"
Task: "T036 [P] [US3] Add evaluation viewer smoke test using configs/smoke_eval.yml artifacts in tests/integration/test_viewer_smoke.py"
```

## Parallel Example: User Story 4

```text
Task: "T041 [P] [US4] Add config validation tests for disabled and bounded training replay sampling settings in tests/unit/test_config.py"
Task: "T042 [P] [US4] Add training replay sampling integration tests for disabled default behavior and enabled bounded sample output in tests/integration/test_training_replay_sampling.py"
Task: "T043 [P] [US4] Add sampled replay viewer selection tests for multiple episode replay artifacts in tests/contract/test_viewer_contract.py"
Task: "T044 [P] [US4] Add CLI contract test for training sampled replay metadata in tests/contract/test_cli_viewer.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete US1 replay snapshot contract tests and match replay integration.
3. Complete basic viewer replay loading and playback controls.
4. Validate `marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/viewer-match` writes `replay.jsonl`.
5. Validate `marlctf viewer --artifact artifacts/viewer-match` can inspect the replay.

### Incremental Delivery

1. Deliver replay artifact foundation plus US1 visual match replay MVP.
2. Add US2 training metrics charts from existing `metrics.jsonl`.
3. Add US3 evaluation comparison visualization from existing evaluation artifacts.
4. Add US4 optional sampled training episode replays.
5. Complete polish docs and quickstart validation.

### Parallel Team Strategy

With multiple contributors:

1. Complete Setup and Foundational phases together.
2. Build US1 first to establish replay/viewer shell.
3. Work on US2 chart parsing and US3 evaluation parsing in parallel once viewer data primitives are stable.
4. Start US4 only after replay writing and viewer selection patterns are proven.

---

## Notes

- Tasks marked [P] touch different files or isolated test cases and can run in parallel.
- Story labels map directly to the four user stories in `spec.md`.
- Each story has an independent test path and a checkpoint command or artifact.
- Tests should fail against the current code before implementation begins.
- Avoid recording every training episode replay by default; sampled training replays must remain bounded.

