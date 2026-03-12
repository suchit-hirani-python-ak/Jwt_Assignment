from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config  import settings

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(
    DATABASE_URL,
    connect_args = {"check_same_thread":False}
)

AsyncSessionalLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

async def get_db():
    db: AsyncSession = AsyncSessionalLocal()
    try:
        yield db 
    finally:
        db.close()