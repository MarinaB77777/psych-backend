# runtime/acquisition/runtime_bridge.py

from __future__ import annotations

from runtime.acquisition.contracts import (
    AcquisitionRequest,
    AcquisitionResult,
    ExposureFilterResult,
    InboundFilterResult,
    ReadinessEvaluation,
)
from runtime.acquisition.service_with_registry import (
    AcquisitionServiceWithRegistry,
)


class AcquisitionRuntimeBridge:
    """
    Runtime ↔ Acquisition bridge.

    This bridge gives Runtime a bounded interface to the acquisition subsystem.

    It is NOT:
    - Analyst;
    - Governance;
    - answer builder;
    - retry executor;
    - acquisition transport;
    - truth authority;
    - memory authority;
    - autonomous orchestrator.

    Runtime asks for acquisition coordination.
    Acquisition returns bounded operational outputs.

    runtime_bridge ≠ Analyst
    runtime_bridge ≠ Governance
    runtime_bridge ≠ executor
    runtime_bridge ≠ answer builder
    """

    def __init__(
        self,
        acquisition_service: AcquisitionServiceWithRegistry | None = None,
    ) -> None:
        self.acquisition_service = (
            acquisition_service or AcquisitionServiceWithRegistry()
        )

    def create_acquisition_request(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionRequest:
        return self.acquisition_service.register_request(request)

    def get_acquisition_request(
        self,
        request_id: str,
    ) -> AcquisitionRequest | None:
        return self.acquisition_service.get_request(request_id)

    def prepare_external_acquisition(
        self,
        request_id: str,
        privacy_policy_known: bool = True,
        human_permission_granted: bool = False,
    ) -> ExposureFilterResult | None:
        return self.acquisition_service.prepare_outbound_request(
            request_id=request_id,
            privacy_policy_known=privacy_policy_known,
            human_permission_granted=human_permission_granted,
        )

    def receive_external_result(
        self,
        request_id: str,
        acquisition_result: AcquisitionResult,
        domain: str | None = None,
    ) -> InboundFilterResult | None:
        return self.acquisition_service.process_inbound_result(
            request_id=request_id,
            acquisition_result=acquisition_result,
            domain=domain,
        )

    def apply_acquired_fields(
        self,
        request_id: str,
        filled_fields: dict,
        extra_filled_fields_metadata: dict | None = None,
    ) -> AcquisitionRequest | None:
        return self.acquisition_service.apply_cleaned_fields(
            request_id=request_id,
            filled_fields=filled_fields,
            extra_filled_fields_metadata=extra_filled_fields_metadata,
        )

    def evaluate_acquisition_readiness(
        self,
        request_id: str,
    ) -> ReadinessEvaluation | None:
        return self.acquisition_service.evaluate_readiness(
            request_id=request_id,
        )