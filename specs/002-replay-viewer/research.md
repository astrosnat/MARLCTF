# Research: Replay Viewer

## Decision: Store replay timelines as JSONL snapshot streams

**Rationale**: MARLCTF already stores metrics and events as local JSONL. Replay
snapshots are naturally ordered by step, can be streamed line by line, and remain
inspectable with ordinary text tools. JSONL also lets interrupted or partially
written runs preserve useful replay data up to the last completed step.

**Alternatives considered**:
- Single large JSON document: easier to load at once, but less friendly for
  partial writes and larger runs.
- Binary replay format: smaller, but conflicts with inspectable local artifacts.
- Reconstructing replay from event logs only: fragile because event logs do not
  contain complete board state for every step.

## Decision: Record an initial snapshot and one post-step snapshot per step

**Rationale**: The viewer needs to show the initial board before any action and
every state after actions resolve. This makes step counts intuitive and avoids
requiring the viewer to infer state transitions from events.

**Alternatives considered**:
- Record only post-step snapshots: misses the initial setup.
- Record pre-step and post-step snapshots for every step: doubles artifact size
  without adding enough value for the default grid.

## Decision: Keep the first viewer static and local

**Rationale**: The project is a local toy simulation, and users need artifact
inspection rather than account-based collaboration. Static assets can load files
from the user's machine or be served locally by a minimal command. This avoids a
server, database, or frontend build chain.

**Alternatives considered**:
- Full web application with backend: more complex than needed for local replay
  inspection.
- Desktop GUI toolkit: adds platform-specific packaging and testing overhead.
- Terminal-only rendering: useful for debugging but insufficient for charts and
  interactive replay controls.

## Decision: Use simple client-side charts from metrics artifacts

**Rationale**: Training and evaluation metrics are already JSONL/JSON artifacts.
The viewer can parse them directly and draw compact charts for returns, outcomes,
captures, episode length, exploration, buffer size, and evaluation comparisons.

**Alternatives considered**:
- Generate static chart images during training: less interactive and harder to
  inspect per-seed details.
- Add a metrics database: unnecessary for smoke-scale local experiments.

## Decision: Make training replay sampling opt-in and bounded

**Rationale**: Training can produce many episodes, so recording every episode by
default would grow artifacts quickly. A bounded sampling mode supports early,
middle, late, or configured episode inspection while keeping consumer hardware
and disk usage friendly.

**Alternatives considered**:
- Always record every training episode: simple but violates artifact-size and
  default-training constraints.
- Never record training replays: misses the user's requested later workflow for
  inspecting behavior changes over training.

## Decision: Keep replay snapshots additive to existing environment contracts

**Rationale**: Visualization should not change observation spaces, action spaces,
reward outputs, lifecycle rules, training behavior, or evaluation evidence. Replay
snapshots are a new artifact view over existing match state.

**Alternatives considered**:
- Add visualization fields to observations: pollutes agent inputs with UI needs.
- Change event schema to carry full state: would make event logs heavier and mix
  event semantics with replay state.
