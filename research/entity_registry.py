from assessment.studies.decision_under_uncertainty import QUESTION_BANK
from assessment.analysis.analysis_method_registry import METHODS


MODEL_PARAMETERS = [
    "StressBurden",
    "ResourceDeficit",
    "Pressure",
    "TrajectoryRisk",
    "CurrentState",
    "ModeledBurden",
    "BurdenManifestationDelta",
]

MODEL_MECHANISMS = [
    "CoincidenceBurden",
    "ResourceExhaustion",
    "DecisionDegradation",
    "DualFailure",
    "OptionSpaceCollapse",
    "RecoveryMismatch",
    "LearningFailure",
    "CommitmentTrap",
    "MismatchLoad",
    "NegativeSpiral",
]

def _question_entities(language: str = "ru") -> list[dict]:
    bank = QUESTION_BANK.get(language, QUESTION_BANK["ru"])
    result = []

    for code, question in bank.items():
        prompt = question.get("prompt") or question.get("text") or code

        result.append({
            "id": code,
            "type": "QUESTION",
            "label": f"{code} — {prompt}",
            "source": "question_bank",
            "study_id": "decision_under_uncertainty",
        })

    return result


def _simple_entities(items: list[str], entity_type: str, source: str) -> list[dict]:
    return [
        {
            "id": item,
            "type": entity_type,
            "label": item,
            "source": source,
        }
        for item in items
    ]


def _statistical_method_entities() -> list[dict]:
    return [
        {
            "id": method["method_id"],
            "type": "STATISTICAL_METHOD",
            "label": method.get("title") or method["method_id"],
            "source": "analysis_method_registry",
            "purpose": method.get("purpose"),
            "category": method.get("category"),
        }
        for method in METHODS
    ]


def list_entities(entity_type: str | None = None, language: str = "ru") -> list[dict]:
    entities = []

    entities += _question_entities(language=language)
    entities += _simple_entities(MODEL_PARAMETERS, "MODEL_PARAMETER", "model_registry")
    entities += _simple_entities(MODEL_MECHANISMS, "MODEL_MECHANISM", "model_registry")
    entities += _statistical_method_entities()

    if entity_type:
        return [item for item in entities if item.get("type") == entity_type]

    return entities
