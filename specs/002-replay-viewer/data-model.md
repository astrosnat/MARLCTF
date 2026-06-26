# Data Model: Replay Viewer

## Replay Snapshot

Represents one visualizable state in a match or sampled training episode.

Fields:
- `schema_version`: replay schema version string.
- `run_id`: source run identifier.
- `run_type`: `match`, `train`, or `evaluate` when applicable.
- `scenario_id`: scenario used to produce the snapshot.
- `seed`: seed for the episode or match.
- `episode`: optional episode number for training replay samples.
- `step`: replay step number, starting at `0` for initial state.
- `map`: width, height, and wall coordinates.
- `agents`: mapping of agent id to team, x/y position, alive state, and flag
  carrying state.
- `flags`: mapping of team id to flag status, x/y position when visible, and
  carrier agent id when carried.
- `score`: mapping of team id to capture count.
- `terminal`: status, winner, and terminal reason when known.
- `events`: rule-relevant events associated with the step.

Validation rules:
- Snapshot order must be non-decreasing by `step` within one replay artifact.
- Exactly six known 3v3 agent ids must be present for default scenario snapshots.
- Agent and flag coordinates must be inside map bounds when coordinates are not
  null.
- Carried flags must have null coordinates and a valid carrier agent id.
- `score` must contain `red` and `blue`.

## Replay Artifact

Represents an ordered snapshot stream and its relationship to a run.

Fields:
- `path`: artifact path.
- `format`: `jsonl` for snapshot streams.
- `schema_version`: snapshot schema version.
- `run_id`: source run id.
- `scenario_id`: source scenario id.
- `seed`: source seed when single-seed.
- `episode`: optional sampled training episode number.
- `snapshot_count`: number of snapshots written.
- `first_step`: first step in the artifact.
- `last_step`: final step in the artifact.

Validation rules:
- The artifact must contain at least one snapshot to be playable.
- Metadata recorded in `run.json` must match the snapshot stream's run id and
  scenario id.

## Viewer Manifest

Represents a loaded run directory and the visualizable artifacts found inside it.

Fields:
- `run_metadata`: parsed run metadata.
- `replay_artifacts`: list of replay artifacts available for playback.
- `metric_artifacts`: metrics files available for charts.
- `comparison_artifact`: optional evaluation comparison file.
- `warnings`: missing optional artifacts or compatibility notes.

Validation rules:
- Missing optional artifacts must produce warnings, not crashes.
- Required artifacts for a selected view must be validated before display.

## Viewer Session

Represents local UI state while a user inspects artifacts.

Fields:
- `selected_run`: loaded run directory or files.
- `selected_view`: replay, training metrics, or evaluation comparison.
- `selected_replay`: active replay artifact.
- `selected_step`: current snapshot index or step number.
- `playback_state`: playing or paused.
- `playback_speed`: selected speed multiplier.
- `selected_metric_series`: visible chart series.

State transitions:
- No artifact loaded -> artifact loaded -> view selected.
- Paused -> playing -> paused.
- Replay selected -> step changed by playback, scrubber, or step controls.

## Training Chart Series

Represents one per-episode metric series in the training charts.

Fields:
- `name`: metric label such as episode return, capture count, episode length,
  epsilon, buffer size, or win.
- `points`: ordered episode/value pairs.
- `available`: whether the metric was present in the source file.
- `warning`: optional explanation when a metric is missing.

Validation rules:
- Episode numbers must be ordered for display.
- Missing optional series must not block available charts.

## Evaluation Comparison View

Represents visualized candidate-versus-baseline evidence.

Fields:
- `candidate`: team id and aggregate metrics.
- `baseline`: team id and aggregate metrics.
- `acceptance`: configured thresholds and pass/fail result.
- `per_seed_results`: seed-level evaluation metrics.

Validation rules:
- Candidate and baseline summaries must contain seed count, win rate, capture
  count, average return, average episode length, and rule-validity failures.
- Acceptance must include pass/fail status.

## Training Replay Sample

Represents a retained replay from one selected training episode.

Fields:
- `episode`: training episode number.
- `sampling_reason`: configured cadence, explicit episode request, first,
  middle, latest, or final.
- `replay_artifact`: replay artifact metadata.

Validation rules:
- Sample count must not exceed configured limit.
- Sampling disabled means no sampled episode replay artifacts are required.
