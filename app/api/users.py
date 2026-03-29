from typing import Annotated
from app.db.session import AsyncSession
from app.core.dependencies import allow_admin, oauth2_scheme
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.get("", response_model=list[UserResponse])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    admin: Annotated[User, Depends(allow_admin)]
):
    """
    Retrieve all users (Admin only).

    Args:
        db (AsyncSession): Database session dependency.
        admin (User): Authenticated admin user (validated by allow_admin dependency).

    Returns:
        list[UserResponse]: List of all users in the system.
    """
    return await AuthService(db).all_users(admin)

@router.get("/me",response_model=UserResponse)
async def user_me(db: Annotated[AsyncSession,Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    """
    Retrieve details of the currently authenticated user.

    Args:
        db (AsyncSession): Database session dependency.
        token (str): JWT token extracted from request headers.

    Returns:
        UserResponse: Details of the logged-in user.
    """
    return await AuthService(db).current_user(token)