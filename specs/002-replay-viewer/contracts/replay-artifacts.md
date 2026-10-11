# Replay Artifact Contract

## Purpose

Define the local replay artifacts used by the viewer to animate match and sampled
training episodes.

## Files

Match replay:

```text
<artifact-dir>/replay.jsonl
```

Sampled training replay:

```text
<artifact-dir>/replays/episode-000001.jsonl
```

Run metadata MUST include replay discoverability when replay artifacts exist:

```json
{
  "replay_paths": ["artifacts/smoke-match/replay.jsonl"],
  "replay_available": true
}
```

Training runs with sampled replay artifacts MUST also include:

```json
{
  "sampled_replays": [
    {
      "episode": 1,
      "sampling_reason": "first",
      "path": "artifacts/smoke-train/replays/episode-000001.jsonl"
    }
  ]
}
```

## Snapshot JSONL Row

Each line in a replay artifact is one replay snapshot.

```json
{
  "schema_version": "1.0",
  "run_id": "match-tiny-3v3-ctf-...",
  "run_type": "match",
  "scenario_id": "tiny-3v3-ctf",
  "seed": 42,
  "episode": null,
  "step": 0,
  "map": {
    "width": 9,
    "height": 7,
    "walls": [[4, 1], [4, 5]]
  },
  "agents": {
    "red_0": {"team": "red", "x": 1, "y": 2, "alive": true, "has_flag": false},
    "blue_0": {"team": "blue", "x": 7, "y": 2, "alive": true, "has_flag": false}
  },
  "flags": {
    "red": {"status": "home", "x": 0, "y": 3, "carrier": null},
    "blue": {"status": "home", "x": 8, "y": 3, "carrier": null}
  },
  "score": {"red": 0, "blue": 0},
  "terminal": {"status": "running", "winner": null, "reason": null},
  "events": []
}
```

## Required Fields

- `schema_version`
- `run_id`
- `run_type`
- `scenario_id`
- `seed`
- `step`
- `map.width`
- `map.height`
- `map.walls`
- `agents`
- `flags.red`
- `flags.blue`
- `score.red`
- `score.blue`
- `terminal.status`
- `events`

## Validation Rules

- Default scenario replay rows MUST contain six agents: `red_0`, `red_1`,
  `red_2`, `blue_0`, `blue_1`, `blue_2`.
- Agent coordinates MUST be integers inside map bounds.
- Flag coordinates MUST be integers inside map bounds when `carrier` is null.
- Carried flags MUST set `x` and `y` to null and `carrier` to a valid agent id.
- Snapshot steps MUST start at `0` and be ordered.
- Final snapshot terminal status MUST match the source run summary when the run
  completed.
- Event objects MUST preserve the existing event fields: `step`, `event_type`,
  `agent_id`, `team_id`, and `details`.

## Compatibility

Older run directories without replay artifacts remain valid MARLCTF artifacts.
The viewer MUST show metrics/comparison views when possible and report replay as
unavailable instead of treating the run as corrupt.
