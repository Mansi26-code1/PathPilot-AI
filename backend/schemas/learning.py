from pydantic import BaseModel, Field
from datetime import datetime



class LearningResourceRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=2,
        max_length=500
    )


class LearningResource(BaseModel):
    title: str
    url: str | None = None
    skill: str | None = None
    level: str | None = None
    source: str | None = None
    description: str | None = None


class LearningResourceResponse(BaseModel):
    answer: str
    resources: list[LearningResource]
    source_type: str



class LearningHistoryItem(BaseModel):
    id: int
    question: str
    answer: str
    source_type: str
    created_at: datetime

    class Config:
        from_attributes = True    


class SaveLearningResourceRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    url: str = Field(..., min_length=5, max_length=1000)
    skill: str | None = None
    level: str | None = None
    description: str | None = None


class SavedLearningResourceResponse(BaseModel):
    id: int
    title: str
    url: str
    skill: str | None = None
    level: str | None = None
    description: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True      
