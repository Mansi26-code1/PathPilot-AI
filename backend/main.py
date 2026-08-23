from fastapi import FastAPI
from backend.config import APP_NAME, APP_VERSION
from backend.database import engine, Base
from backend import models
from backend.routers.auth import router as auth_router
from backend.routers.user import router as user_router
from backend.routers.resume import router as resume_router
from backend.routers.mentor import router as mentor_router
from backend.routers.learning import router as learning_router
from backend.routers.agent import router as agent_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI Career Mentor Platform"
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(resume_router)
app.include_router(mentor_router)
app.include_router(learning_router)
app.include_router(agent_router)

@app.get("/")
def home():
    return {"message": "Welcome to PathPilot AI"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PathPilot AI Backend",
        "version": APP_VERSION
    }