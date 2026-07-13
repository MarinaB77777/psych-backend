from assessment.analysis.statistics.grouping import (
    collect_grouped_numeric_values_bidirectional,
)
from assessment.analysis.statistics.one_way_anova import (
    one_way_anova_test,
)


def run_one_way_anova(
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

    if len(groups) < 3:
        return {
            "ok": False,
            "status": "three_or_more_groups_required",
            "method_id": "one_way_anova",
            "observed_group_count": len(groups),
        }

    test_result = one_way_anova_test(
        groups=groups,
    )

    if not test_result.get("ok"):
        return {
            "ok": False,
            "method_id": "one_way_anova",
            **test_result,
        }

    alpha = test_result["alpha"]
    p_value = test_result["p_value"]

    return {
        "ok": True,
        "status": "completed",
        "analysis_type": "statistical_method_run",
        "study_id": study_id,
        "method_id": "one_way_anova",
        "method_title": "One-way ANOVA",
        "left_question_code": left_question_code,
        "right_question_code": right_question_code,
        "sample_size": test_result["sample_size"],
        "test_statistic": test_result["test_statistic"],
        "test_statistic_name": test_result["test_statistic_name"],
        "degrees_of_freedom": test_result["degrees_of_freedom"],
        "alpha": alpha,
        "p_value": p_value,
        "is_statistically_significant": (
            p_value is not None and p_value < alpha
        ),
        "null_hypothesis": (
            "All independent groups have equal outcome means."
        ),
        "alternative_hypothesis": (
            "At least one independent group mean differs."
        ),
        "decision": test_result["decision"],
        "group_summary": test_result["group_summary"],
        "results": {
            "f_statistic": test_result["test_statistic"],
            "degrees_of_freedom": test_result["degrees_of_freedom"],
            "p_value": p_value,
            "sum_of_squares": test_result["sum_of_squares"],
            "mean_squares": test_result["mean_squares"],
        },
        "interpretation": {
            "summary": (
                "One-way ANOVA was calculated for three or more independent "
                "groups using the selected numeric outcome."
            ),
        },
    }
