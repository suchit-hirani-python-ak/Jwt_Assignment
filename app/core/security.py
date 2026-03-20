from datetime import timezone, datetime, timedelta
import jwt
from app.core import security
from app.core.config import settings
from pwdlib import PasswordHash

from fastapi.security import OAuth2PasswordBearer

from app.exception.error import AuthException
from app.models.user import User

# The tokenUrl is where the "Authorize" button will send the username/password
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") 

# This scheme handles the 72-byte limit by pre-hashing with SHA256
# No more 72-byte errors, ever.
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # Pre-hash to bypass the 72-byte bcrypt limit
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Apply the same pre-hash before verifying
    return password_hash.verify(plain_password, hashed_password)

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
    
def generate_tokens(user: User):
    # Call the function defined in the same file directly
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    if settings.access_token_expire_minutes > 30:
        raise AuthException("Token has expired")
    
    refresh_token = create_access_token(
        data={"sub": user.email, "type": "refresh"},
        expires_delta=timedelta(days=settings.refresh_token_expire_days)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
