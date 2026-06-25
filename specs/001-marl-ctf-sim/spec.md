# Feature Specification: Toy MARL CTF Simulation

**Feature Branch**: `001-marl-ctf-sim`  
**Created**: 2026-06-25  
**Status**: Draft  
**Input**: User description: "I want to make a toy capture the flag MARL simulation that can run on consumer grade hardware. I want to use pettingzoo + KAZ + qmix or vdn. I want a 3v3 match"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run a 3v3 CTF Match (Priority: P1)

As an experimenter, I can run a complete three-versus-three capture-the-flag
match with two teams of agents so that I can observe whether the toy environment
produces valid team play.

**Why this priority**: A playable and valid match is the smallest useful slice
of the simulation. Training and evaluation depend on the match rules working
first.

**Independent Test**: Start a match with six agents and a fixed scenario, run it
until a terminal condition is reached, and verify that every turn, score change,
capture event, and final result follows the stated rules.

**Acceptance Scenarios**:

1. **Given** a valid 3v3 scenario with two teams and six agents, **When** a match
   is started, **Then** the system initializes all agents, team assignments,
   flags, spawn areas, and score state before the first step.
2. **Given** an active match, **When** agents move, tag opponents, pick up flags,
   return flags, or time expires, **Then** the system updates the match state,
   scores, rewards, and terminal status according to the rules.

---

### User Story 2 - Train Cooperative Agents Locally (Priority: P2)

As an experimenter, I can run a short cooperative training session for the 3v3
match on consumer-grade hardware so that I can verify the simulation supports
multi-agent learning experiments without specialized infrastructure.

**Why this priority**: The project goal is a toy MARL simulation, not only a
hand-scripted game. Local training establishes that the environment is usable for
learning experiments.

**Independent Test**: Run a bounded training smoke test with a documented seed
and resource limit, then verify that the run completes, produces metrics, and
stores enough metadata to reproduce the run.

**Acceptance Scenarios**:

1. **Given** a local machine with ordinary consumer-grade resources, **When** a
   short training run is started with a fixed seed and small workload, **Then**
   the run completes within the configured limit and records reward, episode,
   win/loss, and runtime metrics.
2. **Given** a completed training run, **When** the same configuration and seed
   are used again, **Then** the resulting run metadata is sufficient to compare
   outcomes and diagnose differences.

---

### User Story 3 - Evaluate and Compare Team Policies (Priority: P3)

As an experimenter, I can evaluate trained, random, and scripted team policies
against each other so that I can tell whether learning changes team behavior in
the CTF match.

**Why this priority**: Evaluation makes training results meaningful and gives
the user a way to compare policy quality beyond watching a single match.

**Independent Test**: Run an evaluation batch across a fixed set of seeds and
verify that the system reports aggregate outcomes for each team policy pairing.

**Acceptance Scenarios**:

1. **Given** two selectable team policies and an evaluation seed set, **When** an
   evaluation batch runs, **Then** the system reports win rate, capture count,
   average return, episode length, and rule-validity failures.
2. **Given** a baseline policy and a candidate policy, **When** their evaluation
   metrics are compared, **Then** the system identifies whether the candidate
   meets the configured acceptance threshold.

---

### Edge Cases

- A match reaches the maximum step limit without either team winning.
- Multiple agents attempt to occupy, tag, or interact with the same cell or zone
  on the same step.
- An agent holding a flag is tagged, blocked, or returned to spawn.
- An invalid action is submitted by a policy during a match.
- A training or evaluation run is interrupted before completion.
- A requested local workload exceeds the configured resource budget.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support a capture-the-flag match with exactly two
  teams of three agents each for the initial feature scope.
- **FR-002**: The system MUST define deterministic match initialization for
  teams, agents, spawn areas, flags, scoring state, and scenario layout when a
  seed is supplied.
- **FR-003**: The system MUST define the legal actions available to each agent
  and reject or handle invalid actions without corrupting match state.
- **FR-004**: The system MUST define observable match state for each agent,
  including enough information for cooperative team behavior while preserving any
  intended partial-observability rules.
- **FR-005**: The system MUST implement capture-the-flag mechanics for movement,
  tagging, flag pickup, flag return, scoring, respawn or reset behavior, and
  terminal conditions.
- **FR-006**: The system MUST emit per-agent and team rewards for match events
  and final outcomes.
- **FR-007**: The system MUST support scripted or random baseline policies that
  can complete full matches without learning.
- **FR-008**: The system MUST support a bounded local training smoke run for a
  cooperative team-learning policy.
- **FR-009**: The system MUST support evaluation runs that compare at least two
  team policy configurations over a fixed seed set.
- **FR-010**: The system MUST record run metadata including seed, scenario,
  reward configuration, termination limits, policy configuration, runtime, and
  summary metrics.
- **FR-011**: The system MUST provide a consumer-grade default configuration that
  finishes a smoke match, smoke training run, and smoke evaluation without
  requiring specialized hardware.
- **FR-012**: The system MUST expose rule-validity failures, invalid actions, and
  interrupted runs as inspectable errors or artifacts.

### Key Entities *(include if feature involves data)*

- **Match**: A single 3v3 CTF episode with teams, agents, scenario layout,
  current state, score, step count, rewards, and terminal outcome.
- **Team**: A group of three agents sharing an objective, score, and policy
  assignment.
- **Agent**: A controllable participant with team membership, position,
  alive/active state, action choice, observation, and reward history.
- **Scenario**: The map, spawn areas, flag locations, movement constraints,
  scoring rules, step limit, and seed policy used to initialize matches.
- **Policy Configuration**: A selectable control strategy for a team, such as a
  baseline, trained candidate, or learning run configuration.
- **Run Artifact**: Metadata, logs, metrics, and optional checkpoints produced by
  a match, training run, or evaluation batch.

### Simulation & Learning Context *(mandatory for behavior changes)*

- **Environment Configuration**: Initial scope is one toy 3v3 CTF scenario with
  documented map layout, spawn zones, flag locations, legal actions, reward
  definition, terminal conditions, maximum step limit, and seed policy.
- **Agent-Environment Contracts**: The feature must document each agent's
  observation contents, legal action set, reward outputs, lifecycle events, and
  state-transition assumptions before planning implementation.
- **Evaluation Evidence**: Learning-related changes must compare a candidate
  team policy against random or scripted baselines using win rate, capture count,
  average return, episode length, and rule-validity failure count over a fixed
  seed set.
- **Reproducibility Artifacts**: Each run must produce configuration, seed,
  scenario identifier, policy identifier, summary metrics, runtime, and any
  checkpoint or diagnostic artifact needed to reproduce or inspect the result.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can run a complete 3v3 match from start to terminal outcome
  in under 2 minutes using the default smoke configuration.
- **SC-002**: At least 100 seeded smoke matches complete with zero rule-validity
  failures for movement, tagging, scoring, and terminal-state handling.
- **SC-003**: A default local training smoke run completes within 30 minutes on
  consumer-grade hardware and produces reward, episode, win/loss, and runtime
  metrics.
- **SC-004**: A default evaluation batch compares two team policy configurations
  across at least 10 seeds and reports aggregate metrics for each configuration.
- **SC-005**: Re-running a match with the same scenario and seed reproduces the
  same initial state and deterministic baseline-policy outcome in 100% of smoke
  checks.
- **SC-006**: A new user can identify the match result, final score, winner,
  capture count, and run configuration from the generated artifacts without
  reading source code.

## Assumptions

- The first deliverable is a toy simulation and local experiment workflow, not a
  production-scale training platform.
- The initial match size is fixed at 3v3; different team sizes are out of scope
  for this feature.
- Consumer-grade hardware means a typical modern laptop or desktop CPU/GPU
  setup, with defaults chosen to keep smoke runs small.
- The user's requested PettingZoo, KAZ, and QMIX or VDN preferences are planning
  constraints; the specification defines required behavior and evidence without
  prescribing implementation steps.
- The first learning goal is a cooperative team-learning smoke test and policy
  comparison, not state-of-the-art CTF performance.
- Visual rendering is optional for this feature; inspectable logs and metrics are
  sufficient for the first usable version.
