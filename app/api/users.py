from typing import Annotated
from app.db.session import AsyncSession
from app.core.dependencies import allow_admin,oauth2_scheme
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()

@router.get("", response_model=list[UserResponse])
async def get_all_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    # This dependency ensures ONLY an admin reaches the code below
    admin: User = Depends(allow_admin) 
):
    # Pass the 'admin' object to the service
    return await AuthService(db).all_users(admin)

@router.get("/me",response_model=UserResponse)
async def user_me(db: Annotated[AsyncSession,Depends(get_db)],token: str= Depends(oauth2_scheme)):
    return await AuthService(db).current_user(token)