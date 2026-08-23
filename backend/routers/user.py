from fastapi import APIRouter, Depends

from backend.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def current_user(user=Depends(get_current_user)):
    return {
        "message": "Authorized User",
        "user": user
    }