from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import get_current_user
from backend.crud.user import get_user_by_email

from backend.crud.learning import (
    get_learning_history,
    create_saved_learning_resource,
    get_saved_learning_resources
)

from backend.schemas.learning import (
    LearningResourceRequest,
    LearningResourceResponse,
    LearningHistoryItem,
    SaveLearningResourceRequest,
    SavedLearningResourceResponse
)

from backend.services.rag.chain import generate_rag_response
from backend.models import LearningHistory
router = APIRouter(
    prefix="/learning",
    tags=["Learning Hub"]
)
@router.post(
    "/resources",
    response_model=LearningResourceResponse
)
def get_learning_resources(
    request: LearningResourceRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # Generate RAG + web search response
    result = generate_rag_response(
        question=request.question
    )

    # Save learning interaction
    user = get_user_by_email(db, current_user["sub"])

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    history = LearningHistory(
        user_id=user.id,
        question=request.question,
        answer=result["answer"],
        source_type=result["source_type"]
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return result
@router.get(
    "/history",
    response_model=list[LearningHistoryItem]
)
def get_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user = get_user_by_email(db, current_user["sub"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return get_learning_history(db, user.id)
@router.post(
    "/saved",
    response_model=SavedLearningResourceResponse
)
def save_learning_resource(
    request: SaveLearningResourceRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    resource = create_saved_learning_resource(
        db=db,
        user_id=user.id,
        title=request.title,
        url=request.url,
        skill=request.skill,
        level=request.level,
        description=request.description
    )

    return resource
@router.get(
    "/saved",
    response_model=list[SavedLearningResourceResponse]
)
def get_saved_resources(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    user = get_user_by_email(
        db,
        current_user["sub"]
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return get_saved_learning_resources(
        db,
        user.id
    )