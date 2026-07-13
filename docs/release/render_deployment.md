# Render Deployment Notes: Pilot RC

## Canonical entry points

Participant:

- `/consent/pilot_v1/ru`
- `/consent/pilot_v1/en`
- `/consent/pilot_v1/es`

The consent page creates or reuses a participant account, starts a session only after explicit consent, and then continues to `/assessment?lang=<lang>&continue=1`.

Researcher:

- `/research-workspace?lang=ru`
- `/research-workspace?lang=en`
- `/research-workspace?lang=es`

Health check:

- `/health`

Participant result pages are opened only after a real session:

- `/pilot-result?session_id=<session_id>&lang=<lang>`

## Render configuration

Python version:

- `python-3.13.7`

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

- `RESEARCH_PSEUDONYMIZATION_SALT`: long random secret used for research pseudonymization.
- `PILOT_RC_DATA_ROOT`: persistent data root. On Render this must be on a persistent disk.
- `PILOT_RC_REQUIRE_PERSISTENT_DATA_ROOT=true`: fail startup if no persistent root is configured.
- `RESEARCHER_ACCESS_USERNAME`: closed RC researcher username.
- `RESEARCHER_ACCESS_PASSWORD`: closed RC researcher password.
- `RESEARCHER_SESSION_SECRET`: long random secret for signing the researcher session cookie.
- `PILOT_RC_REQUIRE_RESEARCHER_AUTH=true`: fail startup if researcher access env vars are missing.

Do not commit production secrets. Service-account JSON files and credential-like JSON files are ignored by `.gitignore`; if Google credentials are ever needed, provide them through Render secrets or a secret manager.

## Release route allowlist

| Route | Purpose | Audience | Backend dependencies | RU/EN/ES | RC status |
| --- | --- | --- | --- | --- | --- |
| `GET /health` | Service health check | internal | FastAPI app only | n/a | tested by route smoke |
| `GET /assessment` | Participant questionnaire continuation | participant | static UI, pilot account/session APIs | shared i18n + page text | smoke tested |
| `GET /consent/{version}/{lang}` | Standalone consent/agreement and session start | participant | static consent files, account/session APIs | language-specific route | smoke tested |
| `GET /pilot-result` | Participant-safe result/report | participant | `/pilot/sessions/{id}/result`, `/participant-report` | shared i18n | smoke required |
| `POST /pilot/accounts` | Create participant account | participant API | `data/pilot_accounts.json` | language payload | integration tested |
| `POST /pilot/accounts/start-session` | Start pilot session after consent | participant API | account/session stores | language payload | integration tested |
| `POST /pilot/sessions/{id}/answers` | Save questionnaire answers | participant API | session store | data only | integration tested |
| `POST /pilot/sessions/{id}/followup-answers` | Save clarification answers | participant API | session store | data only | integration tested |
| `GET /pilot/sessions/{id}/ray-next-question` | Ray dialogue prompt | participant API | pilot session service | data only | smoke required |
| `POST /pilot/sessions/{id}/ray-chat` | Ray dialogue answer | participant API | pilot interview logic | language payload | smoke required |
| `POST /pilot/sessions/{id}/ray-clarification` | Participant consistency clarification | participant API | consistency layer, session store | language payload | tested |
| `POST /pilot/sessions/{id}/run` | Run pilot model | participant/API | model engine, result service, session store | data only | integration tested |
| `GET /pilot/sessions/{id}/result` | Participant-safe model status | participant API | result service/session store | data only | integration tested |
| `GET /pilot/sessions/{id}/participant-report` | Participant-facing report | participant API | public report builder | language/session data | smoke required |
| `GET /pilot/sessions/{id}/participant-export` | Participant export where safe | participant API | session export service | data only | smoke required |
| `GET /research-workspace` | Researcher workspace entry | researcher | static UI and research APIs | shared i18n | auth + smoke tested |
| `GET /data-check` | Research records check | researcher | research records store | shared i18n | auth + smoke tested |
| `GET /data-preparation` | Prepared data workspace | researcher | research records/prepared outputs | shared i18n | auth + smoke tested |
| `GET /analysis-builder` | Analysis setup | researcher | analysis catalog/check/run APIs | shared i18n | auth + smoke tested |
| `GET /analysis-check` | Analysis compatibility check | researcher | analysis checker | shared i18n | auth + smoke tested |
| `GET /scientific-results` | Scientific results | researcher | analysis results store | shared i18n | auth + smoke tested |
| `GET /research/participant-data/records` | Research records list | researcher API | records store + session/export records | data only | auth + integration tested |
| `GET /research/participant-data/records/{id}` | Research record detail | researcher API | records store/prepared output | data only | auth + integration tested |
| `GET /research/analysis/catalog?study_id=<study_id>` | Analysis variable catalog for one study | researcher API | analysis catalog builder | data only | smoke tested |
| `POST /research/analysis/check` | Analysis contract check | researcher API | analysis checker | data only | integration tested |
| `POST /research/analysis/statistical/run` | Statistical method run | researcher API | statistical runner/results store | data only | integration tested |
| `GET /research/analysis/results` | Analysis results | researcher API | results store | data only | smoke required |

## Not in public Pilot RC navigation

The following remain in the repository but are hidden or marked internal/not available from release navigation:

- staging games and unfinished game pages: `/games`, `/world-choice`
- unfinished Living World participant flow
- `/participant-portal`
- `/offline-ai-core`
- `/measurement-setup`
- `/questionnaire-du`
- `/research-lab`
- `/health-model-research-entities`
- `/question-metadata`
- legacy/demo/debug/internal stands

Backend endpoints are not deleted in this release preparation.

## Persistence audit

Current stores are JSON/file based:

- primary participant/session data: `<PILOT_RC_DATA_ROOT>/primary/pilot_accounts.json`, `<PILOT_RC_DATA_ROOT>/primary/pilot_sessions.json`
- pilot configuration: `<PILOT_RC_DATA_ROOT>/config/pilot_questionnaire_banks.json`
- immutable research snapshots/events: `<PILOT_RC_DATA_ROOT>/research_snapshots/research_records.json`, `<PILOT_RC_DATA_ROOT>/research_snapshots/research_events.jsonl`
- derived analysis outputs: `<PILOT_RC_DATA_ROOT>/derived/analysis/research_analysis_results.json`, `<PILOT_RC_DATA_ROOT>/derived/analysis/research_analysis_sessions/`
- research admin objects/studies: `<PILOT_RC_DATA_ROOT>/research_admin/research_objects.json`, `<PILOT_RC_DATA_ROOT>/research_admin/research_studies.json`
- measurement support stores: `<PILOT_RC_DATA_ROOT>/measurement/connected_measurement_instruments.json`, `<PILOT_RC_DATA_ROOT>/measurement/measurement_storage/`
- internal/offline AI stores: `<PILOT_RC_DATA_ROOT>/internal/offline_ai_core/`
- game session store, not in RC navigation: `<PILOT_RC_DATA_ROOT>/games/game_sessions.json`

Render service files are ephemeral unless a persistent disk or external database is configured. Without persistent storage, pilot sessions, accounts, research exports, and analysis results can be lost after restart/redeploy.

Minimum Render solution for a closed RC:

- configure a persistent disk and set `PILOT_RC_DATA_ROOT` to that mounted path;
- set `PILOT_RC_REQUIRE_PERSISTENT_DATA_ROOT=true` so startup fails if the disk path is missing;
- back up JSON stores before deploy/redeploy;
- do not call the system pilot-ready for real participant recruitment without durable storage and backup policy.

## Security and access status

Closed RC access gate:

- researcher pages and research APIs are protected by a server-side signed-cookie gate;
- credentials and cookie secret are environment-only;
- unauthorized research API access returns controlled `401`; browser access redirects to `/research-login`;
- `/research-logout` clears the researcher cookie;
- participant routes remain available without researcher credentials.

Remaining blockers for real pilot deployment:

- researcher access is a minimal closed-RC gate, not enterprise auth/SSO;
- participant session access is identifier-based and should be treated as closed-demo only;
- `RESEARCH_PSEUDONYMIZATION_SALT` is mandatory for research pseudonymization;
- production secrets must be supplied through environment/secret manager only.

Verdict from local verification: closed RC-ready when Render is configured with persistent disk and the required environment variables. Not pilot-ready for open recruitment.
