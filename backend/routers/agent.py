from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user

from backend.crud.user import get_user_by_email
from backend.crud.resume import get_resume_by_id

from backend.schemas.agent import (
    ShouldIApplyRequest,
    ShouldIApplyResponse,
)

from backend.services.agents.graph import app as agent_app


router = APIRouter(
    prefix="/agent",
    tags=["AI Agent"],
)


@router.post(
    "/should-i-apply",
    response_model=ShouldIApplyResponse,
)
def should_i_apply(
    request: ShouldIApplyRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):

    # ========================================================
    # USER
    # ========================================================

    user = get_user_by_email(
        db,
        current_user["sub"],
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # ========================================================
    # RESUME
    # ========================================================

    resume = get_resume_by_id(
        db,
        request.resume_id,
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    # ========================================================
    # OWNERSHIP
    # ========================================================

    if resume.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to use this resume",
        )

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    jd_text = request.jd_text.strip()

    if len(jd_text) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short to analyze.",
        )

    # ========================================================
    # INITIAL AGENT STATE
    # ========================================================

    initial_state = {
        "resume_id": request.resume_id,
        "jd_text": jd_text,

        "resume_text": None,
        "structured_resume": None,

        "match_score": None,
        "matched_skills": [],
        "missing_skills": [],

        "roadmap": [],
        "resources": [],

        "recommendation": None,
        "reasoning": None,
        "estimated_prep_time": None,
    }

    # ========================================================
    # RUN LANGGRAPH
    # ========================================================

    try:

        result = agent_app.invoke(
            initial_state
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Application analysis agent failed. "
                f"Reason: {str(error)}"
            ),
        )

    # ========================================================
    # SAFE OUTPUT
    # ========================================================

    return {
        "match_score": float(
            result.get("match_score") or 0
        ),

        "matched_skills": (
            result.get("matched_skills")
            or []
        ),

        "missing_skills": (
            result.get("missing_skills")
            or []
        ),

        "roadmap": (
            result.get("roadmap")
            or []
        ),

        "resources": (
            result.get("resources")
            or []
        ),

        "recommendation": (
            result.get("recommendation")
            or "PREPARE_FIRST"
        ),

        "reasoning": (
            result.get("reasoning")
            or "No reasoning was generated."
        ),

        "estimated_prep_time": (
            result.get("estimated_prep_time")
            or "Unknown"
        ),
    }