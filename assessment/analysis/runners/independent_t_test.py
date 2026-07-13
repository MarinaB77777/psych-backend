from assessment.analysis.statistics.descriptive import (
    group_descriptive_summary,
)
from assessment.analysis.statistics.grouping import (
    collect_grouped_numeric_values_bidirectional,
)
from assessment.analysis.statistics.t_test import (
    welch_t_test,
)


def run_independent_t_test(
    *,
    study_id: str,
    left_question_code: str,
    right_question_code: str,
    answer_records: list[dict],
) -> dict:
    groups = collect_grouped_numeric_values_bidirectional(
        answer_records=answer_records,
        left_question_code=left_question_code,
        right_question_code=right_question_code,
    )

    if len(groups) != 2:
        return {
            "ok": False,
            "status": "two_groups_required",
            "method_id": "independent_t_test",
            "observed_group_count": len(groups),
        }

    group_names = sorted(groups.keys())
    group_1_name = group_names[0]
    group_2_name = group_names[1]
    group_1 = groups[group_1_name]
    group_2 = groups[group_2_name]

    test_result = welch_t_test(
        group_1=group_1,
        group_2=group_2,
    )

    if not test_result.get("ok"):
        return {
            "ok": False,
            "method_id": "independent_t_test",
            **test_result,
        }

    alpha = test_result["alpha"]
    p_value = test_result["p_value"]

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "independent_t_test",
        "method_title": "Independent samples t-test",
        "method_variant": "welch_t_test",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": len(group_1) + len(group_2),
        "test_statistic": test_result["test_statistic"],
        "test_statistic_name": test_result["test_statistic_name"],
        "degrees_of_freedom": test_result["degrees_of_freedom"],
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": (
            p_value is not None and p_value < alpha
        ),
        "null_hypothesis": (
            "The two independent groups have equal outcome means."
        ),
        "alternative_hypothesis": (
            "The two independent groups have different outcome means."
        ),
        "decision": test_result["decision"],
        "group_summary": {
            group_1_name: group_descriptive_summary(group_1),
            group_2_name: group_descriptive_summary(group_2),
        },
        "results": {
            "t_statistic": test_result["test_statistic"],
            "degrees_of_freedom": test_result["degrees_of_freedom"],
            "p_value": p_value,
        },
        "interpretation": {
            "summary": (
                "Welch independent samples t-test was calculated for two "
                "independent groups using the selected numeric outcome."
            ),
        },
    }
