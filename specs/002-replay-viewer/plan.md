# Implementation Plan: Replay Viewer

**Branch**: `002-replay-viewer` | **Date**: 2026-06-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-replay-viewer/spec.md`

## Summary

Add replay snapshots and a local visualization workflow for MARLCTF runs. Match
runs will emit deterministic replay artifacts that describe the board, agents,
flags, score, and events at each step. A lightweight local viewer will load run
artifacts, animate match replays on a grid canvas, chart training metrics from
`metrics.jsonl`, and summarize evaluation comparisons. Training episode replay
sampling will be planned as an optional bounded mode so default training remains
small and CPU-friendly.

## Technical Context

**Language/Version**: Python 3.11+ for artifact generation and CLI integration; browser-standard HTML/CSS/JavaScript for the local viewer  
**Primary Dependencies**: Existing MARLCTF package dependencies; no required frontend build dependency for the first viewer  
**Storage**: Local filesystem JSON/JSONL artifacts under run artifact directories  
**Testing**: pytest for artifact contracts and runner integration; browser-level smoke checks for viewer parsing/rendering where available  
**Target Platform**: Windows-first local development with cross-platform file paths; desktop browsers for visualization  
**Project Type**: Single Python package with CLI and static local viewer assets  
**Performance Goals**: Open a default match replay in under 2 seconds; load default training charts in under 5 seconds; keep default match replay artifacts below 1 MB  
**Constraints**: Read-only visualization; deterministic replay playback; no remote service required; default training must not record every episode replay  
**Scale/Scope**: Default 9x7 3v3 CTF scenario, one match replay at a time, default training/evaluation smoke artifacts, optional bounded sampled training replays

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Reproducibility**: PASS. Replay artifacts will include run id, scenario id,
  seed, map, policy ids through linked run metadata, step snapshots, score,
  terminal state, and events.
- **Agent-Environment Contracts**: PASS. Snapshot schemas and viewer contracts
  document board, agent, flag, event, metric, and comparison fields without
  changing observation/action/reward contracts.
- **Test Strategy**: PASS. Plan includes artifact schema tests, runner replay
  integration tests, viewer parser/validation tests, and smoke checks for match,
  training, and evaluation artifacts.
- **Training Evidence**: PASS. This feature visualizes training/evaluation
  evidence but does not claim behavior improvement. Existing evaluation metrics
  and thresholds remain the evidence source.
- **Simplicity**: PASS. Static viewer assets and JSONL replay snapshots avoid a
  server or frontend build pipeline for the first version.

## Project Structure

### Documentation (this feature)

```text
specs/002-replay-viewer/
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
|   |-- replay-artifacts.md
|   |-- viewer.md
|   `-- cli.md
`-- tasks.md
```

### Source Code (repository root)

```text
src/marlctf/
|-- artifacts.py                 # JSON/JSONL artifact helpers
|-- cli.py                       # viewer command and run command options
|-- replay.py                    # snapshot schema/building helpers
|-- runner.py                    # match replay writing
|-- training/
|   `-- runner.py                # optional sampled training replay writing
|-- evaluation/
|   `-- evaluator.py             # evaluation artifact compatibility
`-- viewer/
    |-- __init__.py
    `-- static/
        |-- index.html
        |-- app.js
        |-- styles.css
        `-- sample-manifest.json

tests/
|-- contract/
|   |-- test_replay_artifact_contract.py
|   |-- test_viewer_contract.py
|   `-- test_cli_viewer.py
|-- integration/
|   |-- test_match_replay_smoke.py
|   |-- test_viewer_smoke.py
|   `-- test_training_replay_sampling.py
`-- unit/
    |-- test_replay_snapshots.py
    `-- test_viewer_data_parsing.py

docs/
|-- artifacts.md                 # update with replay artifacts
`-- viewer.md                    # user guide for opening local artifacts
```

**Structure Decision**: Keep replay generation in the Python package with the
existing run loops and artifact writer. Keep the viewer as static package assets
so it can be opened locally or served by a tiny CLI command without introducing a
new application project.

## Complexity Tracking

No constitution violations. The only new UI surface is a static local viewer,
which is justified by the feature's explicit need to inspect agent behavior and
training evidence visually.

## Phase 0 Research Summary

See [research.md](./research.md). Key decisions: use JSONL snapshots for replay
streams, include one initial snapshot plus one post-step snapshot per match step,
ship a static local viewer without a frontend build system, parse metrics client
side for charts, and make training replay sampling opt-in and bounded.

## Phase 1 Design Summary

See [data-model.md](./data-model.md) for replay and viewer entities. See
[contracts/](./contracts/) for artifact, viewer, and CLI contracts. See
[quickstart.md](./quickstart.md) for the end-to-end validation path.

## Post-Design Constitution Check

- **Reproducibility**: PASS. Data model and contracts define replay linkage to
  run metadata, deterministic ordered snapshots, and sampled training replay
  metadata.
- **Agent-Environment Contracts**: PASS. Existing environment contracts remain
  unchanged; replay contracts are additive and validate against current match
  state.
- **Test Strategy**: PASS. Contracts and quickstart define schema, parser,
  integration, and viewer smoke validation.
- **Training Evidence**: PASS. Training charts and evaluation views consume
  existing evidence; sampled training replays are inspection artifacts, not
  performance claims.
- **Simplicity**: PASS. No server, database, or frontend build chain is required
  for MVP visualization.
