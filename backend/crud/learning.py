from sqlalchemy.orm import Session
from backend.models import LearningHistory
from backend.models import LearningHistory, LearningResourceSaved


def get_learning_history(db: Session, user_id: int):
    return (
        db.query(LearningHistory)
        .filter(LearningHistory.user_id == user_id)
        .order_by(LearningHistory.created_at.desc())
        .all()
    )



def create_saved_learning_resource(
    db: Session,
    user_id: int,
    title: str,
    url: str,
    skill: str | None = None,
    level: str | None = None,
    description: str | None = None
):
    resource = LearningResourceSaved(
        user_id=user_id,
        title=title,
        url=url,
        skill=skill,
        level=level,
        description=description
    )

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return resource


def get_saved_learning_resources(
    db: Session,
    user_id: int
):
    return (
        db.query(LearningResourceSaved)
        .filter(
            LearningResourceSaved.user_id == user_id
        )
        .order_by(
            LearningResourceSaved.created_at.desc()
        )
        .all()
    )