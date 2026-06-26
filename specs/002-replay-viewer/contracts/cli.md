# CLI Contract: Replay Viewer

## Purpose

Define command behavior for generating visualizable artifacts and opening the
local viewer.

## Existing Commands With Replay Output

### `marlctf match`

New default behavior:
- Completed match runs write `replay.jsonl` in the artifact directory.
- `run.json` records `replay_available` and `replay_paths`.

Optional behavior:
- A future option MAY disable replay writing for matches when artifact size is a
  concern.

Required artifacts after a default smoke match:

```text
run.json
metrics.jsonl
events.jsonl
replay.jsonl
```

### `marlctf train`

Default behavior:
- Training metrics and checkpoints remain unchanged.
- Sampled episode replay writing is disabled or bounded by config.

When training replay sampling is enabled:

```text
replays/episode-000001.jsonl
```

`run.json` records sampled replay metadata.

### `marlctf evaluate`

Default behavior:
- Evaluation metrics and comparison remain unchanged.
- Viewer can consume `run.json`, `metrics.jsonl`, and `comparison.json`.

## New Command: `marlctf viewer`

Opens or serves the local viewer.

Required behavior:
- With no artifact argument, command reports where the viewer is available and
  how to load local artifacts.
- With an artifact path or run directory, command starts the viewer with that
  artifact preselected when possible.

Options:
- `--artifact <path>`: run directory or artifact file to open.
- `--host <host>`: local host address for serving viewer files.
- `--port <port>`: local port for serving viewer files.
- `--no-open`: do not open a browser automatically.

Exit codes:
- `0`: viewer started or static viewer path reported.
- `1`: artifact path does not exist or is not readable.
- `2`: runtime failure starting the local viewer.

## Required Contract Tests

- `marlctf match` writes replay metadata and `replay.jsonl`.
- `marlctf viewer --artifact <run-dir>` accepts a valid run directory.
- `marlctf viewer --artifact <missing>` returns config/user error.
- Training with sampling disabled preserves existing training artifacts.
- Training with sampling enabled writes bounded sampled replay metadata.
