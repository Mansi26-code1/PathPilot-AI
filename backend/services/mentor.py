import json
from groq import Groq

from backend.config import (
    GROQ_API_KEY,
    GROQ_MODEL
)


client = Groq(api_key=GROQ_API_KEY)


# ============================================================
# MENTOR SYSTEM PROMPT
# ============================================================

MENTOR_SYSTEM_PROMPT = """
You are PathPilot AI, an evidence-based career mentor for
students, freshers and early-career professionals.

Your job is to give practical, honest and resume-grounded
career guidance.

GROUNDING:
- Never invent skills, projects, experience, education,
  certifications or technologies.
- Resume information is evidence only.
- Clearly distinguish EXISTING SKILLS, SKILL GAPS and
  RECOMMENDED SKILLS.
- Never convert a recommendation into an existing skill.
- Never convert an interest into experience.
- Never guarantee a job or salary.

CAREER:
Consider realistic paths such as:
Software Engineer, Backend Developer, Frontend Developer,
Full Stack Developer, Data Analyst, Data Scientist,
ML Engineer, AI Engineer, GenAI Engineer, MLOps,
Cloud/DevOps, QA/Automation and other suitable roles.

Do not automatically recommend AI Engineer.
Use the user's actual background and stated goal.

ROADMAP:
When the user asks for a roadmap, career transition plan,
preparation plan or assessment, provide 5-8 ordered steps.

Each roadmap item must contain:
{
  "step": "...",
  "reason": "...",
  "priority": "High/Medium/Low"
}

Start from the user's actual current level.

INTERVIEW PREPARATION:
Only include topics relevant to the recommended role.

CONVERSATION:
Use previous conversation only to maintain continuity.
Do not repeat questions already answered.

IMPORTANT:
If the user asks a simple conversational question,
give a useful answer in quick_answer and do not force a
complete career analysis.

If the user explicitly asks for a roadmap, assessment,
career recommendation or preparation plan, populate the
relevant structured fields.

Return ONLY valid JSON.
Use EXACTLY this structure:

{
  "quick_answer": "",
  "current_assessment": "",
  "career_recommendations": [],
  "strengths": [],
  "skill_gaps": [],
  "roadmap": [],
  "interview_preparation": [],
  "next_steps": [],
  "questions": []
}
"""


# ============================================================
# CONTEXT LIMITS
# ============================================================

# Keep request comfortably below Groq TPM limit.
MAX_HISTORY_MESSAGES = 2
MAX_HISTORY_MESSAGE_CHARS = 700
MAX_RESUME_CONTEXT_CHARS = 5000
MAX_USER_MESSAGE_CHARS = 2500


# ============================================================
# SAFE JSON
# ============================================================

def _safe_json_loads(content: str) -> dict:

    if not content:
        return {}

    try:
        result = json.loads(content)

        if isinstance(result, dict):
            return result

    except Exception:
        pass

    # Try extracting JSON object
    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1 and end > start:

        try:
            result = json.loads(
                content[start:end + 1]
            )

            if isinstance(result, dict):
                return result

        except Exception:
            pass

    return {}


# ============================================================
# NORMALIZE RESPONSE
# ============================================================

def _normalize_result(result: dict) -> dict:

    if not isinstance(result, dict):
        result = {}

    return {
        "quick_answer": str(
            result.get("quick_answer") or ""
        ),

        "current_assessment": str(
            result.get("current_assessment") or ""
        ),

        "career_recommendations": (
            result.get("career_recommendations")
            if isinstance(
                result.get("career_recommendations"),
                list
            )
            else []
        ),

        "strengths": (
            result.get("strengths")
            if isinstance(
                result.get("strengths"),
                list
            )
            else []
        ),

        "skill_gaps": (
            result.get("skill_gaps")
            if isinstance(
                result.get("skill_gaps"),
                list
            )
            else []
        ),

        "roadmap": (
            result.get("roadmap")
            if isinstance(
                result.get("roadmap"),
                list
            )
            else []
        ),

        "interview_preparation": (
            result.get("interview_preparation")
            if isinstance(
                result.get("interview_preparation"),
                list
            )
            else []
        ),

        "next_steps": (
            result.get("next_steps")
            if isinstance(
                result.get("next_steps"),
                list
            )
            else []
        ),

        "questions": (
            result.get("questions")
            if isinstance(
                result.get("questions"),
                list
            )
            else []
        )
    }


# ============================================================
# RESUME COMPACTION
# ============================================================

def _compact_resume(resume_context: dict | None) -> str:

    if not resume_context:
        return "No resume provided."

    compact = {
        "name": resume_context.get("name"),
        "education": resume_context.get(
            "education",
            []
        )[:3],

        "skills": resume_context.get(
            "skills",
            []
        )[:30],

        "experience": resume_context.get(
            "experience",
            []
        )[:6],

        "projects": resume_context.get(
            "projects",
            []
        )[:6],

        "achievements": resume_context.get(
            "achievements",
            []
        )[:5]
    }

    text = json.dumps(
        compact,
        ensure_ascii=False
    )

    return text[:MAX_RESUME_CONTEXT_CHARS]


# ============================================================
# MAIN MENTOR FUNCTION
# ============================================================

def generate_mentor_response(
    user_message: str,
    resume_context: dict | None = None,
    conversation_history: list | None = None
):

    user_message = (
        user_message or ""
    ).strip()

    if not user_message:

        return _normalize_result({
            "quick_answer": "Please ask me a career or interview question."
        })

    user_message = user_message[
        :MAX_USER_MESSAGE_CHARS
    ]

    resume_text = _compact_resume(
        resume_context
    )

    messages = [
        {
            "role": "system",
            "content": MENTOR_SYSTEM_PROMPT
        }
    ]

    # --------------------------------------------------------
    # SMALL CONVERSATION HISTORY
    # --------------------------------------------------------

    if conversation_history:

        history = conversation_history[
            -MAX_HISTORY_MESSAGES:
        ]

        for turn in history:

            if not isinstance(turn, dict):
                continue

            role = turn.get("role")
            content = turn.get("content")

            if role not in (
                "user",
                "assistant"
            ):
                continue

            if not content:
                continue

            content = str(content)

            # IMPORTANT:
            # Previous assistant JSON can become huge.
            # Keep only a small portion.
            content = content[
                :MAX_HISTORY_MESSAGE_CHARS
            ]

            messages.append({
                "role": role,
                "content": content
            })

    # --------------------------------------------------------
    # CURRENT REQUEST
    # --------------------------------------------------------

    current_prompt = f"""
USER PROFILE:

{resume_text}

USER QUESTION:

{user_message}

INSTRUCTIONS:

Answer the user's question directly.

If they ask for a roadmap, provide an actual ordered roadmap,
not only a list of things they "need to learn".

If they ask what they need to learn, clearly state:

1. What they already know.
2. What is missing.
3. What to learn first.
4. What to learn next.
5. How to practice it.
6. What interview preparation is required.

If the user asks about a role that is unrelated to their
resume, explain the gap honestly.

If the question is simple, keep the answer concise.
"""

    messages.append({
        "role": "user",
        "content": current_prompt
    })

    # --------------------------------------------------------
    # GROQ CALL
    # --------------------------------------------------------

    try:

        response = client.chat.completions.create(
            model=GROQ_MODEL,

            messages=messages,

            temperature=0.2,

            max_tokens=1100,

            response_format={
                "type": "json_object"
            }
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        result = _safe_json_loads(
            content
        )

        # ----------------------------------------------------
        # FALLBACK IF JSON FAILS
        # ----------------------------------------------------

        if not result:

            return _normalize_result({
                "quick_answer":
                    "I couldn't generate the structured mentor response. "
                    "Please try the question again."
            })

        return _normalize_result(
            result
        )

    except Exception as e:

        print(
            f"Mentor generation failed: {e}"
        )

        # Do NOT hide the actual error from backend logs,
        # but return a usable response to frontend.
        return _normalize_result({
            "quick_answer":
                "Mentor is temporarily unavailable. "
                "Please try again in a moment."
        })