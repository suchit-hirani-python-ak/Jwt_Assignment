from fastapi.security import OAuth2PasswordRequestForm
import jwt
from app.core.dependencies import get_current_user
from app.exception.error import BadRequest, Forbidden, NotFound, Unauthorized
from app.repositories.user_repository import UserRepository,User
from app.schemas.token import RefreshRequest
from app.schemas.user import  UserCreate
from app.core import security
from app.core.security import generate_tokens, verify_password
from fastapi import Depends,Response
from app.core import security
from app.core.config import settings
from app.db.session import AsyncSession
from app.core.security import oauth2_scheme

class AuthService:
    def __init__(self,db:AsyncSession):
        self.repo = UserRepository(db)
        
    async def register(self, payload: UserCreate) -> User:
        if await self.repo.get_by_email(payload.email):
            raise BadRequest("user already exists")
            
        db_user = User(
            email=payload.email.lower(),
            hashed_password=security.hash_password(payload.password),
            role=payload.role or "user"
        )
        return await self.repo.create(db_user)


    async def login(self, payload: OAuth2PasswordRequestForm, response: Response):
        user = await self.repo.get_by_email(payload.username)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise Unauthorized()
        
        
        
        tokens = generate_tokens(user)
        await self.repo.update_token(user.id,tokens["refresh_token"])
        
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True, 
            samesite="lax",
            max_age=settings.refresh_token_expire_days
        )
        
        return tokens



    
    async def current_user(self, token: str) -> User:
        payload = get_current_user(token) 
        
        user = await self.repo.get_by_email(payload.sub)
        
        if not user:
            raise NotFound("User not found")
            
        return user
    
    async def all_users(self,user:User)->list[User]:
        if user.role != "admin":
            raise Forbidden()
        return await self.repo.list_all()


    async def refresh_token(self,request:RefreshRequest,token: str=Depends(oauth2_scheme)):
        token = request.refresh_token.strip('"').replace('%22', '')
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
        
        
        if payload.get("type") != "refresh":
            raise Unauthorized("not authorized")

        email = payload.get("sub")
        if not email:
            raise Unauthorized()
        
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFound("user not found")
            
        return generate_tokens(user)