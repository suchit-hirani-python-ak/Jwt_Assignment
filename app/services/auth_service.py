from fastapi.security import OAuth2PasswordRequestForm
import jwt
from app.core.dependencies import get_current_user
from app.exception.error import BadRequest, Forbidden, NotFound, Unauthorized
from app.repositories.user_repository import UserRepository,User
from app.schemas.token import RefreshRequest
from app.schemas.user import  UserCreate
from fastapi import Depends,Response
from app.core.config import settings
from app.db.session import AsyncSession
from app.core.security import oauth2_scheme, redis_client, verify_password, generate_tokens,hash_password

# redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
class AuthService:
    def __init__(self,db:AsyncSession):
        self.repo = UserRepository(db)
        
    async def register(self, payload: UserCreate) -> User:
        if await self.repo.get_by_email(payload.email):
            raise BadRequest("user already exists")
            
        db_user = User(
            email=payload.email.lower(),
            hashed_password=hash_password(payload.password),
            role=payload.role or "user"
        )
        return await self.repo.create(db_user)


    async def login(self, payload: OAuth2PasswordRequestForm, response: Response):
        email = payload.username
        lockout_key = f"lockout:{email}"
        attempts_key = f"attempts:{email}"

        # 1. Check if user is currently locked out
        if await redis_client.exists(lockout_key):
            ttl = await redis_client.ttl(lockout_key)
            raise Forbidden(f"Account locked try again in {ttl//60} minutes")

        user = await self.repo.get_by_email(email)
        
        # 2. Verify Credentials
        if not user or not verify_password(payload.password, user.hashed_password):
            # --- FAILURE BLOCK ---
            failed_count = await redis_client.incr(attempts_key)
            
            if failed_count == 1:
                await redis_client.expire(attempts_key, 600) # 10 min window

            if failed_count >= 5:
                # Lock for 10 minutes
                await redis_client.setex(lockout_key, 600, "locked")
                await redis_client.delete(attempts_key)
                raise Forbidden("Too many attempts. Locked for 10 min.")
                
            raise Unauthorized(f"Invalid credentials. {5 - failed_count} attempts left.")

        # --- SUCCESS BLOCK ---
        # Delete the previous "session of error" (the counter) immediately
        await redis_client.delete(attempts_key)

        tokens = generate_tokens(user)
        await self.repo.update_token(user.id, tokens["refresh_token"])
        
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh_token"],
            httponly=True,
            secure=True, 
            samesite="lax",
            max_age=(settings.refresh_token_expire_days * 24 * 60 + 330) * 60
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
        # token = request.refresh_token.strip('"').replace('%22', '')
        payload = jwt.decode(token, settings.refresh_secret_key.get_secret_value(), algorithms=[settings.algorithm])
        
        
        if payload.get("type") != "refresh":
            raise Unauthorized("not authorized")

        email = payload.get("sub")
        if not email:
            raise Unauthorized()
        
        user = await self.repo.get_by_email(email)
        if not user:
            raise NotFound("user not found")
            
        return generate_tokens(user)