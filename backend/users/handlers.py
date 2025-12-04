"""User API handlers"""
from fastapi import APIRouter, HTTPException, status, Depends

from users.models import UserCreate
from users.service import UserService
from common.exceptions import ValidationError, DuplicateError


router = APIRouter(prefix="/users", tags=["users"])


def get_user_service() -> UserService:
    """Dependency injection for UserService"""
    from config import get_user_service
    return get_user_service()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, service: UserService = Depends(get_user_service)):
    """Create a new user"""
    try:
        created_user = service.create_user(user.userId, user.name)
        return {
            "userId": created_user.user_id,
            "name": created_user.name
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get("/{user_id}")
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    """Get a user by ID"""
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return {
        "userId": user.user_id,
        "name": user.name
    }
