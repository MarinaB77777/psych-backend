METHODS = [
    {
        "method_id": "chi_square",
        "title": "Chi-square test of independence",
        "category": "standard",
        "purpose": "association_between_categorical_variables",
        "scale_patterns": [
            {"left": ["nominal", "ordinal"], "right": ["nominal", "ordinal"]},
        ],
        "required_conditions": [
            "independent_observations",
            "sufficient_expected_cell_counts",
        ],
    },
    {
        "method_id": "fisher_exact",
        "title": "Fisher exact test",
        "category": "standard",
        "purpose": "association_between_two_binary_categorical_variables",
        "scale_patterns": [
            {"left": ["nominal"], "right": ["nominal"]},
        ],
        "required_conditions": [
            "two_by_two_table",
            "independent_observations",
        ],
    },
    {
        "method_id": "spearman_correlation",
        "title": "Spearman rank correlation",
        "category": "standard",
        "purpose": "monotonic_association_between_ordered_or_numeric_variables",
        "scale_patterns": [
            {"left": ["ordinal", "interval", "ratio", "continuous"], "right": ["ordinal", "interval", "ratio", "continuous"]},
        ],
        "required_conditions": [
            "paired_observations",
            "monotonic_relationship_plausible",
        ],
    },
    {
        "method_id": "pearson_correlation",
        "title": "Pearson correlation",
        "category": "standard",
        "purpose": "linear_association_between_numeric_variables",
        "scale_patterns": [
            {"left": ["interval", "ratio", "continuous"], "right": ["interval", "ratio", "continuous"]},
        ],
        "required_conditions": [
            "paired_observations",
            "linear_relationship_plausible",
            "no_extreme_outliers",
        ],
    },
    {
        "method_id": "mann_whitney_u",
        "title": "Mann-Whitney U test",
        "category": "standard",
        "purpose": "compare_numeric_or_ordinal_outcome_between_two_independent_groups",
        "scale_patterns": [
            {"left": ["nominal"], "right": ["ordinal", "interval", "ratio", "continuous"]},
            {"left": ["ordinal", "interval", "ratio", "continuous"], "right": ["nominal"]},
        ],
        "required_conditions": [
            "two_groups",
            "independent_observations",
        ],
    },
    {
        "method_id": "kruskal_wallis",
        "title": "Kruskal-Wallis test",
        "category": "standard",
        "purpose": "compare_numeric_or_ordinal_outcome_between_three_or_more_independent_groups",
        "scale_patterns": [
            {"left": ["nominal"], "right": ["ordinal", "interval", "ratio", "continuous"]},
            {"left": ["ordinal", "interval", "ratio", "continuous"], "right": ["nominal"]},
        ],
        "required_conditions": [
            "three_or_more_groups",
            "independent_observations",
        ],
    },
    {
        "method_id": "independent_t_test",
        "title": "Independent samples t-test",
        "category": "standard",
        "purpose": "compare_numeric_outcome_between_two_independent_groups",
        "scale_patterns": [
            {"left": ["nominal"], "right": ["interval", "ratio", "continuous"]},
            {"left": ["interval", "ratio", "continuous"], "right": ["nominal"]},
        ],
        "required_conditions": [
            "two_groups",
            "independent_observations",
            "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
            "variance_assumption_checked",
        ],
    },
    {
        "method_id": "one_way_anova",
        "title": "One-way ANOVA",
        "category": "standard",
        "purpose": "compare_numeric_outcome_between_three_or_more_independent_groups",
        "scale_patterns": [
            {"left": ["nominal"], "right": ["interval", "ratio", "continuous"]},
            {"left": ["interval", "ratio", "continuous"], "right": ["nominal"]},
        ],
        "required_conditions": [
            "three_or_more_groups",
            "independent_observations",
            "approximately_normal_outcome_within_groups_or_sufficient_sample_size",
            "variance_assumption_checked",
        ],
    },
]