import json
import re

from groq import Groq

from backend.database import SessionLocal
from backend.crud.resume import get_resume_by_id

from backend.services.resume_parser import parse_resume
from backend.services.resume_extractor import extract_resume

from backend.services.mentor import generate_mentor_response
from backend.services.rag.chain import generate_rag_response

from backend.services.jd_matcher import match_resume_with_jd

from backend.config import GROQ_API_KEY, GROQ_MODEL

from backend.services.agents.state import AgentState
from backend.services.agents.guardrails import validate_decision_schema


# ============================================================
# GROQ CLIENT
# ============================================================

decision_client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# HELPERS
# ============================================================

def add_trace(
    state: AgentState,
    message: str
) -> AgentState:

    trace = state.get("agent_trace") or []

    trace.append(message)

    state["agent_trace"] = trace

    return state


def safe_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def extract_json_object(text: str):

    if not text:
        return {}

    try:

        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except Exception:
        pass

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    if match:

        try:

            result = json.loads(
                match.group(0)
            )

            if isinstance(result, dict):
                return result

        except Exception:
            pass

    return {}


# ============================================================
# 1. RESUME AGENT
# ============================================================

def resume_agent(
    state: AgentState
) -> AgentState:

    print("Resume Agent running...")

    add_trace(
        state,
        "Resume Agent started"
    )

    db = SessionLocal()

    try:

        resume = get_resume_by_id(
            db,
            state["resume_id"]
        )

        if not resume:

            state["resume_text"] = None
            state["structured_resume"] = None

            add_trace(
                state,
                "Resume Agent: resume not found"
            )

            return state

        resume_text = (
            resume.extracted_text or ""
        )

        if not resume_text.strip():

            state["resume_text"] = ""
            state["structured_resume"] = {}

            add_trace(
                state,
                "Resume Agent: resume text is empty"
            )

            return state

        sections = parse_resume(
            resume_text
        )

        structured_data = extract_resume(
            resume_text,
            sections
        )

        state["resume_text"] = resume_text

        state["structured_resume"] = (
            structured_data or {}
        )

        add_trace(
            state,
            "Resume Agent completed successfully"
        )

    except Exception as e:

        print(
            f"Resume Agent error: {e}"
        )

        state["resume_text"] = None
        state["structured_resume"] = None

        add_trace(
            state,
            f"Resume Agent failed: {str(e)}"
        )

    finally:

        db.close()

    return state


# ============================================================
# 2. JD MATCH AGENT
# ============================================================

def jd_match_agent(
    state: AgentState
) -> AgentState:

    print("JD Match Agent running...")

    add_trace(
        state,
        "JD Match Agent started"
    )

    structured_resume = (
        state.get("structured_resume")
    )

    resume_text = (
        state.get("resume_text") or ""
    )

    jd_text = (
        state.get("jd_text") or ""
    )

    if not structured_resume:

        state["match_score"] = 0.0
        state["matched_skills"] = []
        state["missing_skills"] = []
        state["jd_skills_detected"] = []
        state["skill_match_score"] = 0.0
        state["text_similarity_score"] = 0.0

        add_trace(
            state,
            "JD Match Agent: no structured resume available"
        )

        return state

    if not jd_text.strip():

        state["match_score"] = 0.0
        state["matched_skills"] = []
        state["missing_skills"] = []
        state["jd_skills_detected"] = []
        state["skill_match_score"] = 0.0
        state["text_similarity_score"] = 0.0

        add_trace(
            state,
            "JD Match Agent: JD is empty"
        )

        return state

    try:

        resume_skills = (
            structured_resume.get(
                "skills_flat",
                []
            )
        )

        result = match_resume_with_jd(

            resume_text=resume_text,

            jd_text=jd_text,

            resume_skills=resume_skills,

            structured_data=structured_resume
        )

        state["match_score"] = float(
            result.get(
                "overall_match_score",
                0.0
            )
        )

        state["matched_skills"] = (
            result.get(
                "matched_skills",
                []
            )
        )

        state["missing_skills"] = (
            result.get(
                "missing_skills",
                []
            )
        )

        state["jd_skills_detected"] = (
            result.get(
                "jd_skills_detected",
                []
            )
        )

        state["skill_match_score"] = (
            result.get(
                "skill_match_score",
                0.0
            )
        )

        state["text_similarity_score"] = (
            result.get(
                "text_similarity_score",
                0.0
            )
        )

        # Keep additional ATS/JD analysis if matcher provides it.
        if "breakdown" in result:
            state["ats_breakdown"] = result.get(
                "breakdown"
            )

        if "contact_info" in result:
            state["contact_info"] = result.get(
                "contact_info"
            )

        if "weak_phrases" in result:
            state["weak_phrases"] = result.get(
                "weak_phrases"
            )

        add_trace(
            state,
            "JD Match Agent completed successfully"
        )

    except Exception as e:

        print(
            f"JD Match Agent error: {e}"
        )

        state["match_score"] = 0.0
        state["matched_skills"] = []
        state["missing_skills"] = []

        add_trace(
            state,
            f"JD Match Agent failed: {str(e)}"
        )

    return state


# ============================================================
# 3. ROADMAP AGENT
# ============================================================

def roadmap_agent(
    state: AgentState
) -> AgentState:

    print("Roadmap Agent running...")

    add_trace(
        state,
        "Roadmap Agent started"
    )

    missing_skills = (
        state.get("missing_skills") or []
    )

    match_score = (
        state.get("match_score") or 0
    )

    structured_resume = (
        state.get("structured_resume") or {}
    )

    if not missing_skills:

        user_message = f"""
The candidate has a {match_score}% match with the job.

There are no major technical gaps.

Create a SHORT interview preparation roadmap.

Focus on:
1. validating existing skills
2. project explanation
3. likely interview questions
4. role-specific preparation

Return 3-5 roadmap steps.
"""

    else:

        missing_text = ", ".join(
            str(x)
            for x in missing_skills[:8]
        )

        user_message = f"""
The candidate has a {match_score}% match.

Important missing or weak skills:
{missing_text}

Create a focused preparation roadmap.

Prioritize only the highest-value requirements.

Return 3-5 ordered roadmap steps.

Each step must contain:
step
reason
priority
"""

    try:

        result = generate_mentor_response(
            user_message=user_message,
            resume_context=structured_resume,
            conversation_history=None
        )

        roadmap = []

        if isinstance(result, dict):

            roadmap = result.get(
                "roadmap",
                []
            )

            if not roadmap:
                roadmap = result.get(
                    "next_steps",
                    []
                )

        roadmap = safe_list(
            roadmap
        )

        normalized = []

        for index, step in enumerate(
            roadmap[:5],
            start=1
        ):

            if isinstance(step, dict):

                normalized.append({
                    "step": str(
                        step.get(
                            "step",
                            step.get(
                                "title",
                                f"Preparation Step {index}"
                            )
                        )
                    ),

                    "priority": str(
                        step.get(
                            "priority",
                            "Medium"
                        )
                    ),

                    "reason": str(
                        step.get(
                            "reason",
                            step.get(
                                "description",
                                ""
                            )
                        )
                    )
                })

            elif step:

                normalized.append({
                    "step": str(step),
                    "priority": "Medium",
                    "reason": ""
                })

        state["roadmap"] = normalized

        add_trace(
            state,
            "Roadmap Agent completed successfully"
        )

    except Exception as e:

        print(
            f"Roadmap Agent error: {e}"
        )

        state["roadmap"] = []

        add_trace(
            state,
            f"Roadmap Agent failed: {str(e)}"
        )

    return state


# ============================================================
# 4. RESOURCE AGENT
# ============================================================

def resource_agent(
    state: AgentState
) -> AgentState:

    print("Resource Agent running...")

    add_trace(
        state,
        "Resource Agent started"
    )

    missing_skills = (
        state.get("missing_skills") or []
    )

    roadmap = (
        state.get("roadmap") or []
    )

    resources = []

    # --------------------------------------------------------
    # BUILD SMALL TOPIC LIST
    # --------------------------------------------------------

    topics = []

    for skill in missing_skills[:5]:

        skill = str(
            skill
        ).strip()

        if skill and skill.lower() not in {
            x.lower()
            for x in topics
        }:

            topics.append(skill)

    # If no missing skills, use roadmap.
    if not topics:

        for item in roadmap[:3]:

            if isinstance(item, dict):

                topic = (
                    item.get("step")
                    or ""
                )

            else:

                topic = str(item)

            topic = str(
                topic
            ).strip()

            if topic and topic.lower() not in {
                x.lower()
                for x in topics
            }:

                topics.append(topic)

    topics = topics[:4]

    if not topics:

        state["resources"] = []

        add_trace(
            state,
            "Resource Agent found no topics"
        )

        return state

    # --------------------------------------------------------
    # IMPORTANT:
    # ONE RAG CALL instead of one call per skill.
    # --------------------------------------------------------

    topic_text = ", ".join(
        topics
    )

    question = f"""
Find the best learning resources for these topics:

{topic_text}

The resources are for a fresher preparing for a job interview.

Prioritize:
- practical learning
- interview preparation
- official documentation
- high-quality tutorials
- projects/practice

Return a small useful set of resources.

Do not return more than 10 resources.

Each resource should contain:
title
description
url
skill
"""

    try:

        result = generate_rag_response(
            question=question
        )

        if isinstance(result, dict):

            returned = safe_list(
                result.get(
                    "resources",
                    []
                )
            )

            for resource in returned:

                if isinstance(resource, dict):

                    item = dict(
                        resource
                    )

                    item["title"] = str(
                        item.get(
                            "title",
                            item.get(
                                "name",
                                "Learning Resource"
                            )
                        )
                    ).strip()

                    item["description"] = str(
                        item.get(
                            "description",
                            item.get(
                                "summary",
                                ""
                            )
                        )
                    ).strip()

                    item["url"] = (
                        item.get("url")
                        or item.get("link")
                    )

                    item["skill"] = str(
                        item.get(
                            "skill",
                            topics[0]
                        )
                    ).strip()

                    resources.append(
                        item
                    )

                elif resource:

                    resources.append({
                        "title": str(resource),
                        "description": "",
                        "url": None,
                        "skill": topics[0]
                    })

        # ----------------------------------------------------
        # If RAG returns nothing, provide topic fallback.
        # ----------------------------------------------------

        if not resources:

            for topic in topics:

                resources.append({
                    "title": f"{topic} learning resources",
                    "description": (
                        f"Use high-quality documentation, "
                        f"tutorials and hands-on practice for {topic}."
                    ),
                    "url": None,
                    "skill": topic
                })

    except Exception as e:

        print(
            f"Resource Agent RAG failed: {e}"
        )

        add_trace(
            state,
            f"Resource RAG failed: {str(e)}"
        )

        # Do not fail complete workflow.
        for topic in topics:

            resources.append({
                "title": f"{topic} preparation",
                "description": (
                    f"Prepare {topic} using official documentation "
                    f"and hands-on interview practice."
                ),
                "url": None,
                "skill": topic
            })

    # --------------------------------------------------------
    # DEDUPLICATE
    # --------------------------------------------------------

    unique = []
    seen = set()

    for resource in resources:

        if not isinstance(resource, dict):
            continue

        title = str(
            resource.get(
                "title",
                ""
            )
        ).lower().strip()

        url = str(
            resource.get(
                "url",
                ""
            )
        ).lower().strip()

        key = (
            f"url:{url}"
            if url
            else f"title:{title}"
        )

        if key in seen:
            continue

        seen.add(key)

        unique.append(
            resource
        )

    state["resources"] = unique[:10]

    add_trace(
        state,
        (
            "Resource Agent completed successfully "
            f"with {len(state['resources'])} resources "
            f"using 1 batched RAG call"
        )
    )

    print(
        "Resource Agent completed:",
        len(state["resources"]),
        "resources"
    )

    return state


# ============================================================
# 5. FINAL DECISION AGENT
# ============================================================

def final_decision_agent(
    state: AgentState
) -> AgentState:

    print("Final Decision Agent running...")

    add_trace(
        state,
        "Final Decision Agent started"
    )

    match_score = float(
        state.get("match_score") or 0
    )

    skill_match_score = float(
        state.get("skill_match_score") or 0
    )

    missing_skills = (
        state.get("missing_skills") or []
    )

    matched_skills = (
        state.get("matched_skills") or []
    )

    # ========================================================
    # DETERMINISTIC DECISION
    # ========================================================
    #
    # This is intentional.
    #
    # The previous version asked an LLM to make a tiny decision
    # while sending roadmap/resources as context.
    #
    # That caused:
    # - token waste
    # - JSON truncation
    # - Groq rate limits
    #
    # The actual decision logic is simple enough to be
    # deterministic.
    # ========================================================

    missing_count = len(
        missing_skills
    )

    if match_score >= 70:

        recommendation = "APPLY_NOW"

        reasoning = (
            f"The candidate has a strong overall match "
            f"of {match_score:.1f}%. "
            f"{len(matched_skills)} relevant skills are matched. "
            f"The candidate should apply while preparing "
            f"the remaining gaps."
        )

        prep_time = (
            "3-7 days"
            if missing_count <= 2
            else "1-2 weeks"
        )

    elif match_score >= 50:

        recommendation = "APPLY_NOW"

        reasoning = (
            f"The candidate has a moderate match "
            f"of {match_score:.1f}%. "
            f"The role is worth applying to while "
            f"preparing the identified skill gaps."
        )

        prep_time = "1-2 weeks"

    else:

        recommendation = "PREPARE_FIRST"

        reasoning = (
            f"The current match is {match_score:.1f}%. "
            f"Several job requirements appear to be missing "
            f"or weak, so focused preparation is recommended "
            f"before relying heavily on this role."
        )

        prep_time = "2-4 weeks"

    # ========================================================
    # SAVE DECISION
    # ========================================================

    state["recommendation"] = (
        recommendation
    )

    state["reasoning"] = (
        reasoning
    )

    state["estimated_prep_time"] = (
        prep_time
    )

    add_trace(
        state,
        (
            "Final Decision Agent completed successfully "
            f"with {recommendation}"
        )
    )

    print(
        "Final Decision:",
        recommendation
    )

    return state