# Game Module Contract v0.1

The Game Module is a research instrument layer. It records game events and
prepares normalized game signal bundles for later analysis.

Game != diagnosis.

Game signal != truth.

Game = additional evidence.

## Data Flow

Game UI -> Raw Game Events -> Game Data Preparation -> Game Signal Bundle ->
Readiness / Analyzer -> Health Model comparison.

The game never writes directly to `S`, `CurrentStateScore`,
`TrajectoryFailureRisk` or other Health Model authority fields.

## Required Provenance

Every event must preserve:

- `event_id`;
- `game_session_id`;
- `session_id`;
- `game_id`;
- `game_version`;
- `question_id` and/or `question_uuid` when the event answers a predefined
  research question;
- `answer` and/or `value` when the event carries an answer;
- `shared_timestamp_utc`;
- `screen_id`;
- `event_type`;
- `object_id` when relevant;
- `previous_object_id` when relevant;
- `decision_time_ms` when available;
- `confirmation_step` when available;
- `cancel_count`;
- `excluded_from_analysis`.

## Supported Scope

Only owned project games are registered. There is no external game catalog in
this contract and no placeholder game logic.

## Prepared Signal Bundle

The prepared bundle may include:

- `source_type: "game"`;
- `source_name`;
- `shared_time_reference: true`;
- `game_session_id`;
- `session_id`;
- `game_id`;
- `game_version`;
- `object_catalog_version`;
- `completed`;
- `abandoned`;
- `tutorial_excluded_from_analysis`;
- `world_initial_choices`;
- `crisis_sequence`;
- `question_answers`;
- `metrics`;
- `interpretation: null`.

The bundle transfers facts, not conclusions.

