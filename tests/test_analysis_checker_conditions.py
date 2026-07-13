from assessment.analysis.analysis_checker import check_pair_analysis
from research.analyses.health_model.model_parameter_analysis_checker import (
    check_model_parameter_pair_analysis,
)


def _group_records(group_count: int = 2) -> list[dict]:
    groups = ["A", "B", "C"][:group_count]
    records = []
    participant_number = 1

    for group_index, group in enumerate(groups):
        for offset in range(4):
            participant_id = f"p{participant_number}"
            outcome = 10 + group_index * 4 + offset
            records.extend([
                {
                    "participant_id": participant_id,
                    "session_id": f"s{participant_number}",
                    "question_code": "group",
                    "answer_value": group,
                    "scale_type": "nominal",
                },
                {
                    "participant_id": participant_id,
                    "session_id": f"s{participant_number}",
                    "question_code": "outcome",
                    "answer_value": outcome,
                    "scale_type": "continuous",
                },
            ])
            participant_number += 1

    return records


def _correlation_records() -> list[dict]:
    records = []

    for index in range(8):
        participant_id = f"p{index}"
        records.extend([
            {
                "participant_id": participant_id,
                "session_id": f"s{index}",
                "question_code": "left",
                "answer_value": index + 1,
                "scale_type": "continuous",
            },
            {
                "participant_id": participant_id,
                "session_id": f"s{index}",
                "question_code": "right",
                "answer_value": (index + 1) * 2,
                "scale_type": "continuous",
            },
        ])

    return records


def _categorical_records() -> list[dict]:
    pairs = [
        ("yes", "low"),
        ("yes", "low"),
        ("yes", "high"),
        ("yes", "high"),
        ("no", "low"),
        ("no", "low"),
        ("no", "high"),
        ("no", "high"),
    ]
    records = []

    for index, (left, right) in enumerate(pairs):
        participant_id = f"p{index}"
        records.extend([
            {
                "participant_id": participant_id,
                "session_id": f"s{index}",
                "question_code": "left_cat",
                "answer_value": left,
                "scale_type": "nominal",
            },
            {
                "participant_id": participant_id,
                "session_id": f"s{index}",
                "question_code": "right_cat",
                "answer_value": right,
                "scale_type": "nominal",
            },
        ])

    return records


def _statuses(result: dict) -> dict:
    return {
        check["check_id"]: check["status"]
        for check in result["checks"]
    }


def test_group_methods_have_no_pending_checks():
    for method_id, group_count in [
        ("independent_t_test", 2),
        ("one_way_anova", 3),
        ("mann_whitney_u", 2),
        ("kruskal_wallis", 3),
    ]:
        result = check_pair_analysis(
            study_id="synthetic",
            left_question_code="group",
            right_question_code="outcome",
            method_id=method_id,
            answer_records=_group_records(group_count),
        )

        assert result["ok"] is True
        assert result["status"] == "applicable"
        assert "pending" not in _statuses(result).values()


def test_correlation_methods_have_no_pending_checks():
    for method_id in ["pearson_correlation", "spearman_correlation"]:
        result = check_pair_analysis(
            study_id="synthetic",
            left_question_code="left",
            right_question_code="right",
            method_id=method_id,
            answer_records=_correlation_records(),
        )

        assert result["ok"] is True
        assert result["status"] == "applicable"
        assert "pending" not in _statuses(result).values()


def test_categorical_methods_have_no_pending_checks():
    for method_id in ["chi_square", "fisher_exact"]:
        result = check_pair_analysis(
            study_id="synthetic",
            left_question_code="left_cat",
            right_question_code="right_cat",
            method_id=method_id,
            answer_records=_categorical_records(),
        )

        assert result["ok"] is True
        assert result["status"] == "applicable"
        assert "pending" not in _statuses(result).values()


def test_health_model_parameter_checker_matches_general_checker():
    dataset = {
        "ok": True,
        "study_id": "health_model",
        "analysis_scope": "synthetic",
        "observation_unit": "participant",
        "repeated_measure_policy": "single_session",
        "participant_reference": "participant_id",
        "selected_observation_count": 8,
        "compatible_answer_records": _group_records(2),
        "left_variable": {
            "variable_code": "group",
            "scale_type": "nominal",
        },
        "right_variable": {
            "variable_code": "outcome",
            "scale_type": "continuous",
        },
    }

    result = check_model_parameter_pair_analysis(
        dataset=dataset,
        method_id="independent_t_test",
    )

    assert result["ok"] is True
    assert result["status"] == "applicable"
    assert "pending" not in _statuses(result).values()
