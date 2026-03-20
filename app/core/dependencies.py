import jwt 
from fastapi import Depends
from app.core.config import settings
from app.core.security import oauth2_scheme
from app.exception.error import Forbidden, Unauthorized
from app.models.user import User
from app.schemas.token import TokenResponse


def get_current_user(token: str=Depends(oauth2_scheme)) -> TokenResponse:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
        token_data = TokenResponse(**payload)
        
            
        return token_data
    except:
        raise Unauthorized("Could not validate cradentials")


class RoleChecker:
    def __init__(self, allowed_roles: str):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise Forbidden()
        return user

allow_admin = RoleChecker("admin")