# Ray Research Colleague Integration Plan

## Current bounded integration

Ray Research Colleague consistency awareness is implemented as a pure comparison
layer in `pilot_session/consistency_awareness.py`.

It is currently connected only to the existing Pilot Ray dialogue helper:

- `pilot_session/interview.py::build_ray_next_question`
- `pilot_session/interview.py::build_ray_chat_response`
- existing Ray endpoints in `main.py`

The integration does not write data, retry work, continue flows implicitly,
update the Health Model, update Runtime state, update Governance, or create
learning-profile memory.

## Existing project surfaces found

- Ray dialogue endpoints:
  - `POST /ray/chat/{session_id}`
  - `GET /pilot/sessions/{session_id}/ray-next-question`
  - `POST /pilot/sessions/{session_id}/ray-answer`
  - `POST /pilot/sessions/{session_id}/ray-chat`
- Ray dialogue helper:
  - `pilot_session/interview.py`
- Pilot answer provenance:
  - `ParticipantSession.research_answer_records`
  - `ParticipantSession.questionnaire_submissions`
  - `ParticipantSession.answer_merge_history`
- Existing readiness / consistency logic:
  - `model_engine/readiness.py`
  - `model_engine/consistency.py`
- Public and internal result boundaries:
  - `ParticipantSession.public_output`
  - `ParticipantSession.raw_engine_result`

## Future safe integration steps

1. Add a researcher-facing consistency panel that shows observation type,
   comparability status, time scope, source type, and validation step.
2. Keep participant-facing Ray output limited to neutral clarification text.
3. If readiness uses the new observations, expose them as data-quality
   warnings, not as participant truth or diagnosis.
4. If Analyzer uses the observations, require an explicit analysis policy:
   session-only, previous-session-aware, sensor-aware, or export-snapshot-aware.
5. If sensor context is added later, use real consented sensor declarations and
   availability metadata. Missing sensors must remain non-blocking.

## Explicit non-integration

This layer must not directly integrate with:

- Health Model scoring or formulas;
- Runtime authority or continuation;
- Governance decisions;
- automatic recommendations or forecasts;
- learning-profile memory;
- Decision Under Uncertainty staging games.
