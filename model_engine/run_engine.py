from model_engine.coverage import compute_coverage
from model_engine.quality import compute_q_basic
from model_engine.states import (
    determine_initial_state,
    determine_final_state,
)
from model_engine.resources import compute_r
from model_engine.markers import compute_k_self
from model_engine.loads import compute_loads
from model_engine.stress import compute_s
from model_engine.delta import compute_delta
from model_engine.consistency import compute_consistency
from model_engine.outputs import build_output
from model_engine.pressure import compute_pressure
from model_engine.multipliers import compute_multipliers
from model_engine.questions import build_next_questions
from model_engine.reasons import (
    normalize_reason_codes,
    extract_public_reasons,
)

def run_engine_logic(answers: dict):
    coverage_data = compute_coverage(answers)

    q_data = compute_q_basic(
        answers=answers,
        coverage_data=coverage_data,
    )

    state_data = determine_initial_state(
        coverage_data=coverage_data,
        q_data=q_data,
        answers=answers,
    )

    r_data = compute_r(answers)
    k_self_data = compute_k_self(answers)

    loads_data = compute_loads(answers)
    
    pressure_data = compute_pressure(
        answers=answers,
        loads_data=loads_data,
        r_data=r_data,
   )
    
    multipliers_data = compute_multipliers(
        answers=answers,
        r_data=r_data,
        loads_data=loads_data,
    )

    s_data = compute_s(
        loads_data=loads_data,
        r_data=r_data,
        pressure_data=pressure_data,
        multipliers_data=multipliers_data,
    )


    if state_data["state"] == "CRITICAL":
        s_data["s_final"] = 10
        s_data["critical_override"] = True
    else:
        s_data["critical_override"] = False


    delta_data = compute_delta(
        r_data=r_data,
        k_self_data=k_self_data,
    )

    c_data = compute_consistency(delta_data)

    final_state_data = determine_final_state(
        initial_state=state_data["state"],
        s_data=s_data,
        k_self_data=k_self_data,
        consistency_data=c_data,
        coverage_data=coverage_data,
        q_data=q_data,
    )

    next_questions = build_next_questions(
        coverage_data=coverage_data,
        delta_data=delta_data,
        consistency_data=c_data,
        limit=3,
    )

    confidence = "low"

    if coverage_data["coverage"] >= 0.6 and q_data["q_global"] <= 1:
        confidence = "medium"

    if coverage_data["coverage"] >= 0.8 and q_data["q_global"] == 0:
        confidence = "high"

    combined_reason_codes = (
        state_data["reason_codes"]
        + final_state_data["reason_codes"]
    )

    normalized_reasons = normalize_reason_codes(combined_reason_codes)
    public_reasons = extract_public_reasons(normalized_reasons)

    output_data = build_output(
        state=final_state_data["state"],
        confidence=confidence,
        coverage=coverage_data["coverage"],
        q_global=q_data["q_global"],
        c_final=c_data["c_final"],
        s_data=s_data,
        r_data=r_data,
        k_self_data=k_self_data,
        delta_data=delta_data,
        warnings=state_data["warnings"],
        public_reasons=public_reasons,
        next_questions=next_questions,
    )


    result = {
        "initial_state": state_data["state"],
        "state": final_state_data["state"],
        "confidence": confidence,
        "engine_location": "backend",
        "coverage": coverage_data["coverage"],
        "missing_fields": coverage_data["missing_fields"],
        "q_global": q_data["q_global"],
        "warnings": state_data["warnings"],
        "reason_codes": combined_reason_codes,
        "r": r_data,
        "k_self": k_self_data,
        "loads": loads_data,
        "pressure": pressure_data,
        "multipliers": multipliers_data,
        "s": s_data,
        "delta": delta_data,
        "consistency": c_data,
        "c_final": c_data["c_final"],
        "output": output_data,
        "next_questions": next_questions,
        "normalized_reasons": normalized_reasons,
        "public_reasons": public_reasons,
    }

    return result