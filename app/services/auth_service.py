from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from pydantic import ValidationError
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.exception.error import ComputationError
from app.repositories.user_repository import UserRepository,User
from app.schemas.token import RefreshRequest
from app.schemas.user import  UserCreate, UserUpdate
from app.core import security
from app.core.security import generate_tokens, verify_password
from fastapi import Depends, HTTPException, Request, Response,status
from datetime import timedelta
from app.core import security
from app.core.config import settings
from app.db.session import AsyncSession
from app.core.security import oauth2_scheme

class AuthService:
    def __init__(self,db:AsyncSession):
        self.repo = UserRepository(db)
        
    async def register(self, payload: UserCreate) -> User:
        # You must await the async repo method
        if await self.repo.get_by_email(payload.email):
            raise ComputationError("User already exists",400)
            
        db_user = User(
            email=payload.email.lower(),
            hashed_password=security.hash_password(payload.password),
            role=payload.role or "user"
        )
        return await self.repo.create(db_user)


    async def login(self, payload: OAuth2PasswordRequestForm, response: Response):
    # 1. Verify User
        user = await self.repo.get_by_email(payload.username)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        
        
        # 3. Generate New Tokens
        tokens = generate_tokens(user)
        await self.repo.update_token(user.id,tokens["refresh_token"])
        # 4. Store the NEW Refresh Token
        

        # 5. Set Cookie
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
        # 1. Use your helper to decode the token into the Pydantic model
        payload = get_current_user(token) 
        
        # 2. Use the 'sub' (email) from the payload to query the database
        user = await self.repo.get_by_email(payload.sub)
        
        # 3. Handle case where token is valid but user was deleted from DB
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return user
    
    async def all_users(self,user:User)->list[User]:
        if user.role != "admin":
            ComputationError("only admin allowed to access",403)
        return await self.repo.list_all()


    async def refresh_token(self,request:RefreshRequest,token: str=Depends(oauth2_scheme)):
        token = request.refresh_token.strip('"').replace('%22', '')
        # 1. Decode specifically for refresh type
        payload = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algorithm])
        
        
        if payload.get("type") != "refresh":
            raise ConnectionError("not authorized",401)

        # 2. Fetch user and generate NEW tokens
        email = payload.get("sub")
        if not email:
            raise ConnectionError("invalid token",401)
        
        user = await self.repo.get_by_email(email)
        if not user:
            raise ConnectionError("user not found",404)
            
        return generate_tokens(user)