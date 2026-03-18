from typing import Annotated
import jwt 
from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from app.core.config import settings
from app.core.security import oauth2_scheme
from app.models.user import User
from app.schemas.token import TokenResponse


def get_current_user(token: str) -> TokenResponse:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
        token_data = TokenResponse(**payload)
        
            
        return token_data
    except (jwt.PyJWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions"
            )
        return user

# 2. Define reusable shortcuts
allow_admin = RoleChecker(["admin"])
allow_staff = RoleChecker(["admin", "user"])