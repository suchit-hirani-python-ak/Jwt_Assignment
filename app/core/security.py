from datetime import timezone, datetime, timedelta
import jwt
from pydantic import ValidationError
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from app.core.config import settings
import hashlib

from fastapi.security import OAuth2PasswordBearer

# The tokenUrl is where the "Authorize" button will send the username/password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 

# This scheme handles the 72-byte limit by pre-hashing with SHA256
# No more 72-byte errors, ever.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    # Pre-hash to bypass the 72-byte bcrypt limit
    pwd_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(pwd_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Apply the same pre-hash before verifying
    pwd_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(pwd_hash, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    # Use .get_secret_value() to access the actual string from Pydantic SecretStr
    return jwt.encode(
        to_encode,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm
    )

def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
        return payload
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
