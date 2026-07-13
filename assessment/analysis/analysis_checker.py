from assessment.analysis.analysis_method_registry import METHODS
from assessment.analysis.variable_metadata import build_variable_metadata
from assessment.analysis.checks.data_available import (
    check_variable_has_data,
)
from assessment.analysis.checks.scale_pattern import (
    check_scale_pattern_supported,
)
from assessment.analysis.checks.observed_groups import (
    check_observed_groups,
)
from assessment.analysis.checks.paired_observations import (
    check_paired_observations,
)
from assessment.analysis.checks.sample_size import (
    check_minimum_paired_sample_size,
)
from assessment.analysis.checks.monotonic_relationship import (
    check_monotonic_relationship_plausible,
)
from assessment.analysis.method_check_map import METHOD_CHECK_MAP
from assessment.analysis.checks.scale_defined import (
    check_scale_defined,
)
from assessment.analysis.checks.complete_pairs import (
    check_minimum_complete_pairs,
)
from assessment.analysis.checks.constant_variable import (
    check_not_constant_variable,
)
from assessment.analysis.checks.contingency_table import (
    check_contingency_table,
    check_two_by_two_table,
)
from assessment.analysis.checks.expected_counts import (
    check_expected_cell_counts,
)
from assessment.analysis.checks.group_balance import (
    check_group_balance,
)
from assessment.analysis.checks.group_size import (
    check_minimum_group_size,
)
from assessment.analysis.checks.linear_relationship import (
    check_linear_relationship_plausible,
)
from assessment.analysis.checks.normality import (
    check_approximately_normal_or_sufficient_sample,
)
from assessment.analysis.checks.numeric_data import (
    check_numeric_data,
)
from assessment.analysis.checks.outliers import (
    check_extreme_outliers_iqr,
)
from assessment.analysis.checks.variance import (
    check_variance_assumption,
)

def _values_for_question(answer_records: list[dict], question_code: str) -> list:
    return [
        record.get("answer_value")
        for record in answer_records
        if record.get("question_code") == question_code
    ]


def _non_missing(values: list) -> list:
    return [
        value for value in values
        if value is not None and value != ""
    ]


def _find_method(method_id: str) -> dict | None:
    for method in METHODS:
        if method.get("method_id") == method_id:
            return method
    return None


def _scale_matches(method: dict, left_scale: str | None, right_scale: str | None) -> bool:
    if not left_scale or not right_scale:
        return False

    for pattern in method.get("scale_patterns", []):
        if (
            left_scale in pattern.get("left", [])
            and right_scale in pattern.get("right", [])
        ):
            return True

    return False


def _participant_key(record: dict) -> str | None:
    return (
        record.get("participant_id")
        or record.get("subject_link_id")
        or record.get("session_id")
        or record.get("record_id")
    )


def _paired_question_values(
    *,
    answer_records: list[dict],
    left_question_code: str,
    right_question_code: str,
) -> list[dict]:
    by_subject = {}

    for record in answer_records:
        key = _participant_key(record)

        if not key:
            continue

        if key not in by_subject:
            by_subject[key] = {
                "participant_key": key,
                "session_ids": set(),
            }

        session_id = record.get("session_id")
        if session_id:
            by_subject[key]["session_ids"].add(session_id)

        code = record.get("question_code")
        value = record.get("answer_value")

        if value is None or value == "":
            continue

        if code == left_question_code:
            by_subject[key]["left"] = value

        if code == right_question_code:
            by_subject[key]["right"] = value

    pairs = []

    for item in by_subject.values():
        if "left" in item and "right" in item:
            pairs.append({
                "participant_key": item["participant_key"],
                "session_ids": sorted(item["session_ids"]),
                "left": item["left"],
                "right": item["right"],
            })

    return pairs


def _group_context(
    *,
    pairs: list[dict],
    left_scale: str | None,
    right_scale: str | None,
) -> dict:
    if left_scale == "nominal" and right_scale != "nominal":
        group_side = "left"
        outcome_side = "right"
    elif right_scale == "nominal" and left_scale != "nominal":
        group_side = "right"
        outcome_side = "left"
    else:
        group_side = "left"
        outcome_side = "right"

    group_values = [pair[group_side] for pair in pairs]
    outcome_values = [pair[outcome_side] for pair in pairs]

    groups = {}
    for group, outcome in zip(group_values, outcome_values):
        groups.setdefault(group, []).append(outcome)

    return {
        "group_side": group_side,
        "outcome_side": outcome_side,
        "group_values": group_values,
        "outcome_values": outcome_values,
        "groups": groups,
    }


def _check_group_count(
    *,
    group_values: list,
    required: str,
) -> dict:
    groups = sorted(set(
        value
        for value in group_values
        if value is not None and value != ""
    ))

    if not groups:
        status = "blocked"
    elif required == "two_groups":
        status = "passed" if len(groups) == 2 else "failed"
    else:
        status = "passed" if len(groups) >= 3 else "failed"

    return {
        "check_id": required,
        "status": status,
        "details": {
            "group_count": len(groups),
            "groups": groups,
        },
    }


def _check_pair_independence(pairs: list[dict]) -> dict:
    participant_keys = [
        pair["participant_key"]
        for pair in pairs
        if pair.get("participant_key")
    ]
    repeated_sessions = {
        pair["participant_key"]: pair["session_ids"]
        for pair in pairs
        if len(pair.get("session_ids") or []) > 1
    }

    if not participant_keys:
        status = "blocked"
    elif repeated_sessions:
        status = "warning"
    else:
        status = "passed"

    return {
        "check_id": "independent_observations",
        "status": status,
        "details": {
            "analysis_unit_count": len(participant_keys),
            "unique_analysis_unit_count": len(set(participant_keys)),
            "repeated_session_units": repeated_sessions,
            "note": "Pairs from the same participant are treated as one analysis unit; warning means repeated sessions need explicit design handling.",
        },
    }


def _combine_check_status(check_id: str, checks: list[dict]) -> dict:
    statuses = [check.get("status") for check in checks]

    if any(status == "failed" for status in statuses):
        status = "failed"
    elif any(status == "blocked" for status in statuses):
        status = "blocked"
    elif any(status == "warning" for status in statuses):
        status = "warning"
    else:
        status = "passed"

    return {
        "check_id": check_id,
        "status": status,
        "details": {
            "checks": checks,
        },
    }


def _check_numeric_for_method(
    *,
    left_values: list,
    right_values: list,
    left_scale: str | None,
    right_scale: str | None,
    group_context: dict,
) -> dict:
    if left_scale == "nominal" or right_scale == "nominal":
        return check_numeric_data(
            values=group_context["outcome_values"],
            variable_name=group_context["outcome_side"],
        )

    return _combine_check_status(
        "numeric_data",
        [
            check_numeric_data(
                values=left_values,
                variable_name="left",
            ),
            check_numeric_data(
                values=right_values,
                variable_name="right",
            ),
        ],
    )


def _check_normality_for_method(
    *,
    left_values: list,
    right_values: list,
    left_scale: str | None,
    right_scale: str | None,
    group_context: dict,
) -> dict:
    if left_scale == "nominal" or right_scale == "nominal":
        checks = [
            check_approximately_normal_or_sufficient_sample(
                values=values,
            )
            for values in group_context["groups"].values()
        ] or [
            check_approximately_normal_or_sufficient_sample(
                values=group_context["outcome_values"],
            )
        ]
    else:
        checks = [
            check_approximately_normal_or_sufficient_sample(
                values=left_values,
            ),
            check_approximately_normal_or_sufficient_sample(
                values=right_values,
            ),
        ]

    return _combine_check_status(
        "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
        checks,
    )


def check_pair_analysis(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    method_id: str,
    answer_records: list[dict],
) -> dict:
    metadata = build_variable_metadata(study_id)

    if not metadata:
        metadata = _metadata_from_answer_records(answer_records)

    left_meta = metadata.get(left_question_code, {})
    right_meta = metadata.get(right_question_code, {})

    method = _find_method(method_id)

    if method is None:
        return {
            "ok": False,
            "status": "method_not_found",
            "method_id": method_id,
        }
    
    required_checks = METHOD_CHECK_MAP.get(method_id)

    if required_checks is None:
        return {
            "ok": False,
            "status": "method_check_map_not_found",
            "method_id": method_id,
        }

    left_values = _values_for_question(answer_records, left_question_code)
    right_values = _values_for_question(answer_records, right_question_code)

    left_non_missing = _non_missing(left_values)
    right_non_missing = _non_missing(right_values)

    left_scale = left_meta.get("scale_type")
    right_scale = right_meta.get("scale_type")
    pairs = _paired_question_values(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )
    group_context = _group_context(
        pairs=pairs,
        left_scale=left_scale,
        right_scale=right_scale,
    )

    checks = []

    checks.append(
        check_variable_has_data(
            question_code=left_question_code,
            answer_records=answer_records,
            side="left",
        )
    )

    checks.append(
        check_variable_has_data(
            question_code=right_question_code,
            answer_records=answer_records,
            side="right",
        )
    )

    checks.append(
        check_scale_defined(
            left_scale=left_scale,
            right_scale=right_scale,
        )
    )

    checks.append(
        check_scale_pattern_supported(
            method=method,
            left_scale=left_scale,
            right_scale=right_scale,
        )
    )

    checks.append(
        check_observed_groups(
            values=left_non_missing,
            side="left",
        )
    )

    checks.append(
        check_observed_groups(
            values=right_non_missing,
            side="right",
        )
    )

    checks.append(
        check_not_constant_variable(
            values=left_values,
            variable_name=left_question_code,
        )
    )

    checks.append(
        check_not_constant_variable(
            values=right_values,
            variable_name=right_question_code,
        )
    )


    for condition in method.get("required_conditions", []):
        if condition == "paired_observations":
            paired_check = check_paired_observations(
                answer_records=answer_records,
                left_question_code=left_question_code,
                right_question_code=right_question_code,
            )

            checks.append(paired_check)

            checks.append(
                check_minimum_paired_sample_size(
                    paired_count=paired_check["details"]["paired_subject_count"],
                    minimum_required=3,
                )
            )

            checks.append(
                check_minimum_complete_pairs(
                    left_values=left_values,
                    right_values=right_values,
                    minimum_required=3,
                )
            )

            continue

        if condition == "independent_observations":
            checks.append(_check_pair_independence(pairs))
            continue

        if condition == "two_groups":
            checks.append(
                _check_group_count(
                    group_values=group_context["group_values"],
                    required="two_groups",
                )
            )
            continue

        if condition == "three_or_more_groups":
            checks.append(
                _check_group_count(
                    group_values=group_context["group_values"],
                    required="three_or_more_groups",
                )
            )
            continue

        if condition == "linear_relationship_plausible":
            checks.append(
                check_linear_relationship_plausible(
                    left_values=left_values,
                    right_values=right_values,
                    minimum_pairs=3,
                )
            )
            continue

        if condition == "monotonic_relationship_plausible":
            checks.append(
                check_monotonic_relationship_plausible(
                    answer_records=answer_records,
                    left_question_code=left_question_code,
                    right_question_code=right_question_code,
                    minimum_pairs=3,
                )
            )
            continue

        if condition == "no_extreme_outliers":
            checks.append(
                check_extreme_outliers_iqr(
                    values=group_context["outcome_values"],
                )
            )
            continue

        if condition == "approximately_normal_outcome_within_groups_or_sufficient_sample_size":
            checks.append(
                _check_normality_for_method(
                    left_values=left_values,
                    right_values=right_values,
                    left_scale=left_scale,
                    right_scale=right_scale,
                    group_context=group_context,
                )
            )
            continue

        if condition == "variance_assumption_checked":
            checks.append(
                check_variance_assumption(
                    groups=group_context["groups"],
                )
            )
            continue

        if condition == "sufficient_expected_cell_counts":
            checks.append(
                check_expected_cell_counts(
                    left_values=left_values,
                    right_values=right_values,
                )
            )
            continue

        if condition == "two_by_two_table":
            checks.append(
                check_two_by_two_table(
                    left_values=left_values,
                    right_values=right_values,
                )
            )
            continue

        checks.append({
            "check_id": condition,
            "status": "pending",
            "details": {
                "reason": "not implemented yet in analyzer checks",
            },
        })

    for check_id in required_checks:
        if any(check.get("check_id") == check_id for check in checks):
            continue

        if check_id == "numeric_data":
            checks.append(
                _check_numeric_for_method(
                    left_values=left_values,
                    right_values=right_values,
                    left_scale=left_scale,
                    right_scale=right_scale,
                    group_context=group_context,
                )
            )
            continue

        if check_id == "minimum_group_size":
            checks.append(
                check_minimum_group_size(
                    group_values=group_context["group_values"],
                    minimum_per_group=2,
                )
            )
            continue

        if check_id == "group_balance":
            checks.append(
                check_group_balance(
                    group_values=group_context["group_values"],
                )
            )
            continue

        if check_id == "contingency_table":
            checks.append(
                check_contingency_table(
                    left_values=left_values,
                    right_values=right_values,
                )
            )
            continue

        if check_id == "expected_cell_counts":
            checks.append(
                check_expected_cell_counts(
                    left_values=left_values,
                    right_values=right_values,
                )
            )
            continue

        if check_id == "approximately_normal_outcome_within_groups_or_sufficient_sample_size":
            checks.append(
                _check_normality_for_method(
                    left_values=left_values,
                    right_values=right_values,
                    left_scale=left_scale,
                    right_scale=right_scale,
                    group_context=group_context,
                )
            )
            continue

    failed = [
        check for check in checks
        if check.get("status") == "failed"
    ]

    pending = [
        check for check in checks
        if check.get("status") == "pending"
    ]

    blocked = [
        check for check in checks
        if check.get("status") == "blocked"
    ]

    if failed:
        status = "not_applicable"
    elif blocked:
        status = "not_enough_data"
    elif pending:
        status = "candidate_needs_more_checks"
    else:
        status = "applicable"

    return {
        "ok": True,
        "analysis_type": "pair_analysis_check",
        "study_id": study_id,
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "method": method,
        "required_checks": required_checks,
        "left_variable": left_meta,
        "right_variable": right_meta,
        "status": status,
        "checks": checks,
    }

def _metadata_from_answer_records(
    answer_records: list[dict],
) -> dict:
    metadata = {}

    for record in answer_records:
        code = record.get("question_code")

        if not code:
            continue

        if code not in metadata:
            metadata[code] = {
                "question_code": code,
                "title": record.get("title"),
                "scale_type": record.get("scale_type"),
                "question_type": record.get("question_type"),
            }

        for key in ["title", "scale_type", "question_type"]:
            if metadata[code].get(key) is None and record.get(key) is not None:
                metadata[code][key] = record.get(key)

    return metadata
