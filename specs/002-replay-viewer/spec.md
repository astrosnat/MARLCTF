# Feature Specification: Replay Viewer

**Feature Branch**: `002-replay-viewer`  
**Created**: 2026-06-26  
**Status**: Draft  
**Input**: User description: "I want to add replay snapshots, build a simple viewer with HTML/JS Canvas, add training charts from metrics.jsonl and then later add episode replay sampling during training"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect A Completed Match Replay (Priority: P1)

A researcher or developer can run a small capture-the-flag match, open its replay, and step through the match visually to understand where agents moved, where flags were, when events happened, and why the match ended.

**Why this priority**: Replay inspection is the minimum useful visual layer. Without step-by-step state snapshots, neither the viewer nor later training replay analysis has trustworthy source data.

**Independent Test**: Run one deterministic match, open the produced replay in the viewer, and verify the board, agents, flags, score, step counter, and event list match the recorded run artifacts.

**Acceptance Scenarios**:

1. **Given** a completed match run with replay snapshots, **When** the user opens the replay in the viewer, **Then** the viewer shows the map, walls, both flags, all six agents, score, terminal status, and current step.
2. **Given** a replay with multiple steps, **When** the user presses play, pauses, or steps forward and backward, **Then** the displayed board and event list update to the selected step without changing the replay data.
3. **Given** a replay containing flag pickup, tag, score, invalid-action, or terminal events, **When** the user navigates to those steps, **Then** the viewer highlights or lists those events with enough context to identify the affected agent or team.

---

### User Story 2 - Understand Training Progress With Charts (Priority: P2)

A researcher or developer can open a training run and see compact charts that explain how training changed over episodes, including return, win/loss outcomes, capture counts, episode length, exploration, and replay buffer growth.

**Why this priority**: Training metrics explain whether the learning run is doing anything useful before the user spends time inspecting individual behavior.

**Independent Test**: Run a bounded training smoke run, open its metrics in the viewer, and verify charts and summary statistics match the recorded training metrics.

**Acceptance Scenarios**:

1. **Given** a completed training run with episode metrics, **When** the user opens the training view, **Then** the viewer shows episode-level charts for return, outcome, captures, episode length, exploration level, and buffer size.
2. **Given** a training metric file with missing optional fields, **When** the user opens it, **Then** the viewer still displays available charts and clearly marks unavailable series.
3. **Given** a training run with a saved candidate policy reference, **When** the user inspects the summary, **Then** the viewer shows which run, scenario, seed, and candidate policy evidence the charts describe.

---

### User Story 3 - Compare Evaluation Evidence Visually (Priority: P3)

A researcher or developer can open an evaluation run and quickly understand how the candidate and baseline compared across fixed seeds.

**Why this priority**: Evaluation is the acceptance evidence for learned policies, and charts make pass/fail results easier to understand than raw files alone.

**Independent Test**: Run an evaluation batch, open the generated comparison, and verify the viewer summarizes candidate metrics, baseline metrics, acceptance thresholds, and pass/fail status.

**Acceptance Scenarios**:

1. **Given** a completed evaluation run, **When** the user opens the comparison view, **Then** the viewer shows candidate and baseline win rate, capture count, average return, average episode length, rule-validity failures, and threshold result.
2. **Given** per-seed evaluation metrics, **When** the user selects a seed row or point, **Then** the viewer shows that seed's winner, score, episode length, return, and terminal reason.

---

### User Story 4 - Sample Training Episode Replays Later (Priority: P4)

A researcher or developer can configure training to retain a small number of episode replays so they can compare early, middle, and late behavior without recording every training episode.

**Why this priority**: Sampling training replays is valuable but should follow the core replay and viewer foundation. It must not make default training heavy on consumer hardware.

**Independent Test**: Run training with replay sampling enabled, then verify the run records sampled episode replays and the viewer can select among them.

**Acceptance Scenarios**:

1. **Given** training replay sampling is enabled, **When** a training run completes, **Then** the run includes replay snapshots for the configured sampled episodes and records which episodes were retained.
2. **Given** training replay sampling is disabled, **When** a training run completes, **Then** training metrics and checkpoints are still produced without sampled episode replay files.
3. **Given** sampled training replays from multiple episodes, **When** the user opens the viewer, **Then** they can switch between sampled episodes and see the selected episode's board animation and event list.

### Edge Cases

- Replay snapshots are missing, empty, or from a failed/interrupted run.
- Replay and metric artifacts refer to different scenario ids, seeds, or run ids.
- A replay step references an agent, flag, event, or map cell that is not valid for the scenario.
- Metric data is partial because a run was interrupted.
- A user opens a large replay or metric file on consumer-grade hardware.
- A user opens an older artifact that does not include replay snapshots.
- A training run has no saved checkpoint but still has valid metrics.
- Sampled training replay settings request more retained episodes than the run produced.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST record replay snapshots for completed match runs, including scenario id, run id, seed, step number, map dimensions, walls, agent positions, agent flag-carrying state, flag state, score, terminal status, and events for each step.
- **FR-002**: The system MUST include replay artifact locations and replay availability in run metadata so users can discover visualizable runs from the existing artifact directory.
- **FR-003**: The system MUST provide a local visual viewer that can open replay artifacts without requiring a remote service.
- **FR-004**: Users MUST be able to play, pause, restart, step forward, step backward, and change playback speed for a replay.
- **FR-005**: The viewer MUST display the grid map, walls, red and blue agents, red and blue flags, score, current step, terminal outcome, and relevant step events.
- **FR-006**: The viewer MUST validate replay data before playback and show a clear error state when required replay fields are missing or inconsistent.
- **FR-007**: The viewer MUST open training metric artifacts and display episode-level charts for return, outcome, capture count, episode length, exploration level when present, and replay buffer size when present.
- **FR-008**: The viewer MUST open evaluation artifacts and display candidate metrics, baseline metrics, per-seed results, configured threshold values, and pass/fail status.
- **FR-009**: The system MUST support visual inspection from artifacts generated by the default match, training, and evaluation smoke commands.
- **FR-010**: The system MUST preserve deterministic replay behavior: the same replay artifact must show the same sequence every time it is opened.
- **FR-011**: The system MUST keep default artifact sizes suitable for consumer-grade hardware and avoid recording every training episode unless the user explicitly enables sampled training replays.
- **FR-012**: The system MUST support an optional training replay sampling mode that retains a bounded set of episode replay snapshots and records which episodes were sampled.
- **FR-013**: When training replay sampling is disabled, the system MUST keep current training metrics, checkpoint, and evaluation behavior unchanged.
- **FR-014**: The viewer MUST show enough run context for users to identify the scenario, run type, seed or seed set, policies, and artifact paths being visualized.

### Key Entities *(include if feature involves data)*

- **Replay Snapshot**: A single point in a match or episode timeline. Includes step number, board state, agents, flags, score, terminal status, and step events.
- **Replay Artifact**: An ordered collection of replay snapshots associated with one run or sampled training episode.
- **Viewer Session**: A user's current inspection state, including selected artifact, selected step or episode, playback mode, and speed.
- **Training Chart Series**: A named sequence of per-episode metric values shown in the viewer.
- **Evaluation Comparison View**: Candidate and baseline aggregate metrics, per-seed evidence, and threshold result shown together for one evaluation run.
- **Training Replay Sample**: A retained replay artifact for a selected training episode, plus metadata describing the episode number and sampling reason.

### Simulation & Learning Context *(mandatory for behavior changes)*

- **Environment Configuration**: Replay artifacts are tied to the existing `tiny-3v3-ctf` scenario and must preserve the map, seed, policy ids, reward config, termination conditions, and score progression from the source run.
- **Agent-Environment Contracts**: Replay snapshots must represent the six-agent 3v3 environment without changing observation space, action space, reward outputs, or terminal/truncation rules.
- **Evaluation Evidence**: Evaluation visualization must use the existing baseline-versus-candidate evidence: win rate, capture count, average return, episode length, rule-validity failures, fixed seed set, and pass/fail threshold.
- **Reproducibility Artifacts**: Replay, metric, comparison, checkpoint-reference, and run metadata artifacts must remain local, inspectable, and linked to the run that produced them.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can run one smoke match, open its replay, and visually inspect any recorded step in under 2 minutes from command completion.
- **SC-002**: The viewer correctly displays all six agents, both flags, score, and current step for 100% of replay snapshots generated by the default smoke match.
- **SC-003**: A user can identify at least one terminal outcome and the final score from the viewer without opening raw artifact files.
- **SC-004**: Training charts load a default smoke training run and display at least four episode metric series in under 5 seconds on consumer-grade hardware.
- **SC-005**: Evaluation visualization displays candidate metrics, baseline metrics, and acceptance pass/fail status for all seeds in the default smoke evaluation.
- **SC-006**: Opening an invalid, missing, or incompatible artifact produces a clear error message and does not crash the viewer.
- **SC-007**: When sampled training replays are enabled, retained replay artifacts remain bounded to the configured sample count and default training remains unchanged when sampling is disabled.

## Assumptions

- The first viewer is intended for local research and debugging rather than public hosting or collaborative multi-user access.
- Existing smoke match, training, and evaluation commands remain the source of truth for generating visualizable artifacts.
- Default replay recording is enabled for match runs because matches are small and immediately useful to inspect.
- Default training replay sampling is disabled or very limited to avoid large artifact growth during local training.
- The initial viewer targets desktop browsers and local files; mobile-specific interaction design is out of scope for this feature.
- Visualization is read-only: users can inspect artifacts but cannot edit or replay-run policy decisions from inside the viewer.
