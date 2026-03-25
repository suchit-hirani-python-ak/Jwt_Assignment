from datetime import timezone, datetime, timedelta
import jwt
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
import redis.asyncio as redis
from app.core.config import settings
from app.models.user import User


redis_client = redis.from_url("redis://redis:6379", decode_responses=True)

# The tokenUrl is where the "Authorize" button will send the username/password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 

# This scheme handles the 72-byte limit by pre-hashing with SHA256
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    # Pre-hash to bypass the 72-byte bcrypt limit
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Apply the same pre-hash before verifying
    return password_hash.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire, "type": "access"})
    
    return jwt.encode(
        payload=to_encode,
        key=settings.access_secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )

def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.refresh_token_expire_days))
    to_encode.update({"exp": expire, "type": "refresh"})
    
    return jwt.encode(
        payload=to_encode,
        key=settings.refresh_secret_key.get_secret_value(), # Use Refresh Secret
        algorithm=settings.algorithm
    )

def generate_tokens(user: User):
    access_token = create_access_token(
        data={"sub": str(user.email), "role": user.role}
        
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.email)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
