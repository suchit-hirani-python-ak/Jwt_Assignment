from app.repositories.user_repository import UserRepository,User
from app.schemas.user import UserCreate
from app.core.dependencies import decode_token
from app.core import security
from fastapi import HTTPException
from datetime import timedelta
from app.core import security
from app.core.config import settings

class AuthService:
    def __init__(self,db:UserRepository):
        self.repo = db
        
    async def register(self, payload:UserCreate) -> User:
        if await self.repo.get_by_email(payload.email):
            raise HTTPException(status_code=400, detail="User already exists")
        
        db_user = User(
            email = payload.email,
            hashed_password = security.hash_password(payload.password),
            role = payload.role or "user"
        )
        return await self.repo.create(db_user) 
    
    async def login(self, email: str, password: str):
        """Logic for User Login & JWT generation."""
        user = await self.repo.get_by_email(email)
        if not user or not security.verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return self._generate_tokens(user)

    def _generate_tokens(self, user: User):
        """Helper to create Access (short) and Refresh (long) tokens."""
        # 1. Access Token (with user_id and role for IDOR/RBAC)
        access_delta = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = security.create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role},
            expires_delta=access_delta
        )
        
        # 2. Refresh Token (Longer lived, e.g., 7 days)
        refresh_token = security.create_access_token(
            data={"sub": user.email, "type": "refresh"},
            expires_delta=timedelta(days=7)
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }