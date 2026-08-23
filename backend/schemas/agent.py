from pydantic import BaseModel, Field


class ShouldIApplyRequest(BaseModel):

    resume_id: int = Field(
        ...,
        gt=0,
    )

    jd_text: str = Field(
        ...,
        min_length=20,
    )


class ShouldIApplyResponse(BaseModel):

    match_score: float

    matched_skills: list[str]

    missing_skills: list[str]

    roadmap: list[dict]

    resources: list[dict]

    recommendation: str

    reasoning: str

    estimated_prep_time: str