from sqlalchemy.orm import Session
from backend.models import Conversation


def create_conversation_message(
    db: Session,
    user_id: int,
    role: str,
    message: str
):
    conversation = Conversation(
        user_id=user_id,
        role=role,
        message=message
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation_history(
    db: Session,
    user_id: int,
    limit: int = 20
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.asc())
        .limit(limit)
        .all()
    )