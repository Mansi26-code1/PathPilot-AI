# ============================================================
# Guardrails — safety checks for the agent workflow
# ============================================================

MAX_ITERATIONS = 5
VALID_RECOMMENDATIONS = {"APPLY_NOW", "PREPARE_FIRST"}


def check_iteration_limit(iteration_count: int) -> None:
    """
    Prevents infinite loops — raises an error if the agent
    workflow has run more steps than expected.
    """
    if iteration_count > MAX_ITERATIONS:
        raise RuntimeError(
            f"Agent workflow exceeded max iterations ({MAX_ITERATIONS}). "
            "Stopping to prevent infinite loop."
        )


def validate_decision_schema(result: dict) -> bool:
    """
    Confirms the Final Decision Agent's output has the
    required fields and a valid recommendation value.
    """
    required_keys = {"recommendation", "reasoning", "estimated_prep_time"}

    if not required_keys.issubset(result.keys()):
        return False

    if result.get("recommendation") not in VALID_RECOMMENDATIONS:
        return False

    if not result.get("reasoning") or not isinstance(result.get("reasoning"), str):
        return False

    return True


def validate_match_score(score) -> bool:
    """
    Confirms match_score is a valid percentage (0-100).
    """
    return isinstance(score, (int, float)) and 0 <= score <= 100