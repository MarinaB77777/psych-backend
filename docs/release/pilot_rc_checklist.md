# Pilot RC Checklist

## Participant flow

- [ ] Open `/consent/pilot_v1/ru`
- [ ] Switch to EN and ES; navigation, title, instructions, buttons, errors and empty states change language
- [ ] Accept consent/agreement
- [ ] Confirm declined consent does not create a session
- [ ] Confirm accepted consent creates/reuses participant account and starts a session
- [ ] Continue to `/assessment?lang=<lang>&continue=1`
- [ ] Complete questionnaire and/or Ray dialogue
- [ ] Complete clarification flow when shown
- [ ] Run session
- [ ] Open participant result/report
- [ ] Confirm participant does not see Research Workspace, UUIDs, internal codes, raw engine output, debug data, or research-only consistency details
- [ ] Confirm completion state is clear

## Researcher flow

- [ ] Open `/research-workspace?lang=ru`
- [ ] Confirm access without researcher cookie redirects to `/research-login`
- [ ] Sign in with env-configured researcher credentials
- [ ] Switch to EN and ES; navigation, titles, buttons, instructions, empty states and researcher labels change language
- [ ] Open Pilot panel
- [ ] Load sessions
- [ ] Open session detail
- [ ] Open Consistency & Clarifications
- [ ] Open Data Check
- [ ] Open Data Preparation
- [ ] Open Analysis Builder
- [ ] Open Analysis Check
- [ ] Open Scientific Results
- [ ] Logout
- [ ] Confirm researcher routes are blocked again
- [ ] Confirm unfinished Games, Living World, Offline AI, Measurement Setup, standalone Research Lab and demo pages are not public RC navigation

## Repeated sessions

- [ ] Create P1/S1 and finish it
- [ ] Save S1 data snapshot
- [ ] Create P1/S2 and finish it
- [ ] Confirm S1 is unchanged
- [ ] Confirm S1 and S2 have different `session_id`
- [ ] Confirm both have the same stable participant id
- [ ] Confirm unique participants = 1 and total sessions = 2
- [ ] Create P2/S3
- [ ] Confirm unique participants = 2 and total sessions = 3
- [ ] Confirm trajectory order is chronological

## Localization smoke

Check RU, EN and ES for:

- [ ] `/assessment`
- [ ] `/consent/pilot_v1/ru`, `/consent/pilot_v1/en`, `/consent/pilot_v1/es`
- [ ] `/pilot-result?session_id=<id>`
- [ ] `/research-workspace`
- [ ] `/data-check`
- [ ] `/data-preparation`
- [ ] `/analysis-builder`
- [ ] `/analysis-check`
- [ ] `/scientific-results`

HTTP 200 is not enough; verify visible text changes.

## Render readiness

- [ ] `runtime.txt` is present
- [ ] `requirements.txt` installs cleanly
- [ ] Render start command is `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] `RESEARCH_PSEUDONYMIZATION_SALT` is set in Render environment
- [ ] `PILOT_RC_DATA_ROOT` points to a Render persistent disk
- [ ] `PILOT_RC_REQUIRE_PERSISTENT_DATA_ROOT=true`
- [ ] `RESEARCHER_ACCESS_USERNAME` is set
- [ ] `RESEARCHER_ACCESS_PASSWORD` is set
- [ ] `RESEARCHER_SESSION_SECRET` is set
- [ ] `PILOT_RC_REQUIRE_RESEARCHER_AUTH=true`
- [ ] no production secrets are committed
- [ ] persistent disk or database is configured before real data collection
- [ ] researcher access is restricted before any non-demo RC
- [ ] `/health` returns OK
- [ ] fresh-data startup works
- [ ] restart/persistence check proves data survives

## Verdict rules

- Demo-ready: all main flows work with demo data, no secrets, no broken RC navigation.
- Closed RC-ready: demo-ready plus restricted researcher access and durable persistence.
- Pilot-ready: closed RC-ready plus production access control, durable storage, backup policy and successful restart/persistence proof.
- Not ready: any required flow fails, localization is broken, secrets are present, or data can be lost during restart for real recruitment.
