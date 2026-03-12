import jwt 
from fastapi import HTTPException, status
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.token import TokenPayload

def decode_token(token: str)-> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm]
        )
        return TokenPayload(**payload)
    except (jwt.PyJWTError,ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"}
        )