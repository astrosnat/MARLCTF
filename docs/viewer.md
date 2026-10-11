# Replay Visualisation

MARLCTF includes a build-free, local HTML/JavaScript Canvas viewer for
inspecting deterministic match replays. It is read-only: viewing a replay does
not rerun policies or change its artifacts.

## Generate And Open A Replay

Run a deterministic smoke match and write its replay artifacts:

```powershell
marlctf match --config configs/smoke_match.yml --seed 42 --artifact-dir artifacts/viewer-match
```

The match artifact directory contains `run.json`, `metrics.jsonl`,
`events.jsonl`, and `replay.jsonl`. Open it with:

```powershell
marlctf viewer --artifact artifacts/viewer-match
```

The command starts an HTTP server on `http://127.0.0.1:8000` and opens that URL
in the default browser. Stop it with `Ctrl+C` in the terminal.

## Visual Features

The current viewer provides:

- A responsive grid showing map bounds, alternating cells, and walls.
- Red and blue flags at their visible positions.
- All agents at each recorded step, labelled by agent number and coloured by
  team; a dark outline identifies a flag carrier.
- Current score, replay step, terminal status, winner, and terminal reason.
- The events attached to the current snapshot, including event details.
- Restart, previous-step, next-step, play, and pause controls.
- A timeline scrubber and playback speeds of `0.5x`, `1x`, `2x`, and `4x`.

Playback is deterministic because the viewer renders recorded snapshots; it
does not recompute environment state.

## Load Artifacts

`--artifact` accepts a match run directory, a `run.json` file, or a replay
JSONL file named `replay*.jsonl` (or stored under a `replays/` directory).
For a run directory, replay paths in `run.json` are considered first, followed
by the conventional `replay.jsonl` and `replays/*.jsonl` locations. The first
discovered replay is loaded and validated.

You may also start with no artifact and choose a file with the **Replay JSONL**
picker on the page:

```powershell
marlctf viewer
```

The file picker parses JSONL locally in the browser. Server-preloaded replays
also receive schema and sequence validation; validation errors are shown in the
viewer before the snapshots are displayed.

## Server Options

```powershell
marlctf viewer --artifact artifacts/viewer-match --host 127.0.0.1 --port 8000 --no-open
```

| Option | Default | Meaning |
|--------|---------|---------|
| `--artifact PATH` | none | Run directory, `run.json`, or replay JSONL to load |
| `--host HOST` | `127.0.0.1` | Interface on which the server listens |
| `--port PORT` | `8000` | HTTP port; `0` requests a free port programmatically |
| `--no-open` | off | Do not launch the default browser |

Keep the loopback host unless other machines must reach the viewer. The server
has no authentication and is intended for local research and debugging.

## Replay Metadata

`run.json` records `replay_available: true` and `replay_paths` when snapshots
are present. See [Artifacts](artifacts.md#replay-artifacts) for the schema.

## Current Scope

The implemented UI visualises match replay snapshots. Artifact discovery can
identify `metrics.jsonl`, `comparison.json`, and sampled replay paths, but the
browser does not yet render training charts, evaluation comparisons, or a
sampled-episode selector. Those items remain planned in
[`specs/002-replay-viewer/tasks.md`](../specs/002-replay-viewer/tasks.md).
Older run directories without replay files remain valid artifacts, but do not
currently produce a visual view.

## Troubleshooting

- **`artifact path does not exist`**: run from the repository root or pass an
  absolute path.
- **`No replay snapshots loaded`**: select a match run containing a non-empty
  `replay.jsonl`; training and evaluation metrics are not rendered yet.
- **Validation errors**: regenerate with the current MARLCTF version or compare
  the file with the replay schema. Missing fields, invalid coordinates, and
  inconsistent step sequences prevent valid playback.
- **Port already in use**: choose another port, such as `--port 8001`.
- **Browser did not open**: copy the printed `MARLCTF viewer:` URL into a
  browser.
- **Opening `index.html` directly does not preload an artifact**: use
  `marlctf viewer` so `/api/artifact` is available, or use the file picker.
