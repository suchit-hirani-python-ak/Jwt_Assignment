from pydantic import BaseModel, ConfigDict
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class TokenPayload(BaseModel):
    sub: str | None = None
    user_id: int
    role: str
    exp: int
    
    model_config = ConfigDict(from_attributes=True)