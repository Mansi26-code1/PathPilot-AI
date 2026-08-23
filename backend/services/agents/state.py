from typing import Any, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """
    Shared state passed between all PathPilot AI agents.

    The LangGraph workflow progressively fills this state:

    Resume Agent
        ↓
    JD Match Agent
        ↓
    Roadmap Agent
        ↓
    Resource Agent
        ↓
    Final Decision Agent
    """

    # ========================================================
    # INPUT
    # ========================================================

    resume_id: int
    jd_text: str

    # ========================================================
    # RESUME DATA
    # ========================================================

    resume_text: Optional[str]
    structured_resume: Optional[dict[str, Any]]

    # ========================================================
    # JD MATCHING
    # ========================================================

    match_score: Optional[float]

    matched_skills: Optional[list[str]]
    missing_skills: Optional[list[str]]

    # Additional matching information
    jd_skills_detected: Optional[list[str]]
    skill_match_score: Optional[float]
    text_similarity_score: Optional[float]

    # ========================================================
    # PREPARATION
    # ========================================================

    roadmap: Optional[list[dict[str, Any]]]

    resources: Optional[list[dict[str, Any]]]

    # ========================================================
    # FINAL DECISION
    # ========================================================

    recommendation: Optional[str]

    reasoning: Optional[str]

    estimated_prep_time: Optional[str]

    # ========================================================
    # AGENT DEBUG / TRACE INFORMATION
    # ========================================================

    agent_trace: Optional[list[str]]