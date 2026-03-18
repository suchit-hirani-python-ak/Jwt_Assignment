from fastapi.responses import JSONResponse
from fastapi import FastAPI,Depends, Request
from app.core.security import oauth2_scheme
from app.db.base import Base
from app.db.session import engine
from contextlib import asynccontextmanager
from app.api import auth, users
from app.core import security
from app.exception.error import ComputationError


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
app.include_router(auth.router, prefix='/auth',tags=["Authentication"])
app.include_router(users.router, prefix='/users',tags=["users"])

@app.exception_handler(ComputationError)
async def error_handler(request:Request, exc: ComputationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail":exc.message}
    )

# Fix: Added a route decorator so this is reachable
@app.get("/")
def server():
    return {"status": "server is running"}
