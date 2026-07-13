from independent_ai_core.service import OfflineIndependentAIService
from independent_ai_core.store import OfflineCoreStore


def test_offline_core_adds_event_trains_profile_and_suggests(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    initial_status = service.status()
    assert initial_status["ok"] is True
    assert initial_status["network_required"] is False
    assert initial_status["autonomous_execution"] is False
    assert "memory_not_authority" in initial_status["contract_invariants"]

    result = service.add_event({
        "event_type": "boundary_rule",
        "content": "Do not execute actions without human review.",
        "language": "en",
        "tags": ["boundary", "offline"],
        "importance": 5,
    })

    assert result["ok"] is True
    assert result["profile"]["events_count"] == 1
    assert result["profile"]["event_type_counts"]["boundary_rule"] == 1

    suggestions = service.suggestions(
        language="en",
        context={"pilot_priority": True},
    )

    assert suggestions["ok"] is True
    assert suggestions["suggestions"]
    assert all(
        item["creates_permission"] is False
        for item in suggestions["suggestions"]
    )
    assert all(
        item["requires_human_review"] is True
        for item in suggestions["suggestions"]
    )
    assert any(
        item["reason"] == "pilot_priority_guardrail"
        for item in suggestions["suggestions"]
    )


def test_offline_core_rejects_unsupported_event_type(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    result = service.add_event({
        "event_type": "autonomous_action",
        "content": "Run without review.",
        "language": "en",
    })

    assert result["ok"] is False
    assert "unsupported_event_type" in result["errors"]


def test_offline_core_rejects_contract_forbidden_metadata(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    result = service.add_event({
        "event_type": "research_observation",
        "content": "Raw answers imported for learning.",
        "language": "en",
        "metadata": {
            "raw_participant_data": {"DU1": 1},
        },
    })

    assert result["ok"] is False
    assert "raw_sensitive_participant_data" in result["errors"]


def test_offline_core_rejects_health_model_output_ingestion(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    result = service.add_event({
        "event_type": "research_observation",
        "content": "Ingest Health Model output into local memory.",
        "language": "en",
        "metadata": {
            "health_model_v61": {"Q": 0.7},
        },
    })

    assert result["ok"] is False
    assert "health_model_output_must_not_be_ingested" in result["errors"]


def test_offline_core_allows_health_model_reference_only(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    result = service.add_event({
        "event_type": "research_observation",
        "content": "Review Health Model report by reference only.",
        "language": "en",
        "metadata": {
            "health_model_reference": {
                "session_id": "session-1",
                "route": "/pilot/sessions/session-1/participant-report",
            },
        },
    })

    assert result["ok"] is True
    assert result["profile"]["events_count"] == 1


def test_offline_core_rejects_embedded_health_model_reference_outputs(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    result = service.add_event({
        "event_type": "research_observation",
        "content": "Review Health Model report by reference.",
        "language": "en",
        "metadata": {
            "health_model_reference": {
                "session_id": "session-1",
                "calculated_outputs": {"Q": 0.7},
            },
        },
    })

    assert result["ok"] is False
    assert "health_model_reference_must_not_embed_outputs" in result["errors"]


def test_offline_core_rejects_research_observation_as_truth(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    result = service.add_event({
        "event_type": "research_observation",
        "content": "This pattern is validated.",
        "language": "en",
        "metadata": {
            "evidence_role": "validated_result",
        },
    })

    assert result["ok"] is False
    assert "offline_memory_must_not_be_research_evidence" in result["errors"]


def test_offline_core_exposes_contract_compliance_report(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    report = service.compliance()

    assert report["ok"] is True
    assert report["execution_policy"]["autonomous_execution"] is False
    assert report["memory_policy"]["memory_is_authority"] is False
    assert report["health_model_policy"]["may_store_health_model_outputs"] is False


def test_offline_core_exposes_health_model_context(tmp_path):
    service = OfflineIndependentAIService(
        store=OfflineCoreStore(tmp_path / "offline_ai_core")
    )

    context = service.health_model_context()

    assert context["ok"] is True
    assert context["integration_status"] == "reference_only_connected"
    assert context["compliance"]["may_reference_health_model_outputs"] is True
    assert context["compliance"]["may_store_health_model_outputs"] is False
