# Pilot RC Persistence Audit

All paths below use `PILOT_RC_DATA_ROOT` when configured. Without it, local development falls back to legacy paths for backward compatibility.

| Store | Class/module | Format | Data | Authoritative key | Read/write paths | Restart | Pilot RC | Truth/cache |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pilot accounts | `pilot_account.persistent_store.PilotAccountPersistentStore` | JSON list | account id, stable participant id, subject link id, language, status | `account_id` | `primary/pilot_accounts.json` | yes with data root | yes | source of truth |
| Pilot sessions | `pilot_session.persistent_store.PilotSessionPersistentStore` | JSON list | sessions, answers, run result, agreement linkage, clarifications, invalidation | `session_id` | `primary/pilot_sessions.json` | yes with data root | yes | source of truth |
| Answers | `pilot_session.service.PilotSessionService` through session store | embedded JSON | questionnaire/Ray answers, revisions, answer records | `session_id` + answer record ids | `primary/pilot_sessions.json` | yes with data root | yes | source of truth |
| Run results | `pilot_session.service.PilotSessionService` through session store | embedded JSON | raw engine result, public output, uncertainty snapshot | `session_id` | `primary/pilot_sessions.json` | yes with data root | yes | source of truth for session result |
| Consistency clarifications | `pilot_session.service.record_consistency_clarification` | embedded JSON | bounded participant clarification records | `clarification_id`, `observation_key` | `primary/pilot_sessions.json` | yes with data root | yes | source of truth |
| Consent/agreement records | `pilot_session.agreement`, session start flow | embedded JSON | consent evaluation, agreement id/version/status/signed_at | `agreement_id` | `primary/pilot_sessions.json` | yes with data root | yes | source of truth for session-level consent |
| Research records/snapshots | `research.records_store` | JSON list | immutable research snapshots and DU records | `record_id`, source `session_id` | `research_snapshots/research_records.json` | yes with data root | yes | immutable research snapshot |
| Research events | `model_engine.research_event_store` | JSONL | bounded research events | `event_id` | `research_snapshots/research_events.jsonl` | yes with data root | partial | event log |
| Prepared Domain Output | `assessment.prepared_output` | derived object embedded in research record/detail | prepared representation derived from answers/result | deterministic content, record/session source | not primary file unless embedded in research record | yes when embedded | yes | derived, not primary truth |
| Analysis results index | `research.analysis_store` | JSON list | saved analysis index | `analysis_id` | `derived/analysis/research_analysis_results.json` | yes with data root | yes | derived output |
| Analysis result records | `research.analysis_store` | JSON file per analysis | full saved analysis payload | `analysis_id` | `derived/analysis/research_analysis_sessions/<analysis_id>.json` | yes with data root | yes | derived output |
| Pilot questionnaire config | functions in `main.py` | JSON object | enabled banks per project | `project_id` | `config/pilot_questionnaire_banks.json` | yes with data root | yes | configuration |
| Research studies | `research.study_store` | JSON list | research study metadata | `study_id` | `research_admin/research_studies.json` | yes with data root | researcher only | admin source |
| Research objects | `research.repository` / `research.lab_store` | JSON list | research objects/hypotheses | `object_id` | `research_admin/research_objects.json` | yes with data root | researcher only | admin source |
| Measurement instruments | `measurement_graph.instruments.connected_store` | JSON list | connected instrument metadata | `instrument_id` | `measurement/connected_measurement_instruments.json` | yes with data root | not public RC | support store |
| Measurement files | `measurement_graph.storage` | JSON/files | measurement graphs/raw files | `measurement_id` | `measurement/measurement_storage/` | yes with data root | not public RC | support store |
| Offline AI core | `independent_ai_core.store.OfflineCoreStore` | JSON files | learning events/profile | event/profile ids | `internal/offline_ai_core/` | yes with data root | not public RC | internal store |
| Games sessions | `research.games.store` | JSON list | game session events | `game_session_id` | `games/game_sessions.json` | yes with data root | hidden from RC nav | source for games layer, excluded from RC |
| Assessment result store | `assessment.result_store` | in-memory dict | legacy account result summary | account/session id | memory only | no | no active RC dependency found | cache/legacy |

## RC persistence decision

The closed RC uses a single explicit `PILOT_RC_DATA_ROOT`. Primary participant/session data, immutable research snapshots, derived analysis outputs, admin configuration, and internal/support stores are separated into subdirectories under that root.

Startup validation:

- if `PILOT_RC_REQUIRE_PERSISTENT_DATA_ROOT=true` or Render sets `RENDER=true`, missing `PILOT_RC_DATA_ROOT` raises a startup error;
- the configured root is created if missing and checked for write access;
- local development without the env var keeps legacy paths for backward compatibility.

No hidden migration is performed. Existing legacy JSON files are not moved automatically.
