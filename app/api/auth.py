from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.token import Token
from app.db.session import AsyncSession, get_db
from app.schemas.user import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository # Added
from app.services.auth_service import AuthService
from typing import Annotated
from app.core.security import oauth2_scheme

router = APIRouter()

# Use Annotated with Depends for modern dependency injection
DBDependency = Annotated[AsyncSession, Depends(get_db)]

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: DBDependency):
    # Dependency Inversion: Router -> Repo -> Service
    repo = UserRepository(db)
    service = AuthService(repo)
    return await service.register(payload)

@router.post("/login", response_model=Token) # Use your Token pydantic model
async def login(
    db: DBDependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    repo = UserRepository(db)
    service = AuthService(repo)
    
    # Map 'username' from the form to 'email' in your service
    return await service.login(
        email=form_data.username, 
        password=form_data.password
    )



@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[str, Depends(oauth2_scheme)], # This adds the Lock icon
    db: DBDependency
):
    repo = UserRepository(db)
    # logic to fetch user by current_user (which is the 'sub' from the token)
    return await repo.get_by_email(current_user)