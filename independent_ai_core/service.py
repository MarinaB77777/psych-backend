from __future__ import annotations

from independent_ai_core.learning import (
    build_learning_profile,
    build_offline_suggestions,
)
from independent_ai_core.contract_compliance import (
    CORE_INVARIANTS,
    compliance_report,
    validate_event_contract,
)
from independent_ai_core.schemas import OfflineLearningEvent
from independent_ai_core.store import OfflineCoreStore


class OfflineIndependentAIService:
    def __init__(self, store: OfflineCoreStore | None = None):
        self.store = store or OfflineCoreStore()

    def status(self) -> dict:
        events = self.store.load_events()
        profile = self.store.load_profile() or build_learning_profile(events)

        return {
            "ok": True,
            "core_id": "offline_independent_ai_core",
            "mode": "offline_learning",
            "network_required": False,
            "autonomous_execution": False,
            "events_count": len(events),
            "profile": profile,
            "boundaries": [
                "local_storage_only",
                "no_hidden_autonomy",
                "no_network_dependency",
                "human_review_required_for_actions",
                "hypothesis_not_fact",
                "memory_not_authority",
                "suggestion_not_permission",
                "local_memory_not_research_evidence",
                "health_model_reference_ids_only",
                "health_model_outputs_not_owned_by_offline_core",
            ],
            "contract_invariants": CORE_INVARIANTS,
            "compliance": compliance_report(),
        }

    def list_events(self) -> dict:
        return {
            "ok": True,
            "events": self.store.load_events(),
        }

    def add_event(self, payload: dict) -> dict:
        event = OfflineLearningEvent(
            event_type=payload.get("event_type", ""),
            content=payload.get("content", ""),
            source=payload.get("source") or "manual",
            language=payload.get("language") or "ru",
            tags=payload.get("tags") or [],
            importance=int(payload.get("importance") or 1),
            metadata=payload.get("metadata") or {},
        )

        errors = event.validate()
        errors.extend(validate_event_contract(payload))

        if errors:
            return {
                "ok": False,
                "status": "invalid_learning_event",
                "errors": sorted(set(errors)),
            }

        self.store.append_event(event.to_dict())
        profile = self.train()

        return {
            "ok": True,
            "status": "event_added",
            "event": event.to_dict(),
            "profile": profile["profile"],
        }

    def train(self) -> dict:
        events = self.store.load_events()
        profile = build_learning_profile(events)
        self.store.save_profile(profile)

        return {
            "ok": True,
            "status": "trained",
            "profile": profile,
        }

    def suggestions(
        self,
        *,
        language: str = "ru",
        context: dict | None = None,
    ) -> dict:
        events = self.store.load_events()
        profile = self.store.load_profile() or build_learning_profile(events)

        return {
            "ok": True,
            "suggestions": build_offline_suggestions(
                profile=profile,
                context=context,
                language=language,
            ),
            "profile": profile,
            "compliance": {
                "suggestions_create_permissions": False,
                "human_review_required": True,
            },
        }

    def compliance(self) -> dict:
        return compliance_report()

    def health_model_context(self) -> dict:
        return {
            "ok": True,
            "integration_status": "reference_only_connected",
            "ownership": {
                "health_model_owns": [
                    "source_data",
                    "calculated_outputs",
                    "state_outputs",
                    "uncertainty_outputs",
                    "forecast_governance_outputs",
                ],
                "offline_core_owns": [
                    "explicit_learning_events",
                    "local_learning_profile",
                    "bounded_suggestions_for_human_review",
                ],
            },
            "offline_core_mode": "may_reference_health_model_records_but_not_ingest_outputs",
            "routes": {
                "classic_run": "/run",
                "v61_run": "/research/health-model/v61/run",
                "pilot_session_run": "/pilot/sessions/{session_id}/run",
                "participant_report": "/pilot/sessions/{session_id}/participant-report",
                "research_variables": "/research/health-model/research-variables",
                "available_parameters": "/research/model-parameters/available",
                "parameter_dependencies": "/research/model-parameters/dependencies",
                "parameter_dataset": "/research/model-parameters/dataset",
                "parameter_check": "/research/model-parameters/check",
            },
            "forbidden_for_offline_core": [
                "store_health_model_source_data",
                "store_health_model_calculated_outputs",
                "rewrite_health_model_state",
                "treat_health_model_output_as_truth",
                "turn_research_finding_into_health_model_state",
            ],
            "compliance": compliance_report()["health_model_policy"],
        }
