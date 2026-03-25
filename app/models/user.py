from typing import List
from pydantic import EmailStr
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user")
    
    tokens: Mapped[List["TokenGeneration"]] = relationship("TokenGeneration", back_populates="user") # type: ignore
    tasks: Mapped[List["Task"]] = relationship("Task",back_populates="user") # type: ignore