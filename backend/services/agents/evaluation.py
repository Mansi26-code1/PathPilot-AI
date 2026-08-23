# ============================================================
# Evaluation — automated checks for agent output quality
# ============================================================

def evaluate_no_hallucination(structured_resume: dict, matched_skills: list) -> dict:
    """
    Confirms every 'matched' skill has evidence somewhere in the
    resume — either the Skills section or elsewhere (Experience,
    Projects), matching how Phase 3's matcher actually works.
    """

    resume_skills = set(
        s.lower() for s in structured_resume.get("skills_flat", [])
    )

    # Also check experience/projects text, since Phase 3 matching
    # considers resume-wide evidence, not just the Skills section
    extra_text = " ".join(
        structured_resume.get("experience", []) +
        structured_resume.get("projects", [])
    ).lower()

    claimed = set(s.lower() for s in matched_skills)

    hallucinated = [
        skill for skill in claimed
        if skill not in resume_skills and skill not in extra_text
    ]

    return {
        "passed": len(hallucinated) == 0,
        "hallucinated_skills": hallucinated
    }

def evaluate_recommendation_valid(recommendation: str) -> dict:
    """
    Confirms the final recommendation is one of the allowed values.
    """
    valid_values = {"APPLY_NOW", "PREPARE_FIRST"}

    return {
        "passed": recommendation in valid_values,
        "value": recommendation
    }


def evaluate_no_guaranteed_outcome(reasoning: str) -> dict:
    """
    Confirms the reasoning doesn't make guarantees about job
    outcomes (e.g. 'you will definitely get this job'), per the
    grounding rule from the Final Decision Agent prompt.
    """
    banned_phrases = [
        "will get the job",
        "guaranteed",
        "you will definitely",
        "100% chance"
    ]

    reasoning_lower = reasoning.lower()
    violations = [p for p in banned_phrases if p in reasoning_lower]

    return {
        "passed": len(violations) == 0,
        "violations": violations
    }


def evaluate_resources_have_urls(resources: list) -> dict:
    """
    Confirms every resource has a real URL — catches the kind of
    invented/missing-link issue we guarded against in Phase 5 RAG.
    """
    missing_url = [r for r in resources if not r.get("url")]

    return {
        "passed": len(missing_url) == 0,
        "resources_missing_url": len(missing_url)
    }


def run_full_evaluation(final_state: dict) -> dict:
    """
    Runs all evaluation checks on a completed agent workflow's
    final state and returns a combined report.
    """

    results = {
        "no_hallucination": evaluate_no_hallucination(
            final_state.get("structured_resume", {}) or {},
            final_state.get("matched_skills", []) or []
        ),
        "recommendation_valid": evaluate_recommendation_valid(
            final_state.get("recommendation")
        ),
        "no_guaranteed_outcome": evaluate_no_guaranteed_outcome(
            final_state.get("reasoning", "") or ""
        ),
        "resources_have_urls": evaluate_resources_have_urls(
            final_state.get("resources", []) or []
        )
    }

    all_passed = all(check["passed"] for check in results.values())

    return {
        "all_passed": all_passed,
        "checks": results
    }