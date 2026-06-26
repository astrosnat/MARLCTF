# Viewer Contract

## Purpose

Define the behavior expected from the local replay and metrics viewer.

## Inputs

The viewer accepts one of these local inputs:

- A run directory containing `run.json` and optional visual artifacts.
- A replay JSONL file.
- A training `metrics.jsonl` file with optional `run.json` context.
- An evaluation directory containing `comparison.json` and per-seed metrics.

## Views

### Replay View

Required display:
- Grid map with walls.
- Red and blue agents.
- Red and blue flags, including carried state.
- Score.
- Current step.
- Terminal status, winner, and reason when available.
- Step event list.

Required controls:
- Play.
- Pause.
- Restart.
- Step forward.
- Step backward.
- Speed selection.
- Step scrubber or direct step selection.

### Training Metrics View

Required display when series are available:
- Episode return.
- Win/loss or winner outcome.
- Capture count.
- Episode length.
- Exploration value.
- Buffer size.

The viewer MUST show unavailable optional series as missing, not as zero-valued
series.

### Evaluation View

Required display:
- Candidate team and aggregate metrics.
- Baseline team and aggregate metrics.
- Acceptance thresholds.
- Pass/fail result.
- Per-seed results with winner, score, return, episode length, terminal reason,
  and rule-validity failures.

## Error States

The viewer MUST provide clear errors for:
- Missing selected file.
- Empty replay file.
- Malformed JSON or JSONL.
- Missing required replay fields.
- Replay/run metadata mismatch.
- Unsupported schema version.

Errors MUST not erase already loaded valid data unless the user selects a new
artifact.

## Accessibility and Usability

- Replay controls MUST be operable with pointer input and keyboard focus.
- Important state changes such as current step, score, and terminal result MUST
  also be represented as text, not only color.
- The viewer MUST preserve enough run context on screen to identify what artifact
  is being inspected.

## Performance Expectations

- Default match replay opens in under 2 seconds.
- Default training metrics charts open in under 5 seconds.
- Playback remains responsive for default smoke artifacts.
