from typing import Any, Dict

from .schemas import (
    GovernanceVerdict,
    GovernanceVisibilityLevel,
)


class VisibilityFilterError(ValueError):
    pass


def apply_visibility_scope(
    payload: Dict[str, Any],
    verdict: GovernanceVerdict,
) -> Dict[str, Any]:

    """
    Runtime-side deterministic filtering.

    Governance decides:
    - visibility level
    - restrictions
    - allowed scopes

    Runtime:
    - does NOT invent filtering rules
    - does NOT reinterpret governance
    - only applies governance decision
    """

    visibility = verdict.governance_visibility_level

    # ==========================================
    # INTERNAL ONLY
    # ==========================================

    if visibility == GovernanceVisibilityLevel.INTERNAL_ONLY:

        return payload

    # ==========================================
    # TRUSTED HUMAN
    # ==========================================

    if visibility == GovernanceVisibilityLevel.TRUSTED_HUMAN:

        trusted_payload = payload.get(
            "trusted_human"
        )

        if trusted_payload is None:

            raise VisibilityFilterError(
                "trusted_human payload missing"
            )

        return trusted_payload

    # ==========================================
    # HUMAN SAFE
    # ==========================================

    if visibility == GovernanceVisibilityLevel.HUMAN_SAFE:

        human_payload = payload.get(
            "human_safe"
        )

        if human_payload is None:

            raise VisibilityFilterError(
                "human_safe payload missing"
            )

        return human_payload

    # ==========================================
    # PUBLIC FILTERED
    # ==========================================

    if visibility == GovernanceVisibilityLevel.PUBLIC_FILTERED:

        public_payload = payload.get(
            "public"
        )

        if public_payload is None:

            raise VisibilityFilterError(
                "public payload missing"
            )

        return public_payload

    # ==========================================
    # EXTERNAL MINIMAL
    # ==========================================

    if visibility == GovernanceVisibilityLevel.EXTERNAL_MINIMAL:

        external_payload = payload.get(
            "external_minimal"
        )

        if external_payload is None:

            raise VisibilityFilterError(
                "external_minimal payload missing"
            )

        return external_payload

    raise VisibilityFilterError(
        f"unsupported visibility level: {visibility}"
    )