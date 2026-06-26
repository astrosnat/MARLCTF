# Artifacts

MARLCTF writes local JSON and JSONL artifacts for reproducibility. Runtime artifacts are ignored by Git except `artifacts/.gitkeep`.

## Common `run.json`

All commands write `run.json`.

```json
{
  "run_id": "match-tiny-3v3-ctf-...",
  "run_type": "match",
  "created_at": "2026-06-26T00:00:00+00:00",
  "status": "completed",
  "config_path": "configs/smoke_match.yml",
  "scenario_id": "tiny-3v3-ctf",
  "seeds": [42],
  "policy_ids": ["red:scripted", "blue:scripted"],
  "metrics_path": "artifacts/smoke-match/metrics.jsonl",
  "events_path": "artifacts/smoke-match/events.jsonl",
  "summary": {}
}
```

Required fields:

| Field | Meaning |
|-------|---------|
| `run_id` | Stable command/scenario/seed-derived identifier |
| `run_type` | `match`, `train`, or `evaluate` |
| `created_at` | UTC timestamp |
| `status` | `running`, `completed`, `failed`, or `interrupted` |
| `config_path` | Source config path |
| `scenario_id` | Scenario used for the run |
| `seeds` | Seed or fixed seed set |
| `policy_ids` | Team policy labels |
| `metrics_path` | JSONL metrics path |
| `events_path` | JSONL events path |
| `summary` | Command-specific aggregate summary for completed runs |

Training runs also include `algorithm`, `reward_config`, `smoke_limits`, and `checkpoint_paths`. Evaluation runs also include `candidate`, `baseline`, `reward_config`, `smoke_limits`, and `comparison_path`.

## Match Metrics

`metrics.jsonl` for `match` stores one JSON object per environment step.

```json
{
  "step": 1,
  "score": {"red": 0, "blue": 0},
  "rewards": {"red_0": -0.01, "blue_0": -0.01},
  "terminated": false,
  "truncated": false
}
```

## Training Metrics

`metrics.jsonl` for `train` stores one JSON object per episode.

```json
{
  "episode": 1,
  "episode_return": -29.5,
  "epsilon": 1.0,
  "winner": "blue",
  "win": false,
  "capture_count": 1,
  "episode_length": 25,
  "buffer_size": 25
}
```

Training checkpoints are written under `checkpoints/`, with `checkpoints/latest.pt` used by the smoke evaluation config.

## Events

`events.jsonl` records rule-relevant match events.

```json
{
  "step": 8,
  "event_type": "tag",
  "agent_id": "red_1",
  "team_id": "red",
  "details": {"tagged_agent_id": "blue_1", "carrier": false}
}
```

Known event types include `move`, `invalid_action`, `tag`, `flag_pickup`, `flag_return`, `score`, and `terminal`.

## Replay Artifacts

Runs that write visual replay snapshots include replay discoverability fields in
`run.json`.

```json
{
  "replay_available": true,
  "replay_paths": ["artifacts/smoke-match/replay.jsonl"]
}
```

`replay.jsonl` stores one schema-versioned snapshot per line. Each snapshot is
designed for the local HTML/Canvas viewer.

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

Required snapshot fields are `schema_version`, `run_id`, `run_type`,
`scenario_id`, `seed`, `step`, `map`, `agents`, `flags`, `score`, `terminal`,
and `events`. Default 3v3 replay rows must contain `red_0`, `red_1`, `red_2`,
`blue_0`, `blue_1`, and `blue_2`. Agent and visible flag coordinates must be
inside map bounds. Carried flags use `x: null`, `y: null`, and a valid
`carrier`.
## Evaluation Metrics

`metrics.jsonl` for `evaluate` stores one JSON object per seed.

```json
{
  "seed": 101,
  "winner": "draw",
  "score": {"red": 0, "blue": 0},
  "returns": {"red": -0.6, "blue": 14.025},
  "episode_length": 200,
  "terminal_reason": "max_steps",
  "status": "truncated",
  "rule_validity_failures": 0
}
```

## `comparison.json`

Evaluation writes aggregate baseline-versus-candidate evidence.

```json
{
  "candidate": {
    "team": "red",
    "metrics": {
      "seed_count": 10,
      "win_rate": 0.0,
      "capture_count": 0,
      "average_return": -6.0,
      "average_episode_length": 200.0,
      "rule_validity_failures": 0
    }
  },
  "baseline": {
    "team": "blue",
    "metrics": {
      "seed_count": 10,
      "win_rate": 0.0,
      "capture_count": 0,
      "average_return": 140.25,
      "average_episode_length": 200.0,
      "rule_validity_failures": 0
    }
  },
  "acceptance": {
    "min_win_rate": 0.5,
    "max_rule_validity_failures": 0,
    "passed": false
  }
}
```

`acceptance.passed` is true only when the candidate reaches the configured minimum win rate and stays within the maximum rule-validity failure budget.
