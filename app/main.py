from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    
app = FastAPI(lifespan=lifespan)

@app.get("/")
def server():
    return "server is running..."

    
           