import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user

from backend.crud.user import get_user_by_email
from backend.crud.resume import get_resume_by_id

from backend.crud.conversation import (
    create_conversation_message,
    get_conversation_history
)

from backend.services.resume_parser import parse_resume
from backend.services.resume_extractor import extract_resume
from backend.services.mentor import generate_mentor_response


router = APIRouter(
    prefix="/mentor",
    tags=["Mentor"]
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class MentorRequest(BaseModel):

    message: str


# ============================================================
# HELPER
# ============================================================

def build_resume_context(resume):
    """
    Convert extracted resume information into a small,
    clean context object for the AI mentor.
    """

    sections = parse_resume(
        resume.extracted_text
    )

    structured_data = extract_resume(
        resume.extracted_text,
        sections
    )

    resume_context = {

        "name": structured_data.get(
            "name"
        ),

        "education": structured_data.get(
            "education",
            []
        ),

        "skills": structured_data.get(
            "skills_flat",
            []
        ),

        "experience": structured_data.get(
            "experience",
            []
        ),

        "projects": structured_data.get(
            "projects",
            []
        ),

        "achievements": structured_data.get(
            "achievements",
            []
        )
    }

    return resume_context


# ============================================================
# RESUME-AWARE MENTOR
# ============================================================

@router.post("/{resume_id}")
def resume_aware_mentor(

    resume_id: int,

    request: MentorRequest,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)
):

    # --------------------------------------------------------
    # 1. Get logged-in user
    # --------------------------------------------------------

    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # 2. Get resume
    # --------------------------------------------------------

    resume = get_resume_by_id(
        db,
        resume_id
    )

    if not resume:

        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # --------------------------------------------------------
    # 3. Ownership check
    # --------------------------------------------------------

    if resume.user_id != user.id:

        raise HTTPException(
            status_code=403,
            detail="You are not authorized to use this resume"
        )

    # --------------------------------------------------------
    # 4. Build resume context
    # --------------------------------------------------------

    try:

        resume_context = build_resume_context(
            resume
        )

    except Exception as e:

        print(
            "Resume context extraction failed:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process resume information"
        )

    # --------------------------------------------------------
    # 5. Conversation history
    # --------------------------------------------------------

    history = get_conversation_history(
        db=db,
        user_id=user.id
    )

    conversation_history = [

        {
            "role": message.role,
            "content": message.message
        }

        for message in history

        if message.role in (
            "user",
            "assistant"
        )
    ]

    # --------------------------------------------------------
    # 6. Save user message
    # --------------------------------------------------------

    create_conversation_message(

        db=db,

        user_id=user.id,

        role="user",

        message=request.message
    )

    # --------------------------------------------------------
    # 7. Generate mentor response
    # --------------------------------------------------------

    try:

        result = generate_mentor_response(

            user_message=request.message,

            resume_context=resume_context,

            conversation_history=conversation_history
        )

    except Exception as e:

        print(
            "Mentor generation failed:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate mentor response"
        )

    # --------------------------------------------------------
    # 8. Save AI response
    # --------------------------------------------------------

    create_conversation_message(

        db=db,

        user_id=user.id,

        role="assistant",

        message=json.dumps(
            result,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # 9. Return
    # --------------------------------------------------------

    return {

        "resume_id": resume.id,

        "filename": resume.filename,

        "mentor_response": result

    }


# ============================================================
# GENERAL / NO-RESUME MENTOR
# ============================================================

@router.post("")
def general_mentor(

    request: MentorRequest,

    db: Session = Depends(get_db),

    current_user=Depends(get_current_user)
):

    # --------------------------------------------------------
    # 1. Get user
    # --------------------------------------------------------

    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # --------------------------------------------------------
    # 2. Conversation history
    # --------------------------------------------------------

    history = get_conversation_history(
        db=db,
        user_id=user.id
    )

    conversation_history = [

        {
            "role": message.role,
            "content": message.message
        }

        for message in history

        if message.role in (
            "user",
            "assistant"
        )
    ]

    # --------------------------------------------------------
    # 3. Save user message
    # --------------------------------------------------------

    create_conversation_message(

        db=db,

        user_id=user.id,

        role="user",

        message=request.message
    )

    # --------------------------------------------------------
    # 4. Generate response without resume
    # --------------------------------------------------------

    try:

        result = generate_mentor_response(

            user_message=request.message,

            resume_context=None,

            conversation_history=conversation_history
        )

    except Exception as e:

        print(
            "General mentor generation failed:",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate mentor response"
        )

    # --------------------------------------------------------
    # 5. Save assistant response
    # --------------------------------------------------------

    create_conversation_message(

        db=db,

        user_id=user.id,

        role="assistant",

        message=json.dumps(
            result,
            ensure_ascii=False
        )
    )

    # --------------------------------------------------------
    # 6. Return
    # --------------------------------------------------------

    return {

        "resume_id": None,

        "filename": None,

        "mentor_response": result

    }