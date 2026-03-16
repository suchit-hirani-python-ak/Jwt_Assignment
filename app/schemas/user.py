from pydantic import EmailStr, BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str
    role: Optional[str] = "user"

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None

class UserResponse(UserBase):
    id: int
    role: str
    
    model_config = ConfigDict(from_attributes=True)