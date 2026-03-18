from datetime import datetime, timezone, timedelta
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class TokenGeneration(Base):
    __tablename__ = "tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String, unique=True, index=True)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    expire_at: Mapped[datetime] = mapped_column(DateTime,insert_default= lambda: datetime.now(timezone.utc)+timedelta(days=7,hours=5,minutes=30))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Use a STRING "User" instead of importing the class
    user: Mapped["User"] = relationship("User", back_populates="tokens")
