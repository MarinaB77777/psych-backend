from __future__ import annotations

from typing import Any


CONTRACT_REFERENCES = [
    "docs/architecture/offline_independent_ai_core_contract.md",
    "docs/pilot/health_model_data_contract.md",
    "runtime/architecture/runtime_memory_boundary_contract.md",
    "runtime/architecture/adaptive_learning.md",
    "runtime/architecture/runtime_relational_boundary_contract.md",
    "runtime/architecture/access_matrix.md",
]

CORE_INVARIANTS = [
    "offline_learning_not_autonomous_execution",
    "learning_profile_not_identity",
    "suggestion_not_permission",
    "local_memory_not_research_evidence",
    "memory_not_authority",
    "remembered_preference_not_current_preference",
    "candidate_pattern_not_truth",
    "trust_not_permission",
    "human_review_required_for_actions",
    "health_model_outputs_remain_health_model_owned",
    "health_model_reference_not_ingestion",
]

FORBIDDEN_METADATA_KEYS = {
    "raw_participant_data": "raw_sensitive_participant_data",
    "participant_answers": "raw_sensitive_participant_data",
    "medical_diagnosis": "medical_or_psychological_conclusion",
    "psychological_diagnosis": "medical_or_psychological_conclusion",
    "identity_label": "hidden_identity_model",
    "personality_score": "hidden_identity_model",
    "human_worth_score": "forbidden_human_worth_ranking",
    "execute_action": "execution_authority_request",
    "execution_authority": "execution_authority_request",
    "permission_grant": "silent_permission_expansion",
    "governance_override": "governance_override_request",
    "inner_core_payload": "inner_core_direct_access",
    "external_ai_truth": "external_ai_as_truth",
    "health_model_source_data": "health_model_data_must_not_be_ingested",
    "health_model_calculated_outputs": "health_model_output_must_not_be_ingested",
    "health_model_state": "health_model_state_must_not_be_owned",
    "health_model_truth": "health_model_truth_must_not_be_claimed",
    "health_model_v61": "health_model_output_must_not_be_ingested",
    "model_parameter_values": "health_model_output_must_not_be_ingested",
    "participant_report": "health_model_report_must_not_be_ingested",
}

FORBIDDEN_CONTENT_MARKERS = {
    "execute without review": "execution_without_human_review",
    "autonomously execute": "autonomous_execution_claim",
    "permanent personality": "hidden_identity_model",
    "diagnose the user": "medical_or_psychological_conclusion",
    "override governance": "governance_override_request",
    "grant permission": "silent_permission_expansion",
    "health model truth": "health_model_truth_must_not_be_claimed",
    "ingest health model output": "health_model_output_must_not_be_ingested",
}

ALLOWED_HEALTH_MODEL_REFERENCE_FIELDS = {
    "session_id",
    "record_id",
    "analysis_id",
    "output_id",
    "route",
    "parameter_code",
    "study_id",
    "note",
}


def compliance_report() -> dict[str, Any]:
    return {
        "ok": True,
        "contract_status": "bounded_compliant_foundation",
        "contract_references": CONTRACT_REFERENCES,
        "invariants": CORE_INVARIANTS,
        "event_write_policy": {
            "allowed": [
                "explicit_learning_events",
                "local_json_persistence",
                "explainable_profile_updates",
                "bounded_suggestions_for_review",
                "health_model_reference_ids_only",
            ],
            "forbidden": sorted(set(FORBIDDEN_METADATA_KEYS.values())),
        },
        "execution_policy": {
            "autonomous_execution": False,
            "human_review_required": True,
            "suggestions_create_permissions": False,
        },
        "memory_policy": {
            "memory_is_authority": False,
            "freshness_required_before_reuse": True,
            "candidate_patterns_are_truth": False,
        },
        "health_model_policy": {
            "may_reference_health_model_outputs": True,
            "may_store_health_model_outputs": False,
            "may_rewrite_health_model_state": False,
            "may_treat_research_as_health_model_truth": False,
            "allowed_reference_fields": sorted(ALLOWED_HEALTH_MODEL_REFERENCE_FIELDS),
        },
    }


def validate_event_contract(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    metadata = payload.get("metadata") or {}
    content = str(payload.get("content") or "").lower()

    if not isinstance(metadata, dict):
        errors.append("metadata_must_be_object")
        return errors

    for key in metadata:
        normalized_key = str(key).lower()
        if normalized_key in FORBIDDEN_METADATA_KEYS:
            errors.append(FORBIDDEN_METADATA_KEYS[normalized_key])

    for marker, error in FORBIDDEN_CONTENT_MARKERS.items():
        if marker in content:
            errors.append(error)

    if "health_model_reference" in metadata:
        reference = metadata.get("health_model_reference")
        if not isinstance(reference, dict):
            errors.append("health_model_reference_must_be_object")
        else:
            for key in reference:
                if str(key).lower() not in ALLOWED_HEALTH_MODEL_REFERENCE_FIELDS:
                    errors.append("health_model_reference_must_not_embed_outputs")

    if payload.get("event_type") == "decision":
        decision_status = str(metadata.get("decision_status") or "").lower()
        if decision_status in {"executed", "approved_execution", "permission_granted"}:
            errors.append("decision_event_must_not_claim_execution_authority")

    if payload.get("event_type") == "research_observation":
        evidence_role = str(metadata.get("evidence_role") or "context").lower()
        if evidence_role in {"truth", "research_evidence", "validated_result"}:
            errors.append("offline_memory_must_not_be_research_evidence")

    return sorted(set(errors))
