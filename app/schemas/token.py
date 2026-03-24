from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class TokenResponse(BaseModel):
    sub: str
    role: str
    exp: int
    
    model_config = ConfigDict(from_attributes=True)

class RefreshRequest(BaseModel):
    refresh_token:str