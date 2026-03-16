from fastapi import FastAPI,Depends
from app.core.security import oauth2_scheme
from app.db.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager
from app.api import auth
from app.core import security


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Clean up on shutdown
    await engine.dispose()
    
app = FastAPI(title="JWT Assignment", lifespan=lifespan)

# Fix: include_router is a method, not a decorator
app.include_router(auth.router, prefix='/auth')
app.include_router(auth.router,prefix='/user')

# Fix: Added a route decorator so this is reachable
@app.get("/")
def server():
    return {"status": "server is running"}
