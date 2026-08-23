import os
import shutil

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db

from backend.crud.resume import (
    create_resume,
    get_resume_by_id
)

from backend.crud.user import (
    get_user_by_email
)

from backend.utils.pdf_parser import (
    extract_text_from_pdf
)

from backend.services.resume_parser import (
    parse_resume
)

from backend.services.resume_extractor import (
    extract_resume
)

from backend.services.ats_analyzer import (
    analyze_ats
)

from backend.services.jd_matcher import (
    match_resume_with_jd
)

from backend.dependencies import (
    get_current_user
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


# ============================================================
# JD REQUEST SCHEMA
# ============================================================

class JDRequest(BaseModel):
    jd_text: str


# ============================================================
# UPLOAD RESUME
# ============================================================

@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:

        # Get logged-in user
        user = get_user_by_email(
            db,
            current_user["sub"]
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # Save uploaded PDF
        upload_folder = "uploads"

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        file_path = os.path.join(
            upload_folder,
            file.filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # PDF → Text
        text = extract_text_from_pdf(
            file_path
        )

        # Text → Sections
        sections = parse_resume(
            text
        )

        # Sections → Structured Data
        structured_data = extract_resume(
            text,
            sections
        )

        # Save Resume
        resume = create_resume(
            db=db,
            user_id=user.id,
            filename=file.filename,
            extracted_text=text
        )

        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume.id,
            "filename": file.filename,
            "structured_data": structured_data
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# GET RESUME
# ============================================================

@router.get("/{resume_id}")
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Get logged-in user
    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get resume
    resume = get_resume_by_id(
        db,
        resume_id
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # Ownership check
    if resume.user_id != user.id:

        raise HTTPException(
            status_code=403,
            detail="You are not authorized to view this resume"
        )

    # Parse resume again
    sections = parse_resume(
        resume.extracted_text
    )

    structured_data = extract_resume(
        resume.extracted_text,
        sections
    )

    return {
        "id": resume.id,
        "filename": resume.filename,
        "structured_data": structured_data
    }


# ============================================================
# ATS ANALYSIS
# ============================================================

@router.get("/{resume_id}/ats")
def analyze_resume_ats(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Get logged-in user
    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get resume
    resume = get_resume_by_id(
        db,
        resume_id
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # Ownership check
    if resume.user_id != user.id:

        raise HTTPException(
            status_code=403,
            detail="You are not authorized to analyze this resume"
        )

    # Parse resume
    sections = parse_resume(
        resume.extracted_text
    )

    structured_data = extract_resume(
        resume.extracted_text,
        sections
    )

    # ATS analysis
    ats_result = analyze_ats(
        resume.extracted_text,
        structured_data
    )

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "ats_analysis": ats_result
    }


# ============================================================
# JD MATCHING
# ============================================================

@router.post("/{resume_id}/match")
def match_resume(
    resume_id: int,
    jd: JDRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Get logged-in user
    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get resume
    resume = get_resume_by_id(
        db,
        resume_id
    )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    # Ownership check
    if resume.user_id != user.id:

        raise HTTPException(
            status_code=403,
            detail="You are not authorized to use this resume"
        )

    # Validate JD
    if not jd.jd_text.strip():

        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )

    # Parse resume
    sections = parse_resume(
        resume.extracted_text
    )

    structured_data = extract_resume(
        resume.extracted_text,
        sections
    )

    # Get resume skills
    resume_skills = structured_data.get(
        "skills_flat",
        []
    )

    # Resume ↔ JD matching
    result = match_resume_with_jd(
        resume_text=resume.extracted_text,
        jd_text=jd.jd_text,
        resume_skills=resume_skills,
        structured_data=structured_data
    )

    return {
        "resume_id": resume.id,
        "filename": resume.filename,
        "jd_match": result
    }