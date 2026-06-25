# Environment Contract: Toy 3v3 CTF Parallel Environment

## Purpose

Define the public environment behavior required by training, evaluation,
baselines, and tests.

## Environment Identity

- Name: `marlctf_3v3_v0`
- API family: PettingZoo Parallel environment
- Agents: `red_0`, `red_1`, `red_2`, `blue_0`, `blue_1`, `blue_2`
- Teams: `red`, `blue`
- Initial scope: one deterministic toy scenario

## Reset

Input:
- `seed`: optional integer.
- `options`: optional mapping with `scenario_id`, `config`, and smoke overrides.

Output:
- `observations`: mapping from each active agent id to Observation.
- `infos`: mapping from each active agent id to info payload.

Required behavior:
- Same `seed` and scenario MUST produce the same initial Match state.
- All six agents MUST be active after reset.
- `infos[agent]["action_mask"]` MUST match the legal actions for the initial state.

## Step

Input:
- `actions`: mapping from active agent id to discrete action id.

Output:
- `observations`: mapping from active agent id to next Observation.
- `rewards`: mapping from agent id to scalar reward for the step.
- `terminations`: mapping from agent id to bool.
- `truncations`: mapping from agent id to bool.
- `infos`: mapping from agent id to info payload.

Required behavior:
- Missing or invalid actions MUST be handled deterministically and recorded.
- Simultaneous actions MUST resolve by documented priority rules.
- Match state MUST NOT mutate after all agents terminate or truncate.

## Action Space

Discrete actions:

| ID | Name | Meaning |
|----|------|---------|
| 0 | `stay` | No movement |
| 1 | `move_north` | Move one cell north if legal |
| 2 | `move_south` | Move one cell south if legal |
| 3 | `move_west` | Move one cell west if legal |
| 4 | `move_east` | Move one cell east if legal |
| 5 | `tag` | Attempt to tag an adjacent opponent |

Action mask:
- Length MUST equal the number of discrete actions.
- Illegal movement into walls, bounds, or blocked cells MUST be masked off.
- `tag` MUST be legal only when at least one taggable opponent is adjacent.

## Observation

Observation MUST be fixed-shape numeric data for each scenario and include:
- Self position, team id, alive state, and flag-carrying state.
- Visible ally summaries.
- Visible opponent summaries.
- Own and opposing flag state relative to observer.
- Score and remaining-step features.
- Optional action mask in `info`.

Partial observability:
- Agents receive local observations.
- Entities outside view range MUST be zero-filled or masked using documented
  sentinel values.

## Global State

`state()` MUST return fixed-shape full-state numeric data suitable for
centralized training with decentralized execution.

State MUST include:
- All agent positions, alive states, and flag-carrying states.
- Both flag states.
- Team scores.
- Remaining-step fraction.
- Scenario/rule encoding needed by a trainer.

## Rewards

Reward output MUST include per-agent scalar rewards.

Initial reward events:
- Small step penalty to encourage completion.
- Positive reward for picking up the opponent flag.
- Positive team reward for scoring.
- Positive reward for tagging an opponent when legal.
- Negative reward for being tagged while carrying a flag.
- Terminal win/loss team reward.

Reward values MUST be loaded from scenario config and recorded in run metadata.

## Termination and Truncation

Terminate when:
- A team reaches the capture target.

Truncate when:
- `max_steps` is reached.

All agents MUST share terminal/truncation status for this team game.

## Error and Info Payloads

Each `info` payload MAY include:
- `action_mask`
- `events`
- `invalid_action`
- `rule_validation_errors`
- `carrying_flag`
- `team_score`

Invalid actions MUST NOT crash a match by default; they MUST be converted to
`stay` or rejected according to config and recorded as events.

## Contract Tests

Required tests:
- Environment passes PettingZoo Parallel API tests.
- Reset with same seed produces identical initial observations and state.
- Action spaces and observation spaces are stable per agent.
- Invalid actions are handled and recorded.
- Global state shape is stable and includes all teams, agents, flags, and score.
