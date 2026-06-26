# Default Scenario

The default scenario is `tiny-3v3-ctf`, a deterministic 3v3 capture-the-flag grid used by the match, training, and evaluation smoke configs.

## Map

- Width: `9`
- Height: `7`
- Walls: `[4, 1]`, `[4, 5]`
- Capture target: `1`
- Max steps: `200`

Team setup:

| Team | Agents | Spawn Zone | Flag Home |
|------|--------|------------|-----------|
| `red` | `red_0`, `red_1`, `red_2` | `[1,2]`, `[1,3]`, `[1,4]` | `[0,3]` |
| `blue` | `blue_0`, `blue_1`, `blue_2` | `[7,2]`, `[7,3]`, `[7,4]` | `[8,3]` |

## Action IDs

| ID | Name | Meaning |
|----|------|---------|
| `0` | `stay` | No movement |
| `1` | `move_north` | Move one cell up if legal |
| `2` | `move_south` | Move one cell down if legal |
| `3` | `move_west` | Move one cell left if legal |
| `4` | `move_east` | Move one cell right if legal |
| `5` | `tag` | Tag an adjacent opponent if legal |

Invalid actions are handled as `stay` and recorded as `invalid_action` events.

## Rules

- All six agents act simultaneously each step.
- Movement into walls, map bounds, or blocked cells is masked out.
- If multiple agents target the same cell, they remain in their original cells.
- An agent picks up the opponent flag by entering the flag home cell.
- A carrier scores by returning to its own flag home.
- A tag action affects the sorted first adjacent opponent.
- Tagged flag carriers drop possession and the carried flag returns home.
- A match terminates when a team reaches `capture_target`.
- A match truncates when `max_steps` is reached.

## Rewards

Default reward values:

| Key | Value |
|-----|-------|
| `step` | `-0.01` |
| `flag_pickup` | `1.0` |
| `tag` | `0.25` |
| `tagged_while_carrying` | `-0.5` |
| `score` | `5.0` |
| `terminal_win` | `10.0` |
| `terminal_loss` | `-10.0` |

Rewards are emitted per agent and the active reward config is recorded in `run.json` for match, training, and evaluation runs.

## Observation Features

Each agent receives a fixed-shape `float32` vector of length `29`:

- Self features: normalized `x`, normalized `y`, red-team indicator, alive flag, carrying-flag indicator.
- Ally features: two visible allies, each encoded as relative `dx`, relative `dy`, alive flag.
- Opponent features: three visible opponents, each encoded as relative `dx`, relative `dy`, alive flag.
- Flag features: own and opponent flag, each encoded as relative `dx`, relative `dy`, status.
- Score and clock features: red score fraction, blue score fraction, remaining step fraction.

Visibility uses Manhattan distance and defaults to `view_radius: 3`. Hidden entities are zero-filled. Action masks are exposed through `infos[agent_id]` when `include_action_mask` is enabled.

## Global State Features

`env.state()` returns a fixed-shape `float32` vector of length `33` for centralized training:

- Six agents, each encoded as normalized `x`, normalized `y`, alive flag, carrying-flag indicator.
- Two flags, each encoded as normalized `x`, normalized `y`, status.
- Red score fraction, blue score fraction, remaining step fraction.

This state is used by the training/evaluation path and leaves room for a future QMIX mixer without changing the environment contract.
