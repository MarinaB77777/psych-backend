import pytest

from research.answer_export_filter import (
    filter_answers_for_research_snapshot,
)


def test_filter_includes_reviewed_exportable_answer():
    result = filter_answers_for_research_snapshot(
        {
            "__example_d1": 3,
        }
    )

    assert result["included_answers"] == {
        "__example_d1": {
            "value": 3,
            "policy_category": "exportable",
            "reason_code": "ANSWER_INCLUDED_BY_POLICY",
            "policy_version": "answer-policy-1",
            "review_status": "reviewed",
            "allowed_export_scope": ["research_snapshot"],
        }
    }
    assert result["excluded_answers"] == {}
    assert result["answer_count"] == 1
    assert result["included_count"] == 1
    assert result["excluded_count"] == 0


def test_filter_excludes_unknown_answer_by_default_without_value_leak():
    result = filter_answers_for_research_snapshot(
        {
            "unknown_variable": "secret-value",
        }
    )

    assert result["included_answers"] == {}
    assert result["excluded_answers"] == {
        "unknown_variable": {
            "policy_category": "not_yet_classified",
            "reason_code": "ANSWER_POLICY_NOT_CLASSIFIED",
            "policy_version": "answer-policy-1",
            "review_status": "not_reviewed",
            "allowed_export_scope": [],
        }
    }
    assert "secret-value" not in str(result["excluded_answers"])
    assert "secret-value" not in str(result)


def test_filter_mixed_answers_includes_only_allowed_values():
    result = filter_answers_for_research_snapshot(
        {
            "__example_d1": 3,
            "unknown_variable": 7,
        }
    )

    assert "__example_d1" in result["included_answers"]
    assert "unknown_variable" in result["excluded_answers"]
    assert "unknown_variable" not in result["included_answers"]
    assert result["answer_count"] == 2
    assert result["included_count"] == 1
    assert result["excluded_count"] == 1


def test_filter_uses_normalized_variable_code_as_output_key():
    result = filter_answers_for_research_snapshot(
        {
            "  __example_d1  ": 3,
        }
    )

    assert "__example_d1" in result["included_answers"]
    assert "  __example_d1  " not in result["included_answers"]


def test_filter_excludes_duplicate_normalized_variable_code():
    result = filter_answers_for_research_snapshot(
        {
            "__example_d1": 3,
            "  __example_d1  ": 4,
        }
    )

    assert result["included_answers"] == {}
    assert result["excluded_answers"]["__example_d1"][
        "reason_code"
    ] == "DUPLICATE_NORMALIZED_VARIABLE_CODE"
    assert result["duplicate_variable_codes_detected"] == [
        "__example_d1"
    ]


def test_filter_rejects_non_dict_answers():
    with pytest.raises(ValueError):
        filter_answers_for_research_snapshot(
            ["not", "a", "dict"]
        )


@pytest.mark.parametrize(
    "answers",
    [
        {123: "bad"},
        {None: "bad"},
        {("tuple",): "bad"},
    ],
)
def test_filter_rejects_non_string_variable_codes(answers):
    with pytest.raises(ValueError):
        filter_answers_for_research_snapshot(answers)


def test_filter_returns_governance_boundary_flags():
    result = filter_answers_for_research_snapshot({})

    assert result["answer_policy_version"] == "answer-policy-1"
    assert result["filter_version"] == "answer-export-filter-1"
    assert result["filter_method"] == "static_answer_policy_lookup"
    assert result["filter_scope"] == "research_snapshot"
    assert result["count_basis"] == "unique_normalized_variable_codes"
    assert result["answer_values_filtered"] is True
    assert result["unknown_policy_default_deny"] is True
    assert (
        result["malformed_policy_handling"]
        == "not_implemented_static_registry_assumed_valid"
    )
    assert result["consent_evaluated"] is False
    assert result["retention_evaluated"] is False
    assert result["filter_is_not_consent_resolution"] is True
    assert result["filter_is_not_retention_engine"] is True
    assert result["filter_is_not_research_analytics"] is True
    assert result["filter_is_not_auto_classifier"] is True
    assert result["filter_is_not_export_authority"] is True
    assert result["filter_is_not_policy_review"] is True
    assert (
        result["included_answers_are_not_final_export_authorization"]
        is True
    )


def test_filter_marks_included_values_as_raw_policy_allowed():
    result = filter_answers_for_research_snapshot(
        {
            "__example_d1": 3,
        }
    )

    assert result["included_values_are_raw_policy_allowed"] is True