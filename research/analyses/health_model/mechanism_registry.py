MECHANISM_REGISTRY_SCHEMA_VERSION = "mechanism-registry-1"


def _mechanism(
    mechanism_id: str,
    title: str,
    mechanism_type: str,
    required_functions: list[str],
    supporting_functions: list[str],
    minimum_required: int,
    first_measurement_allowed_statuses: list[str],
    confirmed_requires_repeated_measurement: bool,
    trajectory_contributes_to: list[str],
):
    return {
        "id": mechanism_id,
        "title": title,
        "type": mechanism_type,
        "required_functions": required_functions,
        "supporting_functions": supporting_functions,
        "minimum_required": minimum_required,
        "first_measurement_allowed_statuses": first_measurement_allowed_statuses,
        "confirmed_requires_repeated_measurement": confirmed_requires_repeated_measurement,
        "trajectory_contributes_to": trajectory_contributes_to,
        "schema_version": MECHANISM_REGISTRY_SCHEMA_VERSION,
    }


MECHANISM_REGISTRY = {
    "option_space_collapse": _mechanism(
        mechanism_id="option_space_collapse",
        title="OptionSpaceCollapse",
        mechanism_type="latent_trajectory_mechanism",
        required_functions=[
            "perceived_option_availability",
            "option_generation",
            "perceived_agency",
            "future_expectancy",
            "perceived_controllability",
        ],
        supporting_functions=[
            "prioritization",
            "intolerance_of_uncertainty",
            "threat_appraisal",
            "uncertainty_evaluation",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "trajectory_risk",
            "decision_degradation",
            "reserve_discovery_failure",
            "future_path_restriction",
        ],
    ),

    "decision_degradation": _mechanism(
        mechanism_id="decision_degradation",
        title="DecisionDegradation",
        mechanism_type="latent_functional_mechanism",
        required_functions=[
            "working_memory",
            "executive_control",
            "belief_updating",
            "feedback_utilization",
            "cognitive_flexibility",
        ],
        supporting_functions=[
            "judgment",
            "risk_evaluation",
            "emotion_regulation",
            "distress_tolerance",
            "inhibitory_control",
            "metacognitive_monitoring",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "dual_failure",
            "learning_failure",
            "trajectory_risk",
        ],
    ),

    "resource_exhaustion": _mechanism(
        mechanism_id="resource_exhaustion",
        title="ResourceExhaustion",
        mechanism_type="latent_depletion_mechanism",
        required_functions=[
            "recovery_efficiency",
            "restoration_capacity",
            "recovery_regulation",
            "resilience",
        ],
        supporting_functions=[
            "working_memory",
            "executive_control",
            "emotion_regulation",
            "goal_commitment",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "dual_failure",
            "trajectory_risk",
            "recovery_mismatch",
        ],
    ),

    "recovery_mismatch": _mechanism(
        mechanism_id="recovery_mismatch",
        title="RecoveryMismatch",
        mechanism_type="latent_recovery_mechanism",
        required_functions=[
            "recovery_efficiency",
            "restoration_capacity",
            "resilience",
        ],
        supporting_functions=[
            "emotion_regulation",
            "feedback_utilization",
            "working_memory",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "resource_exhaustion",
            "trajectory_risk",
        ],
    ),

    "learning_failure": _mechanism(
        mechanism_id="learning_failure",
        title="LearningFailure",
        mechanism_type="latent_learning_mechanism",
        required_functions=[
            "feedback_utilization",
            "belief_updating",
            "error_monitoring",
            "strategy_switching",
        ],
        supporting_functions=[
            "goal_adjustment_capacity",
            "psychological_flexibility",
            "cognitive_flexibility",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "decision_degradation",
            "commitment_trap",
            "trajectory_risk",
        ],
    ),

    "commitment_trap": _mechanism(
        mechanism_id="commitment_trap",
        title="CommitmentTrap",
        mechanism_type="latent_commitment_mechanism",
        required_functions=[
            "goal_commitment",
            "goal_adjustment_capacity",
            "strategy_switching",
            "value_consistent_behavior",
        ],
        supporting_functions=[
            "distress_tolerance",
            "goal_directed_behavior",
            "psychological_flexibility",
        ],
        minimum_required=2,
        first_measurement_allowed_statuses=[
            "SUSPECTED",
            "LIKELY",
            "NOT_ENOUGH_DATA",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "learning_failure",
            "trajectory_risk",
        ],
    ),

    "dual_failure": _mechanism(
        mechanism_id="dual_failure",
        title="DualFailure",
        mechanism_type="composite_trajectory_mechanism",
        required_functions=[],
        supporting_functions=[],
        minimum_required=0,
        first_measurement_allowed_statuses=[
            "NOT_ENOUGH_DATA",
            "SUSPECTED",
        ],
        confirmed_requires_repeated_measurement=True,
        trajectory_contributes_to=[
            "high_risk_trajectory",
        ],
    ),
}


def get_mechanism(mechanism_id: str) -> dict | None:
    return MECHANISM_REGISTRY.get(mechanism_id)


def list_mechanisms() -> list[dict]:
    return list(MECHANISM_REGISTRY.values())