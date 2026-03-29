from app.core.config import settings
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from app.models.user import User
from app.schemas.token import RefreshRequest, Token, TokenResponse
from app.db.session import AsyncSession, get_db
from app.schemas.user import UserBase, UserCreate, UserResponse, UserUpdate
from app.repositories.user_repository import UserRepository # Added
from app.services.auth_service import AuthService
from app.core.dependencies import allow_admin
from typing import Annotated
from app.core.security import generate_tokens, oauth2_scheme

router = APIRouter()

# Use Annotated with Depends for modern dependency injection
@router.post("/register",response_model=UserResponse)
async def create_user(payload:UserCreate,db: Annotated[AsyncSession,Depends(get_db)]):
    """
    Register a new user.

    Args:
        payload (UserCreate): User registration details such as email, password, etc.
        db (AsyncSession): Database session dependency.

    Returns:
        UserResponse: Details of the newly created user.
    """
    return await AuthService(db).register(payload)

@router.post("/login", response_model=Token)
async def login(
    response:Response,
    payload: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Authenticate user and generate JWT tokens.

    Args:
        response (Response): FastAPI response object used to set cookies.
        payload (OAuth2PasswordRequestForm): Form data containing username and password.
        db (AsyncSession): Database session dependency.

    Returns:
        Token: Access and refresh tokens.
    """
    return await AuthService(db).login(payload,response)



@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Generate a new access token using a refresh token.

    Args:
        request (RefreshRequest): Contains refresh token.
        db (AsyncSession): Database session.

    Returns:
        Token: New access and refresh tokens.
    """
    return await AuthService(db).refresh_token(request)


