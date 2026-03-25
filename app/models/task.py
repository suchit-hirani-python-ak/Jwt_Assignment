from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey
import enum
from datetime import datetime,timezone,timedelta

class Status(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Task(Base):
    __tablename__ = "tasks"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_status: Mapped[Status] = mapped_column(String(10))
    description: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc)+timedelta(hours=5, minutes=30))
    email: Mapped[int] = mapped_column(ForeignKey("users.email"))
    
    user: Mapped["User"] = relationship("User",back_populates="tasks") # type: ignore