# Quickstart: Replay Viewer

This quickstart validates replay snapshots, local viewer behavior, training
charts, evaluation comparison display, and optional sampled training replays.

## Prerequisites

- Python 3.11 or newer.
- MARLCTF installed in editable mode, or `PYTHONPATH=src` set when running from
  the source tree.
- A desktop browser for the viewer.

## Run One Match With Replay

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/viewer-match
```

Expected artifacts:

```text
artifacts/viewer-match/run.json
artifacts/viewer-match/metrics.jsonl
artifacts/viewer-match/events.jsonl
artifacts/viewer-match/replay.jsonl
```

Expected result:
- `run.json` records `replay_available: true` and at least one replay path.
- `replay.jsonl` contains an initial snapshot and one snapshot for each completed
  step.

## Open The Replay Viewer

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli viewer --artifact artifacts/viewer-match
```

Expected result:
- Viewer opens or reports a local URL/path.
- Grid, agents, flags, score, step controls, and events are visible.
- Play, pause, restart, and step controls update the board.

## Open Training Charts

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli train --config configs/smoke_train.yml --seed 7 --artifact-dir artifacts/viewer-train --episodes 3
python -m marlctf.cli viewer --artifact artifacts/viewer-train
```

Expected result:
- Training metrics charts show available episode series.
- Missing optional series are marked unavailable rather than displayed as zeros.

## Open Evaluation Comparison

```powershell
$env:PYTHONPATH = "src"
python -m marlctf.cli evaluate --config configs/smoke_eval.yml --artifact-dir artifacts/viewer-eval
python -m marlctf.cli viewer --artifact artifacts/viewer-eval
```

Expected result:
- Candidate and baseline aggregate metrics are visible.
- Per-seed results are inspectable.
- Acceptance pass/fail status is shown.

## Optional Training Replay Sampling

Enable sampled replay retention in a training config or command option once the
sampling task is implemented.

Expected result:
- `run.json` records sampled replay metadata.
- `replays/` contains no more than the configured number of episode replay files.
- The viewer can switch among sampled episodes.

## Validation Commands

```powershell
$env:PYTHONPATH = "src"
python -m pytest tests/contract/test_replay_artifact_contract.py tests/contract/test_viewer_contract.py
python -m pytest tests/integration/test_match_replay_smoke.py tests/integration/test_viewer_smoke.py
```

Expected result:
- Replay artifact contracts pass.
- Viewer parser and smoke behavior pass for match, training, and evaluation
  artifacts.
