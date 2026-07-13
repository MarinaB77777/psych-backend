# Offline Independent AI Core Contract

## Purpose

Offline Independent AI Core is a separate local-first learning layer for
offline AI work.

It exists to:
- store allowed learning events locally;
- build an explainable learning profile;
- surface suggestions for human review;
- support offline continuity when network AI is unavailable;
- keep individual AI development separate from Pilot v1 execution.

It is not:
- an autonomous agent;
- an execution authority;
- a hidden identity model;
- a replacement for Governance;
- a replacement for Runtime;
- a source of psychological truth.

---

## Architectural Placement

Offline Independent AI Core belongs to:

External Core
-> Memory Foundations
-> Adaptive Learning
-> Offline Independent AI Core

It may exchange bounded signals with:
- Workspace;
- Research Partner panel;
- Governance;
- Runtime memory boundaries;
- future Domain Rays.

It must not directly access:
- Inner Core;
- unrestricted personal data;
- hidden memory layers;
- execution queues without explicit Runtime/Governance mediation.

---

## Data Boundary

The core stores only explicit learning events.

Allowed event classes:
- user_preference;
- correction;
- decision;
- research_observation;
- workflow_pattern;
- boundary_rule;
- language_preference.

All events must remain:
- local by default;
- inspectable;
- removable in future lifecycle tooling;
- attributable to a source;
- separated from pilot research truth.

The core must not silently ingest:
- raw sensitive participant data;
- medical/psychological conclusions;
- external AI outputs as truth;
- inferred identity labels;
- hidden behavioral scores.

---

## Learning Boundary

Training means:
- aggregating explicit events;
- counting event classes, tags, and languages;
- preserving recent preference notes;
- preserving explicit boundary rules;
- producing suggestions from the profile.

Training does not mean:
- model weight training;
- recursive self-modification;
- autonomous capability expansion;
- truth discovery;
- permission expansion.

Candidate patterns are always provisional.

---

## Execution Boundary

Offline Independent AI Core may:
- suggest next steps;
- warn about missing context;
- summarize known preferences;
- point to inconsistencies;
- support offline review.

Offline Independent AI Core must not:
- execute actions;
- change pilot data;
- create research conclusions;
- modify governance state;
- contact external services;
- claim certainty from sparse events.

Human review is required for any operational action.

---

## Pilot Boundary

Pilot v1 remains priority.

Offline Independent AI Core may support pilot work by remembering:
- workflow preferences;
- correction patterns;
- language preferences;
- project boundaries.

It must not:
- become part of participant scoring;
- influence pilot conclusions silently;
- mix individual AI learning with research evidence;
- expand pilot scope without explicit human decision.

---

## Health Model Boundary

Health Model Data is governed by:
- `docs/pilot/health_model_data_contract.md`

The Health Model domain owns:
- source data;
- calculated outputs;
- state outputs;
- uncertainty outputs;
- forecast-governance outputs.

Offline Independent AI Core may reference Health Model records by bounded IDs,
routes, or parameter codes.

Offline Independent AI Core must not:
- store Health Model source data as learning memory;
- store Health Model calculated outputs as learning memory;
- rewrite Health Model state;
- treat Health Model outputs as truth;
- treat research findings as Health Model state.

Reference
!=
ownership transfer.

Health Model output
!=
Offline AI memory.

---

## Current Implementation

Implemented package:
- `independent_ai_core/`

Implemented storage:
- `data/offline_ai_core/learning_events.json`
- `data/offline_ai_core/learning_profile.json`

Implemented UI:
- `/offline-ai-core`

Implemented API:
- `GET /offline-ai-core/status`
- `GET /offline-ai-core/health-model/context`
- `GET /offline-ai-core/events`
- `POST /offline-ai-core/events`
- `POST /offline-ai-core/train`
- `GET /offline-ai-core/suggestions`
- `POST /offline-ai-core/suggestions`

Current status:
- executable foundation;
- local JSON persistence;
- explainable profile;
- bounded suggestions;
- no autonomous execution.
