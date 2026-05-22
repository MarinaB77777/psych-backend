from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    AcquisitionSourceClass,
    AcquisitionStatus,
    ExposureDecision,
    InboundFilterDecision,
    SufficiencyStatus,
)
from runtime.acquisition.runtime_bridge import (
    AcquisitionRuntimeBridge,
)


def make_request(**kwargs) -> AcquisitionRequest:
    data = {
        "request_id": "req-1",
        "raw_internal_question": (
            "Need general scheduling advice."
        ),
        "source_class": (
            AcquisitionSourceClass.STANDARD_AI_SERVICE
        ),
    }

    data.update(kwargs)

    return AcquisitionRequest(**data)


def test_runtime_bridge_creates_request():
    bridge = AcquisitionRuntimeBridge()

    request = bridge.create_acquisition_request(
        make_request()
    )

    assert request.request_id == "req-1"


def test_runtime_bridge_returns_none_for_missing_request():
    bridge = AcquisitionRuntimeBridge()

    assert (
        bridge.get_acquisition_request("missing")
        is None
    )

    assert (
        bridge.prepare_external_acquisition("missing")
        is None
    )

    assert (
        bridge.evaluate_acquisition_readiness(
            "missing"
        )
        is None
    )


def test_runtime_bridge_prepares_outbound_request():
    bridge = AcquisitionRuntimeBridge()

    bridge.create_acquisition_request(
        make_request()
    )

    result = bridge.prepare_external_acquisition(
        "req-1"
    )

    stored = bridge.get_acquisition_request(
        "req-1"
    )

    assert result is not None

    assert (
        result.decision
        == ExposureDecision.ALLOWED
    )

    assert (
        stored.status
        == AcquisitionStatus.WAITING
    )

    assert stored.outbound_sent is False

    assert (
        stored.outbound_source_metadata[
            "outbound_prepared"
        ]
        is True
    )


def test_runtime_bridge_blocks_fake_inbound_result():
    bridge = AcquisitionRuntimeBridge()

    bridge.create_acquisition_request(
        make_request()
    )

    result = bridge.receive_external_result(
        request_id="req-1",
        acquisition_result=AcquisitionResult(
            request_id="req-1",
            source_class=(
                AcquisitionSourceClass.INTERNET
            ),
            raw_external_result=(
                "This is a fictional invented answer."
            ),
        ),
    )

    stored = bridge.get_acquisition_request(
        "req-1"
    )

    assert result is not None

    assert (
        result.decision
        == (
            InboundFilterDecision
            .BLOCKED_FAKE_OR_FABRICATED
        )
    )

    assert (
        stored.status
        == AcquisitionStatus.BLOCKED
    )


def test_runtime_bridge_applies_acquired_fields():
    bridge = AcquisitionRuntimeBridge()

    bridge.create_acquisition_request(
        make_request(
            required_fields=["answer"],
        )
    )

    updated = bridge.apply_acquired_fields(
        request_id="req-1",
        filled_fields={
            "answer": "Some answer",
        },
    )

    assert updated is not None

    assert updated.filled_fields == {
        "answer": "Some answer",
    }


def test_runtime_bridge_evaluates_readiness():
    bridge = AcquisitionRuntimeBridge()

    bridge.create_acquisition_request(
        make_request(
            required_fields=["answer"],
            filled_fields={
                "answer": "Some answer",
            },
        )
    )

    result = (
        bridge.evaluate_acquisition_readiness(
            "req-1"
        )
    )

    stored = bridge.get_acquisition_request(
        "req-1"
    )

    assert result is not None

    assert (
        result.sufficiency_status
        == (
            SufficiencyStatus
            .BOUNDED_ANALYSIS_READY
        )
    )

    assert (
        stored.status
        == (
            AcquisitionStatus
            .SUFFICIENT_FOR_BOUNDED_ANALYSIS
        )
    )


def test_runtime_bridge_does_not_build_answers():
    bridge = AcquisitionRuntimeBridge()

    bridge.create_acquisition_request(
        make_request()
    )

    result = bridge.prepare_external_acquisition(
        "req-1"
    )

    assert result is not None

    assert not hasattr(result, "final_answer")
    assert not hasattr(result, "recommendation")