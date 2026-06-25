# Data Model: Toy MARL CTF Simulation

## Match

Represents one 3v3 CTF episode.

Fields:
- `match_id`: unique run-scoped identifier.
- `scenario_id`: scenario used to initialize the match.
- `seed`: integer seed used for deterministic initialization.
- `teams`: exactly two Team records.
- `agents`: exactly six Agent records.
- `flags`: two Flag records, one per team.
- `step_count`: current step, starting at zero.
- `max_steps`: terminal step limit.
- `score`: mapping of team id to capture count.
- `status`: `not_started`, `running`, `terminated`, or `truncated`.
- `winner`: winning team id or `draw`.
- `events`: ordered MatchEvent records.

Validation rules:
- A match MUST contain exactly two teams of three agents for this feature.
- `step_count` MUST NOT exceed `max_steps`.
- Terminal matches MUST have a terminal reason.

State transitions:
- `not_started` -> `running` after reset.
- `running` -> `terminated` when a team reaches the capture target.
- `running` -> `truncated` when `max_steps` is reached.

## Team

Represents one cooperative side in the match.

Fields:
- `team_id`: stable identifier, `red` or `blue`.
- `agent_ids`: three agent ids.
- `spawn_zone`: cells where team agents start or respawn.
- `flag_home`: home cell for the team's own flag.
- `score`: number of successful captures.
- `policy_id`: policy controlling the team for a run.

Validation rules:
- Team ids MUST be unique per match.
- Each team MUST have exactly three agents.

## Agent

Represents one controllable participant.

Fields:
- `agent_id`: stable PettingZoo agent name, such as `red_0`.
- `team_id`: owning team id.
- `position`: grid coordinate.
- `spawn_position`: reset coordinate.
- `alive`: whether the agent can act this step.
- `has_flag`: whether the agent is carrying the opposing flag.
- `respawn_timer`: steps remaining before reactivation.
- `last_action`: most recent legal or handled action.
- `reward_total`: cumulative episode reward.

Validation rules:
- Agent positions MUST remain inside map bounds.
- An agent MUST NOT carry its own team's flag.
- Dead or respawning agents MUST NOT change position from movement actions.

## Flag

Represents a team objective.

Fields:
- `flag_id`: stable identifier.
- `team_id`: owner team.
- `home_position`: home coordinate.
- `position`: current coordinate or carrier reference.
- `carrier_agent_id`: agent id when carried, otherwise null.
- `status`: `home`, `carried`, or `dropped`.

Validation rules:
- A flag MUST have at most one carrier.
- A carried flag's carrier MUST belong to the opposing team.

State transitions:
- `home` -> `carried` when an opponent picks it up.
- `carried` -> `home` when the carrier scores or is tagged under return rules.
- `carried` -> `dropped` only if the selected rules enable dropped flags.
- `dropped` -> `home` when recovered by owner or timeout expires.

## Scenario

Defines reproducible match setup.

Fields:
- `scenario_id`: stable scenario name.
- `map_width`, `map_height`: grid dimensions.
- `walls`: blocked cells.
- `spawn_zones`: team spawn coordinates.
- `flag_homes`: team flag home coordinates.
- `legal_actions`: action names and ids.
- `capture_target`: score needed to win.
- `max_steps`: truncation threshold.
- `reward_config`: event and terminal reward values.
- `observation_config`: view radius, feature channels, and masking rules.
- `seed_policy`: how seeds are applied during reset.

Validation rules:
- Spawn and flag cells MUST be inside bounds and unblocked.
- Both teams MUST have equal numbers of spawn positions.
- Legal actions MUST be discrete and stable.

## Observation

Represents one agent's local view plus optional action mask.

Fields:
- `agent_id`: observing agent.
- `self_features`: own position, team, alive state, flag-carrying state.
- `ally_features`: visible allied agents.
- `opponent_features`: visible opposing agents.
- `flag_features`: own and opposing flag state relative to observer.
- `score_features`: normalized score and remaining steps.
- `action_mask`: legal action indicator by action id.

Validation rules:
- Observation shape MUST be constant for a scenario.
- Hidden entities MUST be represented by documented zero or mask values.

## Global State

Represents full match state for centralized training and evaluation.

Fields:
- `agent_positions`: all agent positions and alive states.
- `flag_states`: both flag positions/carriers/status.
- `score`: team scores.
- `remaining_steps`: normalized remaining budget.
- `scenario_features`: map and rule identifiers encoded for the trainer.

Validation rules:
- State shape MUST be constant for a scenario.
- State MUST be derived from Match without mutating Match.

## Policy Configuration

Defines how a team is controlled.

Fields:
- `policy_id`: stable identifier.
- `policy_type`: `random`, `scripted`, `vdn`, or future `qmix`.
- `team_id`: controlled team.
- `checkpoint_path`: optional checkpoint for learned policies.
- `hyperparameters`: learning and inference settings.
- `seed`: policy-level random seed.

Validation rules:
- Learned policies MUST include enough hyperparameters and checkpoint metadata
  to reproduce evaluation.

## Run Artifact

Stores reproducibility and metrics for match, training, or evaluation runs.

Fields:
- `run_id`: unique run identifier.
- `run_type`: `match`, `train`, or `evaluate`.
- `created_at`: timestamp.
- `config_path`: source config used for the run.
- `scenario_id`: scenario used.
- `seeds`: seed or seed set.
- `policy_ids`: policies used.
- `metrics_path`: JSONL metrics file.
- `events_path`: optional JSONL events file.
- `checkpoint_paths`: optional model checkpoints.
- `summary`: aggregate result metrics.
- `status`: `completed`, `failed`, or `interrupted`.

Validation rules:
- Completed runs MUST include summary metrics.
- Failed or interrupted runs MUST include an inspectable reason.

## MatchEvent

Records rule-relevant events.

Fields:
- `step`: match step.
- `event_type`: `move`, `invalid_action`, `tag`, `flag_pickup`,
  `flag_return`, `score`, `terminal`, or `error`.
- `agent_id`: primary agent, when applicable.
- `team_id`: primary team, when applicable.
- `details`: event-specific structured payload.

Validation rules:
- Event step MUST be between zero and match `max_steps`.
- Error events MUST include an error code and message.
